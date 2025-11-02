# Quickstart: Basecamp Order Workflows

**Feature**: Basecamp Order Workflows  
**Branch**: `007-basecamp-order-workflows`  
**Date**: 2025-11-02

## Overview

This guide provides a step-by-step implementation checklist for automated Basecamp workflow creation. Follow phases in order - each phase builds on the previous. Estimated time: 3-5 days for experienced Django/Next.js developer.

---

## Prerequisites

- [x] Existing: Order, Report, Lease models with proper relationships
- [x] Existing: BasecampService with API methods (create_todolist, create_todo, create_group)
- [x] Existing: BasecampAccount model with user authentication
- [x] Existing: Order details page in Next.js frontend
- [ ] Required: 4 Basecamp project IDs configured in environment variables

---

## Phase 1: Configuration & Setup (30 min)

### 1.1 Environment Variables

Add to `.env`:
```bash
BASECAMP_PROJECT_FEDERAL_RUNSHEETS=5612345
BASECAMP_PROJECT_FEDERAL_ABSTRACTS=5612346
BASECAMP_PROJECT_STATE_RUNSHEETS=5612347
BASECAMP_PROJECT_STATE_ABSTRACTS=5612348
```

**Verification**: Run `docker compose exec web python3 -c "from django.conf import settings; print(settings.BASECAMP_PROJECT_FEDERAL_RUNSHEETS)"`

---

### 1.2 Django Settings

Add to `web/order_manager_project/settings.py`:
```python
# Basecamp Project IDs
BASECAMP_PROJECT_FEDERAL_RUNSHEETS = env("BASECAMP_PROJECT_FEDERAL_RUNSHEETS", default=None)
BASECAMP_PROJECT_FEDERAL_ABSTRACTS = env("BASECAMP_PROJECT_FEDERAL_ABSTRACTS", default=None)
BASECAMP_PROJECT_STATE_RUNSHEETS = env("BASECAMP_PROJECT_STATE_RUNSHEETS", default=None)
BASECAMP_PROJECT_STATE_ABSTRACTS = env("BASECAMP_PROJECT_STATE_ABSTRACTS", default=None)
```

**Verification**: Settings load without errors on `docker compose exec web python3 manage.py check`

---

## Phase 2: Backend - Workflow Service (2 days)

### 2.1 Create Workflow Service Directory Structure

```bash
cd web/orders/services/
mkdir -p workflow/strategies
touch workflow/__init__.py
touch workflow/config.py
touch workflow/executor.py
touch workflow/strategies/__init__.py
touch workflow/strategies/base.py
touch workflow/strategies/runsheet.py
touch workflow/strategies/abstract.py
```

---

### 2.2 Implement ProductConfig (config.py)

**File**: `web/orders/services/workflow/config.py`

**Key Classes**:
```python
from dataclasses import dataclass
from typing import Type

@dataclass(frozen=True)
class ProductConfig:
    name: str                                    # "Federal Runsheets"
    project_id_env_var: str                      # "BASECAMP_PROJECT_FEDERAL_RUNSHEETS"
    agency: str                                  # "BLM" or "NMSLO"
    report_types: list[str]                      # ["RUNSHEET"] or ["BASE_ABSTRACT", ...]
    workflow_strategy: Type['WorkflowStrategy']  # RunsheetWorkflowStrategy or AbstractWorkflowStrategy

PRODUCT_CONFIGS = {
    "federal_runsheets": ProductConfig(
        name="Federal Runsheets",
        project_id_env_var="BASECAMP_PROJECT_FEDERAL_RUNSHEETS",
        agency="BLM",
        report_types=["RUNSHEET"],
        workflow_strategy=RunsheetWorkflowStrategy,  # Forward reference
    ),
    # ... 3 more configs
}
```

**Verification**: Import without errors: `from orders.services.workflow.config import PRODUCT_CONFIGS`

---

### 2.3 Implement WorkflowStrategy Base Class (strategies/base.py)

**File**: `web/orders/services/workflow/strategies/base.py`

