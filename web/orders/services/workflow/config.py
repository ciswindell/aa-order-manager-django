"""Configuration for workflow automation across product types."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orders.services.workflow.strategies.base import WorkflowStrategy

# Import strategy classes
from orders.services.workflow.strategies.runsheet import RunsheetWorkflowStrategy


@dataclass(frozen=True)
class ProductConfig:
    """Configuration for a single product type (e.g., Federal Runsheets)."""

    name: str  # Human-readable: "Federal Runsheets"
    project_id_env_var: str  # Django setting: "BASECAMP_PROJECT_FEDERAL_RUNSHEETS"
    agency: str  # Filter value: "BLM" or "NMSLO"
    report_types: list[str]  # ["RUNSHEET"] or ["BASE_ABSTRACT", "SUPPLEMENTAL_ABSTRACT", "DOL_ABSTRACT"]
    workflow_strategy: type["WorkflowStrategy"]  # Strategy class to instantiate


# PRODUCT_CONFIGS dictionary populated with forward references to strategy classes
# Strategy classes will be imported and assigned in Phase 3+ implementation
PRODUCT_CONFIGS: dict[str, ProductConfig] = {
    "federal_runsheets": ProductConfig(
        name="Federal Runsheets",
        project_id_env_var="BASECAMP_PROJECT_FEDERAL_RUNSHEETS",
        agency="BLM",
        report_types=["RUNSHEET"],
        workflow_strategy=RunsheetWorkflowStrategy,
    ),
    "federal_abstracts": ProductConfig(
        name="Federal Abstracts",
        project_id_env_var="BASECAMP_PROJECT_FEDERAL_ABSTRACTS",
        agency="BLM",
        report_types=["BASE_ABSTRACT", "SUPPLEMENTAL_ABSTRACT", "DOL_ABSTRACT"],
        workflow_strategy=None,  # type: ignore  # Will be set to AbstractWorkflowStrategy in Phase 4
    ),
    "state_runsheets": ProductConfig(
        name="State Runsheets",
        project_id_env_var="BASECAMP_PROJECT_STATE_RUNSHEETS",
        agency="NMSLO",
        report_types=["RUNSHEET"],
        workflow_strategy=RunsheetWorkflowStrategy,  # Reuses same strategy as Federal Runsheets
    ),
    "state_abstracts": ProductConfig(
        name="State Abstracts",
        project_id_env_var="BASECAMP_PROJECT_STATE_ABSTRACTS",
        agency="NMSLO",
        report_types=["BASE_ABSTRACT", "SUPPLEMENTAL_ABSTRACT", "DOL_ABSTRACT"],
        workflow_strategy=None,  # type: ignore  # Will be set to AbstractWorkflowStrategy in Phase 5
    ),
}

