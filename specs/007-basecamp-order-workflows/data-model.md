# Data Model: Basecamp Order Workflows

**Feature**: Basecamp Order Workflows  
**Branch**: `007-basecamp-order-workflows`  
**Date**: 2025-11-02

## Overview

This document defines the data structures for automated Basecamp workflow creation. The system uses existing Order/Report/Lease models and introduces new internal entities for workflow execution (ProductConfig, WorkflowResult, WorkflowStrategy implementations).

---

## Existing Entities (No Changes Required)

### Order

**Source**: `web/orders/models.py`  
**Purpose**: Customer order containing one or more requested report items

**Structure**:
```python
class Order(models.Model):
    order_number = CharField(max_length=64, unique=True)
    order_date = DateField()
    delivery_link = URLField(blank=True, null=True)
    # ... timestamps, user tracking fields
```

**Key Fields**:
- `order_number`: Unique identifier used in Basecamp to-do list names
- `order_date`: Used in to-do list naming format "Order {number} - {YYYYMMDD}"
- `delivery_link`: Attached to runsheet to-do list descriptions

**Relationships**:
- One-to-many with `Report`: `order.reports.all()`

**Validation**: N/A (existing model, no changes)

---

### Report

**Source**: `web/orders/models.py`  
**Purpose**: Represents a runsheet or abstract report within an order

**Structure**:
```python
class ReportType(models.TextChoices):
    RUNSHEET = "RUNSHEET", "Runsheet"
    BASE_ABSTRACT = "BASE_ABSTRACT", "Base Abstract"
    SUPPLEMENTAL_ABSTRACT = "SUPPLEMENTAL_ABSTRACT", "Supplemental Abstract"
    DOL_ABSTRACT = "DOL_ABSTRACT", "DOL Abstract"

class Report(models.Model):
    order = ForeignKey(Order, on_delete=CASCADE, related_name="reports")
    report_type = CharField(max_length=32, choices=ReportType.choices)
    legal_description = TextField(blank=True, null=True)
    start_date = DateField(blank=True, null=True)
    end_date = DateField(blank=True, null=True)
    # ... timestamps
```

**Key Fields**:
- `report_type`: Determines workflow pattern (RUNSHEET → Pattern A, *_ABSTRACT → Pattern B)
- `legal_description`: Included in to-do descriptions (both patterns)
- `start_date`, `end_date`: Included in abstract to-do list descriptions as "date range"

**Relationships**:
- Many-to-one with `Order`: `report.order`
- Many-to-many with `Lease`: `report.leases.all()`

**Validation**: N/A (existing model, no changes)

---

### Lease

**Source**: `web/orders/models.py`  
**Purpose**: Represents a land lease with agency and runsheet metadata

**Structure**:
```python
class AgencyType(models.TextChoices):
    NMSLO = "NMSLO", "NMSLO"
    BLM = "BLM", "BLM"

class Lease(models.Model):
    lease_number = CharField(max_length=64)
    agency = CharField(max_length=16, choices=AgencyType.choices)
    runsheet_report_found = BooleanField(default=False)
    runsheet_archive_link = URLField(blank=True, null=True)
    # ... other fields
```

**Key Fields**:
- `lease_number`: Used in to-do item names (runsheets) and abstract descriptions
- `agency`: Filter for product detection (BLM = Federal, NMSLO = State)
- `runsheet_report_found`: Determines to-do naming: "{lease_number} - Previous Report" vs "{lease_number}"
- `runsheet_archive_link`: Included in runsheet to-do descriptions

**Relationships**:
- Many-to-many with `Report`: `lease.reports.all()`

**Validation**: N/A (existing model, no changes)

---

## New Internal Entities (No Database Models)

### ProductConfig

**Source**: `web/orders/services/workflow/config.py` (NEW)  
**Purpose**: Configuration for each of the 4 product types (Federal/State × Runsheets/Abstracts)

**Structure**:
```python
@dataclass(frozen=True)
class ProductConfig:
    name: str                                    # Human-readable: "Federal Runsheets"
    project_id_env_var: str                      # Django setting: "BASECAMP_PROJECT_FEDERAL_RUNSHEETS"
    agency: str                                  # Filter value: "BLM" or "NMSLO"
    report_types: list[str]                      # Filter values: ["RUNSHEET"] or ["BASE_ABSTRACT", "SUPPLEMENTAL_ABSTRACT", "DOL_ABSTRACT"]
    workflow_strategy: Type[WorkflowStrategy]    # Strategy class: RunsheetWorkflowStrategy or AbstractWorkflowStrategy
```