**Key Methods**:
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
        Returns: {"todolist_ids": [123, 456], "todo_count": 10}
        Raises: ValueError, HTTPError
        """
        pass
```

**Verification**: Import without errors: `from orders.services.workflow.strategies.base import WorkflowStrategy`

---

### 2.4 Implement RunsheetWorkflowStrategy (strategies/runsheet.py)

**File**: `web/orders/services/workflow/strategies/runsheet.py`

**Key Logic**:
1. Load Basecamp project ID from Django settings
2. Extract all leases matching agency from reports
3. Create 1 to-do list for order:
   - Name: `f"Order {order.order_number} - {order.order_date.strftime('%Y%m%d')}"`
   - Description: Include `order.delivery_link` if present
4. For each lease:
   - Create to-do item:
     - Name: `f"{lease.lease_number} - Previous Report"` if `lease.runsheet_report_found` else `lease.lease_number`
     - Description: Include report legal_description + `lease.runsheet_archive_link`
5. Return `{"todolist_ids": [todolist_id], "todo_count": len(leases)}`

**Key Methods**:
```python
def create_workflow(self, order, reports, product_config, basecamp_service) -> dict:
    # 1. Get project ID
    project_id = self._get_project_id(product_config)
    
    # 2. Extract leases
    leases = self._extract_leases(reports, product_config.agency)
    if not leases:
        return {"todolist_ids": [], "todo_count": 0}
    
    # 3. Create to-do list
    todolist_id = self._create_todolist(order, project_id, basecamp_service)
    
    # 4. Create to-dos
    self._create_todos(todolist_id, leases, reports, project_id, basecamp_service)
    
    return {"todolist_ids": [todolist_id], "todo_count": len(leases)}
```

**Verification**: Unit test with mock BasecampService

---

### 2.5 Implement AbstractWorkflowStrategy (strategies/abstract.py)

**File**: `web/orders/services/workflow/strategies/abstract.py`

**Key Logic**:
1. Load Basecamp project ID from Django settings
2. For each report:
   - Extract abstract type ("Base", "Supplemental", "DOL") from report_type
   - Create 1 to-do list:
     - Name: `f"Order {order.order_number}- {abstract_type} Abstract {report.id} - {order.order_date.strftime('%Y%m%d')}"`
     - Description: Include report type, date range, lease numbers, legal_description, delivery_link
   - Create 6 groups: Setup, Workup, Imaging, Indexing, Assembly, Delivery
   - Create workflow steps (placeholder structure, to be refined):
     - Fixed steps: Created once per report
     - Lease-specific steps: Created once per lease (e.g., "File Index NMLC-{lease_number}")
   - Assign each to-do to corresponding group
3. Return `{"todolist_ids": [list of todolist IDs], "todo_count": total_todos}`

**Key Methods**:
```python
WORKFLOW_GROUPS = ["Setup", "Workup", "Imaging", "Indexing", "Assembly", "Delivery"]

WORKFLOW_STEPS = {
    "Setup": ["Setup Basecamp Project", "Prepare Order"],
    "Workup": [
        # Lease-specific (use {lease_number} placeholder):
        "File Index NMLC-{lease_number}",
        "Create Worksheet {lease_number}",
        "Review Worksheet {lease_number}",
    ],
    # ... other groups (to be finalized during implementation)
}

def create_workflow(self, order, reports, product_config, basecamp_service) -> dict:
    # 1. Get project ID
    # 2. For each report:
    #    - Create to-do list
    #    - Create groups
    #    - Create steps (fixed + lease-specific)
    # 3. Return results
```

**Verification**: Unit test with mock BasecampService

---

### 2.6 Implement WorkflowExecutor (executor.py)

**File**: `web/orders/services/workflow/executor.py`

**Key Classes**:
```python
from dataclasses import dataclass

@dataclass
class WorkflowResult:
    success: bool
    workflows_created: list[str]
    failed_products: list[str]
    error_details: dict[str, str]
    total_count: int

class WorkflowExecutor:
    def execute(self, order_id: int, user_id: int) -> WorkflowResult:
        # 1. Load order with reports and leases (select_related, prefetch_related)
        # 2. Get BasecampService for user
        # 3. Detect applicable products (filter by report_type + agency)
        # 4. For each applicable product:
        #    - Instantiate strategy
        #    - Call strategy.create_workflow()
        #    - Append to workflows_created or failed_products
        # 5. Return WorkflowResult
```

**Verification**: Integration test with real Order/Report/Lease data

---

### 2.7 Create API View (orders/views/workflows.py)

**File**: `web/orders/views/workflows.py` (NEW)

**Key Function**:
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_workflow(request, order_id):
    # 1. Validate order exists
    # 2. Validate Basecamp connection
    # 3. Execute workflows via WorkflowExecutor
    # 4. Serialize and return result
```

**Verification**: Manual test with curl + JWT token

---

### 2.8 Add URL Route (web/api/urls.py)

Add to `urlpatterns`:
```python
from orders.views.workflows import trigger_workflow

urlpatterns = [
    # ... existing patterns
    path("orders/<int:order_id>/workflows/", trigger_workflow, name="trigger_workflow"),
]
```

**Verification**: URL resolves correctly: `docker compose exec web python3 manage.py show_urls | grep workflows`

---

### 2.9 Create Serializer (web/api/serializers/workflows.py)

**File**: `web/api/serializers/workflows.py` (NEW)

**Key Class**:
```python
class WorkflowResultSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    workflows_created = serializers.ListField(child=serializers.CharField())
    failed_products = serializers.ListField(child=serializers.CharField(), required=False)
    total_count = serializers.IntegerField()
    message = serializers.CharField()
```

**Verification**: Serializer accepts WorkflowResult dataclass

---

## Phase 3: Frontend - Push to Basecamp Button (1 day)

### 3.1 Create API Client (frontend/src/lib/api/workflows.ts)

**File**: `frontend/src/lib/api/workflows.ts` (NEW)

**Key Functions**:
```typescript
export interface WorkflowResult {
  success: boolean;
  workflows_created: string[];
  failed_products?: string[];
  total_count: number;
  message: string;
}

export async function triggerWorkflow(orderId: number): Promise<WorkflowResult> {
  const response = await axios.post<WorkflowResult>(
    `/api/orders/${orderId}/workflows/`,
    {},
    { withCredentials: true }
  );
  return response.data;
}
```

**Verification**: TypeScript compiles without errors

---

### 3.2 Update Types (frontend/src/lib/api/types.ts)

Add `WorkflowResult` interface to types file if not using separate workflows.ts

---

### 3.3 Add Button to Order Details Page (frontend/src/app/dashboard/orders/[id]/page.tsx)

**Modifications**:
1. Import `triggerWorkflow` and `Button` component
2. Add state: `const [loading, setLoading] = useState(false)`
3. Add click handler:
   ```typescript
   async function handlePushToBasecamp() {
     setLoading(true);
     try {
       const result = await triggerWorkflow(orderId);
       if (result.success) {
         toast.success(result.message);
       } else {
         toast.warning(result.message);
       }
     } catch (err) {
       toast.error(err.response?.data?.message || 'Failed to create workflows');
     } finally {
       setLoading(false);
     }
   }
   ```
4. Add button component:
   ```tsx
   <Button onClick={handlePushToBasecamp} disabled={loading}>
     {loading ? 'Creating...' : 'Push to Basecamp'}
   </Button>
   ```

**Verification**: Button appears on order details page, disabled state works

---

## Phase 4: Testing & Validation (1 day)

### 4.1 Backend Unit Tests

**Test Files**:
- `web/orders/tests/test_workflow_strategies.py`
- `web/orders/tests/test_workflow_executor.py`

**Test Cases**:
1. **RunsheetWorkflowStrategy**:
   - Creates 1 to-do list with correct name format
   - Creates to-dos for all matching leases
   - Handles "Previous Report" suffix correctly
   - Skips reports with no leases

2. **AbstractWorkflowStrategy**:
   - Creates 1 to-do list per report
   - Creates 6 groups in correct order
   - Creates fixed steps once per report
   - Creates lease-specific steps once per lease
   - Extracts abstract type correctly ("Base", "Supplemental", "DOL")

3. **WorkflowExecutor**:
   - Detects correct products for order (Federal/State, Runsheets/Abstracts)
   - Calls correct strategies
   - Handles partial success (some products fail)
   - Handles no applicable products
   - Logs comprehensive context on failure

**Verification**: `docker compose exec web python3 manage.py test orders.tests.test_workflow_strategies`

---

### 4.2 Integration Tests

**Test Order Setup**:
1. Create Order #TEST001 with order_date = today
2. Add 2 BLM RUNSHEET reports with 3 BLM leases
3. Add 1 BLM BASE_ABSTRACT report with 2 BLM leases
4. Add 1 NMSLO RUNSHEET report with 1 NMSLO lease

**Expected Results**:
- Federal Runsheets: 1 to-do list with 3 to-dos
- Federal Abstracts: 1 to-do list with 6 groups, ~12 to-dos
- State Runsheets: 1 to-do list with 1 to-do

**Manual Test**:
```bash
# 1. Create test order in Django admin
# 2. Get JWT token
# 3. Trigger workflow via API
curl -X POST http://localhost:8000/api/orders/TEST001/workflows/ \
  -H "Cookie: access_token=<jwt_token>" \
  -v

# 4. Verify workflows created in Basecamp (check each project)
```

**Verification**: All 3 product workflows created in correct Basecamp projects

---

### 4.3 Frontend E2E Test

**Test Flow**:
1. Navigate to order details page
2. Click "Push to Basecamp" button
3. Verify button shows "Creating..." loading state
4. Verify success toast appears with workflow names
5. Verify button re-enables after completion

**Verification**: Manual browser test or Playwright/Cypress test

---

### 4.4 Error Handling Tests

**Test Cases**:
1. **Missing Basecamp connection**: Verify 422 error with "Basecamp not connected" message
2. **Missing project ID**: Verify 422 error with "Missing project ID configuration for {product}" message
3. **Basecamp API failure**: Verify retry logic, comprehensive logging, user-friendly error message
4. **Order not found**: Verify 404 error
5. **Unauthorized**: Verify 401 error

**Verification**: Mock BasecampService to raise exceptions, verify responses

---

## Phase 5: Documentation & Deployment (30 min)

### 5.1 Update README

Add to project README:
```markdown
## Basecamp Workflow Automation

Orders can be pushed to Basecamp to create task workflows automatically.

**Configuration**:
Set these environment variables:
- `BASECAMP_PROJECT_FEDERAL_RUNSHEETS`
- `BASECAMP_PROJECT_FEDERAL_ABSTRACTS`
- `BASECAMP_PROJECT_STATE_RUNSHEETS`
- `BASECAMP_PROJECT_STATE_ABSTRACTS`

**Usage**:
1. Navigate to order details page
2. Click "Push to Basecamp" button
3. Workflows are created in corresponding Basecamp projects based on order contents
```

---

### 5.2 Deploy Configuration

**Production Deployment Checklist**:
- [ ] Set all 4 Basecamp project ID environment variables
- [ ] Verify project IDs are correct (test with sample order)
- [ ] Configure monitoring/alerting for workflow creation failures
- [ ] Test OAuth token refresh for Basecamp API
- [ ] Verify CORS settings allow frontend origin

---

## Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| `web/orders/services/workflow/config.py` | ProductConfig + PRODUCT_CONFIGS dict |
| `web/orders/services/workflow/executor.py` | WorkflowExecutor + WorkflowResult |
| `web/orders/services/workflow/strategies/base.py` | WorkflowStrategy interface |
| `web/orders/services/workflow/strategies/runsheet.py` | Pattern A implementation |
| `web/orders/services/workflow/strategies/abstract.py` | Pattern B implementation |
| `web/orders/views/workflows.py` | API view for workflow trigger |
| `web/api/urls.py` | URL route for `/api/orders/{id}/workflows/` |
| `web/api/serializers/workflows.py` | WorkflowResultSerializer |
| `frontend/src/lib/api/workflows.ts` | Frontend API client |
| `frontend/src/app/dashboard/orders/[id]/page.tsx` | Order details page with button |

---

### Environment Variables

```bash
BASECAMP_PROJECT_FEDERAL_RUNSHEETS=<project_id>
BASECAMP_PROJECT_FEDERAL_ABSTRACTS=<project_id>
BASECAMP_PROJECT_STATE_RUNSHEETS=<project_id>
BASECAMP_PROJECT_STATE_ABSTRACTS=<project_id>
```

---

### Testing Commands

```bash
# Backend unit tests
docker compose exec web python3 manage.py test orders.tests.test_workflow_strategies

# Manual API test
curl -X POST http://localhost:8000/api/orders/123/workflows/ \
  -H "Cookie: access_token=<jwt_token>" \
  -v

# Frontend dev server
docker compose exec frontend npm run dev
```

---

## Success Criteria Checklist

Per spec.md:

- [ ] **SC-001**: User can create workflows for all applicable products with single button click
- [ ] **SC-002**: Workflow creation completes within 30 seconds for orders with up to 10 reports
- [ ] **SC-003**: System successfully creates workflows for 95% of orders (excluding config/connection errors)
- [ ] **SC-004**: Success message displays within 5 seconds with workflow creation summary
- [ ] **SC-005**: For runsheet orders, each lease appears as exactly one to-do item with correct naming
- [ ] **SC-006**: For abstract orders, each report results in exactly one to-do list with 6 department groups
- [ ] **SC-007**: Multi-product orders create workflows in all applicable Basecamp projects without manual intervention
- [ ] **SC-008**: Workflow creation errors are resolved within 2 minutes by following displayed error messages
- [ ] **SC-009**: System handles orders with mixed product types without creating duplicate or missing workflows

---

## Troubleshooting

**Problem**: "Missing project ID configuration for Federal Runsheets"  
**Solution**: Set `BASECAMP_PROJECT_FEDERAL_RUNSHEETS` in `.env` file and restart Docker containers

**Problem**: "Basecamp not connected"  
**Solution**: User needs to authorize Basecamp account via integrations page

**Problem**: Workflows created but in wrong projects  
**Solution**: Verify project ID environment variables match correct Basecamp projects (check project IDs in Basecamp URL)

**Problem**: To-dos created without groups (abstracts)  
**Solution**: Check `AbstractWorkflowStrategy._create_groups()` is called before `_create_todos()`

**Problem**: Duplicate to-dos for same lease  
**Solution**: Verify lease filtering logic in `_extract_leases()` - should deduplicate across reports

---

**Estimated Total Time**: 3-5 days (2 days backend, 1 day frontend, 1 day testing, 0.5 day docs)

**Next Step**: Begin Phase 1 (Configuration & Setup)

