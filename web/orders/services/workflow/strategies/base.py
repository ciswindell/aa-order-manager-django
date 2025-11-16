"""Base strategy interface for workflow creation."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from integrations.basecamp.basecamp_service import BasecampService
    from orders.models import Order, Report
    from orders.services.workflow.config import ProductConfig


class WorkflowStrategy(ABC):
    """Abstract base class for workflow creation strategies."""

    @abstractmethod
    def create_workflow(
        self,
        order: "Order",
        reports: list["Report"],
        product_config: "ProductConfig",
        basecamp_service: "BasecampService",
        account_id: str,
    ) -> dict:
        """
        Create workflow for given reports using this strategy.

        Args:
            order: Parent order (for naming, delivery link)
            reports: Filtered reports applicable to this product
                    (already filtered by report_type and agency)
            product_config: Configuration for this product (project_id, name)
            basecamp_service: Basecamp API client
                             (for creating to-do lists, groups, tasks)
            account_id: Basecamp account ID

        Returns:
            dict with created Basecamp entity IDs:
                {
                    "todolist_ids": [123, 456],  # Created to-do list IDs
                    "todo_count": 10,            # Total to-dos created
                }

        Raises:
            ValueError: Missing required data (project ID, empty reports)
            HTTPError: Basecamp API failure (already retried)
        """
        pass