**Key Fields**:
- `name`: Used in success messages ("Workflows created: Federal Runsheets, State Abstracts")
- `project_id_env_var`: Environment variable name to load Basecamp project ID from Django settings
- `agency`: Used to filter leases (`lease.agency == config.agency`)
- `report_types`: Used to filter reports (`report.report_type in config.report_types`)
- `workflow_strategy`: Strategy class to instantiate for this product type

**Validation Rules**:
- `name`: Non-empty string
- `project_id_env_var`: Must exist in Django settings, value must be valid Basecamp project ID (validated at runtime)
- `agency`: Must be "BLM" or "NMSLO"
- `report_types`: Non-empty list of valid ReportType enum values
- `workflow_strategy`: Must be subclass of WorkflowStrategy

**Relationships**:
- Used by `WorkflowExecutor` to determine which products apply to an order
- Passed to `WorkflowStrategy.create_workflow()` as context

**Example Instance**:
```python
PRODUCT_CONFIGS = {
    "federal_runsheets": ProductConfig(
        name="Federal Runsheets",
        project_id_env_var="BASECAMP_PROJECT_FEDERAL_RUNSHEETS",
        agency="BLM",
        report_types=["RUNSHEET"],
        workflow_strategy=RunsheetWorkflowStrategy,
    ),
    # ... 3 more configs
}
```

---

### WorkflowResult

**Source**: `web/orders/services/workflow/executor.py` (NEW)  
**Purpose**: Return type for workflow execution, tracks success/failure per product

**Structure**:
```python
@dataclass
class WorkflowResult:
    success: bool                          # Overall success (True if ANY workflows created)
    workflows_created: list[str]           # Product names that succeeded: ["Federal Runsheets"]
    failed_products: list[str]             # Product names that failed: ["Federal Abstracts"]
    error_details: dict[str, str]          # Map product name → error message
    total_count: int                       # Count of successful workflows
```

**Key Fields**:
- `success`: True if at least one product workflow succeeded, False if all failed or no applicable products
- `workflows_created`: List of product names (from ProductConfig.name) that created workflows successfully
- `failed_products`: List of product names that encountered errors (API failures, missing config)
- `error_details`: Detailed error messages per failed product for logging/debugging
- `total_count`: Count of successful workflows (len(workflows_created))

**Validation Rules**: N/A (return type only)

**Relationships**:
- Returned by `WorkflowExecutor.execute()`
- Serialized by `WorkflowResultSerializer` for API response

**Example Instances**:
```python
# Full success (multi-product order)
WorkflowResult(
    success=True,
    workflows_created=["Federal Runsheets", "Federal Abstracts"],
    failed_products=[],
    error_details={},
    total_count=2,
)

# Partial success (one product failed)
WorkflowResult(
    success=True,
    workflows_created=["Federal Runsheets"],
    failed_products=["Federal Abstracts"],
    error_details={"Federal Abstracts": "Basecamp API timeout"},
    total_count=1,
)

# Total failure
WorkflowResult(
    success=False,
    workflows_created=[],
    failed_products=["Federal Runsheets"],
    error_details={"Federal Runsheets": "Missing project ID configuration"},
    total_count=0,
)
```

---

## Workflow Strategy Interface

### WorkflowStrategy (Abstract Base Class)

**Source**: `web/orders/services/workflow/strategies/base.py` (NEW)  
**Purpose**: Interface for workflow creation strategies (Pattern A and Pattern B)

**Structure**:
```python
from abc import ABC, abstractmethod

class WorkflowStrategy(ABC):
    @abstractmethod
    def create_workflow(
        self,
        order: Order,
        reports: list[Report],
        product_config: ProductConfig,
        basecamp_service: BasecampService,
    ) -> dict:
        """
        Create workflow for given reports using this strategy.
        
        Args:
            order: Parent order (for naming, delivery link)
            reports: Filtered reports applicable to this product (already filtered by report_type and agency)
            product_config: Configuration for this product (project_id, name)
            basecamp_service: Basecamp API client (for creating to-do lists, groups, tasks)
        
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
```

**Key Methods**:
- `create_workflow()`: Main entry point for creating workflows

**Validation Rules**:
- `reports`: Must be non-empty list (caller responsibility to filter)
- `product_config.project_id_env_var`: Must resolve to valid project ID in Django settings
- Basecamp project ID must exist and be accessible with user's credentials

