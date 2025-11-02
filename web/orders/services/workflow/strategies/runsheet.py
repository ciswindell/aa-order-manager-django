"""Runsheet workflow strategy (Pattern A: lease-centric, flat structure)."""

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


class RunsheetWorkflowStrategy(WorkflowStrategy):
    """Strategy for creating lease-centric, flat runsheet workflows."""

    def create_workflow(
        self,
        order: "Order",
        reports: list["Report"],
        product_config: "ProductConfig",
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> dict:
        """
        Create runsheet workflow for given reports.

        Pattern A Logic:
        1. Create 1 to-do list per order
        2. Create 1 to-do per lease (flat structure, no groups)

        Args:
            order: Parent order
            reports: Filtered reports (RUNSHEET, matching agency)
            product_config: Configuration (project_id, agency, name)
            basecamp_service: Basecamp API client
            account_id: Basecamp account ID

        Returns:
            dict with {"todolist_ids": [int], "todo_count": int}

        Raises:
            ValueError: Missing project ID or no leases found
            HTTPError: Basecamp API failure
        """
        # Get project ID
        project_id = self._get_project_id(product_config)

        # Group reports by lease
        grouped_reports = self._group_reports_by_lease(reports, product_config.agency)
        if not grouped_reports:
            logger.info(
                "No leases found for runsheet workflow | order_id=%s | agency=%s",
                order.id,
                product_config.agency,
            )
            return {"todolist_ids": [], "todo_count": 0}

        # Create to-do list
        todolist_id = self._create_todolist(
            order, project_id, basecamp_service, account_id
        )

        # Create to-dos (one per unique lease)
        self._create_todos(
            order=order,
            todolist_id=todolist_id,
            grouped_reports=grouped_reports,
            project_id=project_id,
            basecamp_service=basecamp_service,
            account_id=account_id,
        )

        logger.info(
            "Runsheet workflow created | order_id=%s | product=%s | todolist_id=%s | todo_count=%d",
            order.id,
            product_config.name,
            todolist_id,
            len(grouped_reports),
        )

        return {"todolist_ids": [todolist_id], "todo_count": len(grouped_reports)}

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

    def _group_reports_by_lease(
        self, reports: list["Report"], agency: str
    ) -> dict[str, tuple[list["Report"], "Lease"]]:
        """
        Group reports by their lease number.

        Multiple reports can reference the same lease. This method groups them
        together so we can create one to-do per unique lease with all legal
        descriptions from reports sharing that lease.

        Args:
            reports: List of Report objects
            agency: Agency filter ("BLM" or "NMSLO")

        Returns:
            dict mapping lease_number to (reports_list, lease_object)
            Example: {"NMNM 11111": ([report1, report2], lease_obj)}
        """
        grouped = {}

        for report in reports:
            for lease in report.leases.filter(agency=agency):
                lease_number = lease.lease_number or "[Unknown]"
                if lease_number not in grouped:
                    grouped[lease_number] = ([], lease)
                grouped[lease_number][0].append(report)

        return grouped

    def _create_todolist(
        self,
        order: "Order",
        project_id: str,
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> str:
        """
        Create to-do list for order in Basecamp.

        Args:
            order: Order object
            project_id: Basecamp project ID
            basecamp_service: Basecamp API client
            account_id: Basecamp account ID

        Returns:
            To-do list ID as string

        Raises:
            HTTPError: Basecamp API failure
        """
        # Format: "Order {order_number} - {order_date_YYYYMMDD}"
        todolist_name = (
            f"Order {order.order_number} - {order.order_date.strftime('%Y%m%d')}"
        )

        # Truncate if needed (Basecamp limit)
        if len(todolist_name) > 255:
            todolist_name = todolist_name[:252] + "..."

        # Include delivery link in description if present
        description = ""
        if order.delivery_link:
            description = f"Delivery: {order.delivery_link}"

        # Create to-do list via BasecampService
        result = basecamp_service.create_todolist(
            account_id=account_id,
            project_id=project_id,
            name=todolist_name,
            description=description,
        )

        return str(result["id"])

    def _create_todos(
        self,
        order: "Order",
        todolist_id: str,
        grouped_reports: dict[str, tuple[list["Report"], "Lease"]],
        project_id: str,
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> None:
        """
        Create one to-do per unique lease, with all legal descriptions from reports.

        To-do naming:
        - "{lease_number} - Previous Report" if runsheet_report_found==True
        - "{lease_number}" otherwise

        Description format (HTML):
            <strong>Reports Needed:</strong>
            <ul>
              <li>Sec 1: N2 from <strong>1/1/1979</strong> to <strong>2/2/1988</strong></li>
              <li>Sec 17: NW, S2 from <strong>3/15/1985</strong> to <strong>present</strong></li>
            </ul>
            <strong>Lease Data:</strong> <a href="...">...</a>

        Args:
            order: Order object
            todolist_id: To-do list ID
            grouped_reports: Dict mapping lease_number to (reports_list, lease_object)
            project_id: Basecamp project ID
            basecamp_service: Basecamp API client
            account_id: Basecamp account ID

        Raises:
            HTTPError: Basecamp API failure
        """
        for lease_number, (reports_for_lease, lease) in grouped_reports.items():
            # Build to-do name
            if lease.runsheet_report_found:
                todo_name = f"{lease_number} - Previous Report"
            else:
                todo_name = lease_number

            # Truncate if needed
            if len(todo_name) > 255:
                todo_name = todo_name[:252] + "..."

            # Build HTML description with "Reports Needed:" and "Lease Data:" sections
            html_parts = []

            # Reports Needed section (HTML list)
            if reports_for_lease:
                html_parts.append("<strong>Reports Needed:</strong>")
                html_parts.append("<ul>")
                for report in reports_for_lease:
                    formatted_desc = format_report_description_html(report)
                    html_parts.append(f"<li>{formatted_desc}</li>")
                html_parts.append("</ul>")

            # Lease Data section (link)
            if lease.runsheet_archive and lease.runsheet_archive.share_url:
                archive_url = lease.runsheet_archive.share_url
                html_parts.append(
                    f'<strong>Lease Data:</strong> <a href="{archive_url}">{archive_url}</a>'
                )

            description = "".join(html_parts)

            # Create to-do via BasecampService
            basecamp_service.create_todo(
                account_id=account_id,
                project_id=project_id,
                todolist_id=todolist_id,
                content=todo_name,
                description=description,
            )

            logger.debug(
                "Created runsheet to-do | order_id=%s | lease_id=%s | lease_number=%s | report_count=%d",
                order.id,
                lease.id,
                lease_number,
                len(reports_for_lease),
            )
