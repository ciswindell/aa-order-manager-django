"""Abstract workflow strategy (Pattern B: report-centric, grouped structure)."""

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from orders.services.workflow.strategies.base import WorkflowStrategy
from orders.services.workflow.utils import format_report_description_html

if TYPE_CHECKING:
    from orders.models import Order, Report
    from orders.services.workflow.config import ProductConfig

    from integrations.basecamp.basecamp_service import BasecampService

logger = logging.getLogger(__name__)

# Workflow groups in order (5 departments)
WORKFLOW_GROUPS = [
    "Setup",
    "Workup",
    "Imaging",
    "Indexing",
    "Assembly",
]

# Workflow steps by group
# {lease_number} placeholder will be replaced with actual lease numbers for lease-specific steps
WORKFLOW_STEPS = {
    "Setup": [
        "Setup Abstract Todos",
        "Verify Lease Files",
    ],
    "Workup": [
        "Workup",
        "Microfilm SRP",
    ],
    "Imaging": [
        "Unfiled Documents {lease_number}",  # Lease-specific
        "Image {lease_number}",  # Lease-specific
    ],
    "Indexing": [
        "File Index {lease_number}",  # Lease-specific
        "Create Abstract Worksheet {lease_number}",  # Lease-specific
        "Review Abstract Worksheet {lease_number}",  # Lease-specific
    ],
    "Assembly": [
        "Assemble Abstract",
        "Review Abstract",
    ],
}