**Relationships**:
- Implemented by `RunsheetWorkflowStrategy` and `AbstractWorkflowStrategy`
- Called by `WorkflowExecutor` for each applicable product

---

### RunsheetWorkflowStrategy (Pattern A)

**Source**: `web/orders/services/workflow/strategies/runsheet.py` (NEW)  
**Purpose**: Creates lease-centric, flat workflows for runsheet products

**Pattern A Logic**:
1. Create 1 to-do list per order in configured Basecamp project
2. To-do list name: "Order {order_number} - {order_date_YYYYMMDD}"
3. To-do list description: Include order delivery_link if present
4. For each lease (filtered by agency):
   - Create 1 to-do item
   - Name: "{lease_number} - Previous Report" if `runsheet_report_found==True`, else "{lease_number}"
   - Description: Report legal_description + lease runsheet_archive_link
5. No groups (flat structure)

**Data Flow**:
```
Order + Reports (filtered) → Extract all leases matching agency →
Create 1 to-do list → Create N to-dos (1 per lease) → Return todolist_id
```

**Validation Rules**:
- At least 1 lease must exist with matching agency (skip reports with no leases)
- Lease numbers must be present (use "[Unknown]" if missing)
- To-do list name truncated at 255 characters if needed
- API calls retry with exponential backoff (inherited from BasecampService)

**Example Output**:
```python
{
    "todolist_ids": [789],  # Single to-do list for order
    "todo_count": 3,        # 3 leases = 3 to-dos
}
```

---

### AbstractWorkflowStrategy (Pattern B)

**Source**: `web/orders/services/workflow/strategies/abstract.py` (NEW)  
**Purpose**: Creates report-centric, grouped workflows for abstract products

**Pattern B Logic**:
1. Create 1 to-do list per report (not per order) in configured Basecamp project
2. To-do list name: "Order {order_number}- {abstract_type} Abstract {report_id} - {order_date_YYYYMMDD}"
   - `abstract_type`: "Base", "Supplemental", or "DOL" (extracted from report_type)
3. To-do list description: Include report type, date range (start_date - end_date), list of lease numbers, legal_description, delivery_link
4. Create 6 Basecamp groups in order: Setup, Workup, Imaging, Indexing, Assembly, Delivery
5. Create workflow steps within each group:
   - Fixed steps: Created once per report (e.g., "Setup Basecamp Project")
   - Lease-specific steps: Created once per lease (e.g., "File Index NMLC-{lease_number}", "Create Worksheet {lease_number}")
6. Assign each to-do to its corresponding group

**Data Flow**:
```
Order + Reports (filtered) →
For each report:
  Create 1 to-do list →
  Create 6 groups →
  For each group:
    Create fixed steps →
    For each lease in report:
      Create lease-specific steps →
  Return todolist_id
```

**Validation Rules**:
- Report must have valid report_type (BASE_ABSTRACT, SUPPLEMENTAL_ABSTRACT, or DOL_ABSTRACT)
- To-do list name truncated at 255 characters if needed
- Groups created in exact order (Setup, Workup, Imaging, Indexing, Assembly, Delivery)
- Lease-specific steps skip if report has no leases (create fixed steps only)
- API calls retry with exponential backoff (inherited from BasecampService)

**Workflow Steps Structure** (placeholder, to be refined during implementation):
```python
WORKFLOW_GROUPS = [
    "Setup",
    "Workup",
    "Imaging",
    "Indexing",
    "Assembly",
    "Delivery",
]

WORKFLOW_STEPS = {
    "Setup": [
        "Setup Basecamp Project",
        "Prepare Order",
    ],
    "Workup": [
        # Lease-specific (create once per lease):
        "File Index NMLC-{lease_number}",
        "Create Worksheet {lease_number}",
        "Review Worksheet {lease_number}",
    ],
    # ... other groups (to be finalized during implementation)
}
```

**Example Output**:
```python
{
    "todolist_ids": [790, 791],  # 2 reports = 2 to-do lists
    "todo_count": 24,            # 6 groups × ~4 steps per report
}
```

---

## Data Flow Diagrams

### Product Detection Flow

```
Order → Order.reports.all() → Filter by report_type and agency →
Group by (report_type, agency) →
Map to ProductConfig (via PRODUCT_CONFIGS lookup) →
List of applicable products: ["federal_runsheets", "federal_abstracts"]
```

