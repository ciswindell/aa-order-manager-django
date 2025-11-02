"""Runsheet workflow strategy (Pattern A: lease-centric, flat structure)."""

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from orders.services.workflow.strategies.base import WorkflowStrategy

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

        # Extract leases
        leases = self._extract_leases(reports, product_config.agency)
        if not leases:
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

        # Create to-dos
        self._create_todos(
            order=order,
            todolist_id=todolist_id,
            leases=leases,
            reports=reports,
            project_id=project_id,
            basecamp_service=basecamp_service,
            account_id=account_id,
        )

        logger.info(
            "Runsheet workflow created | order_id=%s | product=%s | todolist_id=%s | todo_count=%d",
            order.id,
            product_config.name,
            todolist_id,
            len(leases),
        )

        return {"todolist_ids": [todolist_id], "todo_count": len(leases)}

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

    def _extract_leases(self, reports: list["Report"], agency: str) -> list:
        """
        Extract all leases matching agency from reports.

        Deduplicates leases across reports (same lease may be in multiple reports).

        Args:
            reports: List of Report objects
            agency: Agency filter ("BLM" or "NMSLO")

        Returns:
            List of deduplicated Lease objects matching agency
        """
        seen_lease_ids = set()
        leases = []

        for report in reports:
            for lease in report.leases.filter(agency=agency):
                if lease.id not in seen_lease_ids:
                    seen_lease_ids.add(lease.id)
                    leases.append(lease)

        return leases

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
        leases: list,
        reports: list["Report"],
        project_id: str,
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> None:
        """
        Create to-do items for each lease.

        To-do naming:
        - "{lease_number} - Previous Report" if runsheet_report_found==True
        - "{lease_number}" otherwise

        Description includes:
        - Report legal_description
        - Lease runsheet_archive_link

        Args:
            order: Order object
            todolist_id: To-do list ID
            leases: List of Lease objects
            reports: List of Report objects (for legal_description)
            project_id: Basecamp project ID
            basecamp_service: Basecamp API client
            account_id: Basecamp account ID

        Raises:
            HTTPError: Basecamp API failure
        """
        # Get legal description from first report (shared across all leases in runsheet)
        legal_description = ""
        if reports:
            legal_description = reports[0].legal_description or ""

        for lease in leases:
            # Build to-do name
            lease_number = lease.lease_number or "[Unknown]"
            if lease.runsheet_report_found:
                todo_name = f"{lease_number} - Previous Report"
            else:
                todo_name = lease_number

            # Truncate if needed
            if len(todo_name) > 255:
                todo_name = todo_name[:252] + "..."

            # Build description
            description_parts = []
            if legal_description:
                description_parts.append(f"Legal Description: {legal_description}")
            
            # Add archive link if available (from runsheet_archive.share_url)
            if lease.runsheet_archive and lease.runsheet_archive.share_url:
                description_parts.append(f"Archive: {lease.runsheet_archive.share_url}")

            description = "\n\n".join(description_parts)

            # Create to-do via BasecampService
            basecamp_service.create_todo(
                account_id=account_id,
                project_id=project_id,
                todolist_id=todolist_id,
                content=todo_name,
                description=description,
            )

            logger.debug(
                "Created runsheet to-do | order_id=%s | lease_id=%s | lease_number=%s",
                order.id,
                lease.id,
                lease_number,
            )