class AbstractWorkflowStrategy(WorkflowStrategy):
    """Strategy for creating report-centric, grouped abstract workflows."""

    def create_workflow(
        self,
        order: "Order",
        reports: list["Report"],
        product_config: "ProductConfig",
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> dict:
        """
        Create abstract workflow for given reports.

        Pattern B Logic:
        1. Create 1 to-do list per report (not per order)
        2. Create 5 groups within each list (Setup → Assembly)
        3. Create workflow steps within groups, duplicating lease-specific steps

        Args:
            order: Parent order
            reports: Filtered reports (abstract types, matching agency)
            product_config: Configuration (project_id, agency, name)
            basecamp_service: Basecamp API client
            account_id: Basecamp account ID

        Returns:
            dict with {"todolist_ids": [int], "todo_count": int}

        Raises:
            ValueError: Missing project ID
            HTTPError: Basecamp API failure
        """
        # Get project ID
        project_id = self._get_project_id(product_config)

        if not reports:
            logger.info(
                "No reports found for abstract workflow | order_id=%s | agency=%s",
                order.id,
                product_config.agency,
            )
            return {"todolist_ids": [], "todo_count": 0}

        # Process each report independently (Pattern B)
        todolist_ids = []
        total_todos = 0

        for report in reports:
            # Extract abstract type for naming
            abstract_type = self._extract_abstract_type(report.report_type)

            # Create to-do list for this report
            todolist_id = self._create_todolist(
                order=order,
                report=report,
                abstract_type=abstract_type,
                product_config=product_config,
                project_id=project_id,
                basecamp_service=basecamp_service,
                account_id=account_id,
            )
            todolist_ids.append(todolist_id)

            # Create groups and steps interleaved (create group, then its tasks immediately)
            todo_count = self._create_groups_and_steps(
                order=order,
                report=report,
                todolist_id=todolist_id,
                product_config=product_config,
                project_id=project_id,
                basecamp_service=basecamp_service,
                account_id=account_id,
            )
            total_todos += todo_count

            logger.info(
                "Abstract workflow created | order_id=%s | report_id=%s | product=%s | groups=%d | todos=%d",
                order.id,
                report.id,
                product_config.name,
                len(WORKFLOW_GROUPS),
                todo_count,
            )

        return {"todolist_ids": todolist_ids, "todo_count": total_todos}

    def _get_project_id(self, product_config: "ProductConfig") -> str:
        """
        Load Basecamp project ID from Django settings.

        Args:
            product_config: Configuration with project_id_env_var

        Returns:
            Project ID as string

        Raises:
            ValueError: If project ID not configured
        """
        project_id = getattr(settings, product_config.project_id_env_var, None)
        if not project_id:
            raise ValueError(
                f"Missing project ID configuration for {product_config.name}. "
                f"Set {product_config.project_id_env_var} in environment variables."
            )
        return str(project_id)

    def _extract_abstract_type(self, report_type: str) -> str:
        """
        Extract human-readable abstract type from report_type enum.

        Args:
            report_type: Report type enum value

        Returns:
            "Base", "Supplemental", or "DOL"
        """
        type_map = {
            "BASE_ABSTRACT": "Base",
            "SUPPLEMENTAL_ABSTRACT": "Supplemental",
            "DOL_ABSTRACT": "DOL",
        }
        return type_map.get(report_type, "Base")

    def _create_todolist(
        self,
        order: "Order",
        report: "Report",
        abstract_type: str,
        product_config: "ProductConfig",
        project_id: str,
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> str:
        """
        Create to-do list for a single report in Basecamp.

        Args:
            order: Order object
            report: Report object
            abstract_type: "Base", "Supplemental", or "DOL"
            product_config: Product configuration
            project_id: Basecamp project ID
            basecamp_service: Basecamp API client
            account_id: Basecamp account ID

        Returns:
            To-do list ID as string

        Raises:
            HTTPError: Basecamp API failure
        """
        # Format: "Order {number}- {type} Abstract {report_id} - {YYYYMMDD}"
        todolist_name = (
            f"Order {order.order_number}- {abstract_type} Abstract "
            f"{report.id} - {order.order_date.strftime('%Y%m%d')}"
        )

        # Truncate if needed (Basecamp limit)
        if len(todolist_name) > 255:
            todolist_name = todolist_name[:252] + "..."

        # Build HTML description
        description = self._build_description(order, report, product_config)

        # Create to-do list via BasecampService
        result = basecamp_service.create_todolist(
            account_id=account_id,
            project_id=project_id,
            name=todolist_name,
            description=description,
        )

        return str(result["id"])

    def _build_description(
        self, order: "Order", report: "Report", product_config: "ProductConfig"
    ) -> str:
        """
        Build HTML description for abstract to-do list.

        Includes: report type, date range, lease numbers, legal description, delivery link

        Args:
            order: Order object
            report: Report object
            product_config: Product configuration

        Returns:
            HTML formatted description
        """
        html_parts = []

        # Report information
        html_parts.append(f"<strong>Report Type:</strong> {report.report_type}<br>")

        # Date range (using format_report_description_html for consistency)
        formatted_desc = format_report_description_html(report)
        html_parts.append(f"<strong>Legal Description:</strong> {formatted_desc}<br>")

        # Lease numbers
        leases = report.leases.filter(agency=product_config.agency)
        if leases.exists():
            lease_numbers = [
                lease.lease_number for lease in leases if lease.lease_number
            ]
            if lease_numbers:
                html_parts.append(
                    f"<strong>Leases:</strong> {', '.join(lease_numbers)}<br>"
                )

        # Delivery link
        if order.delivery_link:
            html_parts.append(
                f'<strong>Delivery:</strong> <a href="{order.delivery_link}">{order.delivery_link}</a>'
            )

        return "".join(html_parts)

    def _create_groups_and_steps(
        self,
        order: "Order",
        report: "Report",
        todolist_id: str,
        product_config: "ProductConfig",
        project_id: str,
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> int:
        """
        Create groups and steps interleaved (create group, then immediately create its tasks).

        This approach creates each group and immediately populates it with tasks before
        moving to the next group, which works better with Basecamp's API.

        Args:
            order: Order object
            report: Report object
            todolist_id: To-do list ID
            product_config: Product configuration
            project_id: Basecamp project ID
            basecamp_service: Basecamp API client
            account_id: Basecamp account ID

        Returns:
            Total number of to-dos created

        Raises:
            HTTPError: Basecamp API failure
        """
        # Get leases for this report
        leases = list(report.leases.filter(agency=product_config.agency))
        lease_numbers = [lease.lease_number for lease in leases if lease.lease_number]

        todo_count = 0

        # Create each group and immediately create its steps
        for group_name in WORKFLOW_GROUPS:
            # Create the group
            result = basecamp_service.create_group(
                account_id=account_id,
                project_id=project_id,
                todolist_id=todolist_id,
                name=group_name,
            )
            group_id = int(result["id"])

            logger.debug(
                "Created abstract workflow group | todolist_id=%s | group=%s | group_id=%s",
                todolist_id,
                group_name,
                group_id,
            )

            # Immediately create steps for this group
            steps = WORKFLOW_STEPS[group_name]

            for step_template in steps:
                # Check if this is a lease-specific step (contains {lease_number})
                if "{lease_number}" in step_template:
                    # Create one step per lease
                    if lease_numbers:
                        for lease_number in lease_numbers:
                            step_name = step_template.replace(
                                "{lease_number}", lease_number
                            )
                            self._create_todo(
                                step_name=step_name,
                                todolist_id=group_id,  # Groups are todolists in Basecamp
                                project_id=project_id,
                                basecamp_service=basecamp_service,
                                account_id=account_id,
                            )
                            todo_count += 1
                    else:
                        # No leases, create step without substitution
                        step_name = step_template.replace(
                            "{lease_number}", "[No Lease]"
                        )
                        self._create_todo(
                            step_name=step_name,
                            todolist_id=group_id,  # Groups are todolists in Basecamp
                            project_id=project_id,
                            basecamp_service=basecamp_service,
                            account_id=account_id,
                        )
                        todo_count += 1
                else:
                    # Fixed step (not lease-specific)
                    self._create_todo(
                        step_name=step_template,
                        todolist_id=group_id,  # Groups are todolists in Basecamp
                        project_id=project_id,
                        basecamp_service=basecamp_service,
                        account_id=account_id,
                    )
                    todo_count += 1

        return todo_count

    def _create_todo(
        self,
        step_name: str,
        todolist_id: int,
        project_id: str,
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> None:
        """
        Create a single to-do item within a group.

        Args:
            step_name: Name of the workflow step
            todolist_id: Group's to-do list ID (groups are todolists in Basecamp)
            project_id: Basecamp project ID
            basecamp_service: Basecamp API client
            account_id: Basecamp account ID

        Raises:
            HTTPError: Basecamp API failure
        """
        # Truncate if needed
        if len(step_name) > 255:
            step_name = step_name[:252] + "..."

        # Create to-do in the group (groups are todolists in Basecamp)
        basecamp_service.create_todo(
            account_id=account_id,
            project_id=project_id,
            todolist_id=str(todolist_id),
            content=step_name,
            description="",
        )

        logger.debug(
            "Created abstract workflow step | todolist_id=%s | step=%s",
            todolist_id,
            step_name,
        )