**Example**:
```
Order #1234 with 3 reports:
  - Report A: report_type=RUNSHEET, leases=[Lease1(agency=BLM), Lease2(agency=BLM)]
  - Report B: report_type=BASE_ABSTRACT, leases=[Lease1(agency=BLM)]
  - Report C: report_type=RUNSHEET, leases=[Lease3(agency=NMSLO)]

Product Detection:
  ✓ Federal Runsheets: Report A (BLM runsheet)
  ✓ Federal Abstracts: Report B (BLM abstract)
  ✓ State Runsheets: Report C (NMSLO runsheet)
  
Applicable ProductConfigs: 3 (all except State Abstracts)
```

---

### Workflow Execution Flow (Pattern A - Runsheets)

```
WorkflowExecutor.execute(order_id) →
Load order, reports, leases →
Detect applicable products →
For each product (e.g., "federal_runsheets"):
  Load ProductConfig →
  Filter reports (report_type in ["RUNSHEET"]) →
  Filter leases (agency == "BLM") →
  Instantiate RunsheetWorkflowStrategy →
  Call strategy.create_workflow() →
    Get Basecamp project ID from Django settings →
    Create 1 to-do list (order-level) →
    For each lease:
      Create to-do item (lease-level) →
    Return {"todolist_ids": [789], "todo_count": 3} →
  Append "Federal Runsheets" to workflows_created →
Return WorkflowResult
```

---

### Workflow Execution Flow (Pattern B - Abstracts)

```
WorkflowExecutor.execute(order_id) →
Load order, reports, leases →
Detect applicable products →
For each product (e.g., "federal_abstracts"):
  Load ProductConfig →
  Filter reports (report_type in ["BASE_ABSTRACT", "SUPPLEMENTAL_ABSTRACT", "DOL_ABSTRACT"]) →
  Filter leases (agency == "BLM") →
  Instantiate AbstractWorkflowStrategy →
  Call strategy.create_workflow() →
    Get Basecamp project ID from Django settings →
    For each report:
      Create 1 to-do list (report-level) →
      Create 6 groups (Setup, Workup, ..., Delivery) →
      For each group:
        Create fixed steps →
        For each lease in report:
          Create lease-specific steps →
      Append todolist_id to results →
    Return {"todolist_ids": [790, 791], "todo_count": 24} →
  Append "Federal Abstracts" to workflows_created →
Return WorkflowResult
```

---

## Environment Configuration

### Django Settings

**Source**: `web/order_manager_project/settings.py`  
**Purpose**: Store Basecamp project IDs as environment variables

**Required Settings**:
```python
# Basecamp Project IDs (must be configured before feature use)
BASECAMP_PROJECT_FEDERAL_RUNSHEETS = env("BASECAMP_PROJECT_FEDERAL_RUNSHEETS", default=None)
BASECAMP_PROJECT_FEDERAL_ABSTRACTS = env("BASECAMP_PROJECT_FEDERAL_ABSTRACTS", default=None)
BASECAMP_PROJECT_STATE_RUNSHEETS = env("BASECAMP_PROJECT_STATE_RUNSHEETS", default=None)
BASECAMP_PROJECT_STATE_ABSTRACTS = env("BASECAMP_PROJECT_STATE_ABSTRACTS", default=None)
```

**Validation**:
- If `None`, raise `ValueError` with message: "Missing project ID configuration for {product_name}. Set {project_id_env_var} in environment variables."
- Value must be convertible to integer (Basecamp project IDs are numeric strings)

**.env Example**:
```bash
BASECAMP_PROJECT_FEDERAL_RUNSHEETS=5612345
BASECAMP_PROJECT_FEDERAL_ABSTRACTS=5612346
BASECAMP_PROJECT_STATE_RUNSHEETS=5612347
BASECAMP_PROJECT_STATE_ABSTRACTS=5612348
```

---

## Summary

**Existing Entities**: Order, Report, Lease (no changes to models)  
**New Internal Entities**: ProductConfig (dataclass), WorkflowResult (dataclass), WorkflowStrategy (interface + 2 implementations)  
**Configuration**: 4 environment variables for Basecamp project IDs  
**Data Flow**: Order → Product Detection → Strategy Selection → Workflow Creation → WorkflowResult

**Key Relationships**:
- Order 1:N Report M:N Lease (existing)
- ProductConfig → WorkflowStrategy (composition)
- WorkflowExecutor → ProductConfig → WorkflowStrategy (delegation)

**Validation**: Environment variables required, report/lease filtering by type and agency, API retry with exponential backoff

