"""Workflow executor for orchestrating workflow creation across product types."""

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from integrations.basecamp.basecamp_service import BasecampService
from integrations.models import BasecampAccount
from orders.models import Order
from orders.services.workflow.config import PRODUCT_CONFIGS

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class WorkflowResult:
    """Result of workflow execution tracking success/failure per product."""

    success: bool  # True if ANY workflows created
    workflows_created: list[str]  # Product names that succeeded
    failed_products: list[str] = field(default_factory=list)  # Product names that failed
    error_details: dict[str, str] = field(default_factory=dict)  # Product name → error message
    total_count: int = 0  # Count of successful workflows


class WorkflowExecutor:
    """Orchestrates workflow creation by delegating to appropriate strategies."""

    def execute(self, order_id: int, user_id: int) -> WorkflowResult:
        """
        Execute workflow creation for all applicable products in an order.

        Args:
            order_id: Primary key of the Order
            user_id: Primary key of the User triggering the workflow

        Returns:
            WorkflowResult with success status and created workflow details

        Raises:
            ValueError: Configuration errors (missing project IDs)
            HTTPError: Basecamp API failures (after retries)
        """
        # 1. Load order with reports and leases
        order = Order.objects.select_related().prefetch_related(
            "reports__leases__runsheet_archive"
        ).get(pk=order_id)

        # 2. Get BasecampService for user
        basecamp_account = BasecampAccount.objects.get(user_id=user_id)
        basecamp_service = BasecampService(access_token=basecamp_account.access_token)
        account_id = str(basecamp_account.account_id)

        # 3. Detect applicable products and execute workflows
        workflows_created = []
        failed_products = []
        error_details = {}
        total_todos = 0

        for product_key, product_config in PRODUCT_CONFIGS.items():
            # Skip if strategy not yet implemented (None)
            if product_config.workflow_strategy is None:
                continue

            # Filter reports by report_type
            applicable_reports = [
                report
                for report in order.reports.all()
                if report.report_type in product_config.report_types
            ]

            # Filter by agency (check if any leases match agency)
            reports_with_matching_leases = []
            for report in applicable_reports:
                if report.leases.filter(agency=product_config.agency).exists():
                    reports_with_matching_leases.append(report)

            # Skip if no applicable reports
            if not reports_with_matching_leases:
                logger.debug(
                    "No applicable reports for product | order_id=%s | product=%s",
                    order_id,
                    product_config.name,
                )
                continue

            # Execute workflow for this product
            try:
                strategy = product_config.workflow_strategy()
                result = strategy.create_workflow(
                    order=order,
                    reports=reports_with_matching_leases,
                    product_config=product_config,
                    basecamp_service=basecamp_service,
                    account_id=account_id,
                )

                # Track success
                if result["todo_count"] > 0:
                    workflows_created.append(product_config.name)
                    total_todos += result["todo_count"]

                    logger.info(
                        "Workflow created | order_id=%s | user_id=%s | product=%s | todos=%d",
                        order_id,
                        user_id,
                        product_config.name,
                        result["todo_count"],
                    )

            except ValueError as e:
                # Configuration error (missing project ID)
                failed_products.append(product_config.name)
                error_details[product_config.name] = str(e)
                logger.error(
                    "Workflow creation failed - configuration error | order_id=%s | product=%s | error=%s",
                    order_id,
                    product_config.name,
                    str(e),
                )
            except Exception as e:
                # API error or other failure
                failed_products.append(product_config.name)
                error_details[product_config.name] = str(e)
                logger.error(
                    "Workflow creation failed | order_id=%s | product=%s | error=%s",
                    order_id,
                    product_config.name,
                    str(e),
                    exc_info=True,
                )

        # 5. Return result
        success = len(workflows_created) > 0
        
        # Log summary
        if not success and not failed_products:
            logger.info(
                "Workflow creation returned no workflows | order_id=%s | user_id=%s",
                order_id,
                user_id,
            )
        elif not success and failed_products:
            logger.warning(
                "Workflow creation failed for all products | order_id=%s | user_id=%s | failed=%s",
                order_id,
                user_id,
                ", ".join(failed_products),
            )
        elif success and failed_products:
            logger.warning(
                "Workflow creation partial success | order_id=%s | user_id=%s | succeeded=%s | failed=%s",
                order_id,
                user_id,
                ", ".join(workflows_created),
                ", ".join(failed_products),
            )
        
        return WorkflowResult(
            success=success,
            workflows_created=workflows_created,
            failed_products=failed_products,
            error_details=error_details,
            total_count=total_todos,
        )

