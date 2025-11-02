# Research: Basecamp Order Workflows

**Feature**: Basecamp Order Workflows  
**Branch**: `007-basecamp-order-workflows`  
**Date**: 2025-11-02

## Overview

This document resolves technical unknowns and design decisions for implementing automated Basecamp workflow creation. Primary challenges: Strategy Pattern for dual workflow types, DRY configuration for 4 product types, and abstract workflow step definition strategy.

---

## Q1: Strategy Pattern Implementation in Django Services

**Decision**: Use abstract base class (`WorkflowStrategy`) with concrete strategies for each pattern type

**Rationale**:
- Runsheet and Abstract workflows have fundamentally different structures (flat vs grouped, lease-centric vs report-centric)
- Strategy Pattern enables independent evolution of each workflow type without affecting the other
- Follows Open/Closed Principle - can add new workflow patterns without modifying existing code
- Testable - each strategy can be tested in isolation
- Existing codebase already uses service layer pattern, Strategy fits naturally

**Implementation**:
```python
# Base strategy
class WorkflowStrategy(ABC):
    @abstractmethod
    def create_workflow(self, order: Order, product_config: ProductConfig, basecamp_service: BasecampService) -> WorkflowResult:
        pass

# Concrete strategies
class RunsheetWorkflowStrategy(WorkflowStrategy):
    def create_workflow(...) -> WorkflowResult:
        # Pattern A: Create 1 to-do list per order, 1 task per lease

class AbstractWorkflowStrategy(WorkflowStrategy):
    def create_workflow(...) -> WorkflowResult:
        # Pattern B: Create 1 to-do list per report, tasks grouped by department
```

**Alternatives Considered**:
1. **Single monolithic function with conditionals**: Rejected - would have 4-way branching for product types, violates OCP, difficult to test
2. **Separate service classes per product**: Rejected - causes duplication (Federal/State runsheets share 90% logic), harder to maintain consistency
3. **Template Method Pattern**: Rejected - not enough shared structure between patterns to benefit from inheritance

**References**:
- Existing codebase: `orders/services/lease/`, `orders/services/report/` follow entity-centric service organization
- Constitution: Principle III (SOLID), Principle IV (DRY)

---

## Q2: ProductConfig vs Environment Variables for Project Configuration

**Decision**: Use `ProductConfig` dataclass + environment variables hybrid approach

**Rationale**:
- **ProductConfig dataclass**: Encapsulates product-specific logic (agency filter, report types, strategy mapping) in code
- **Environment variables**: Store deployment-specific data (Basecamp project IDs) outside code
- Follows DRY - single configuration point for each product type
- Type-safe with Python dataclasses
- Easy to extend - adding 5th product type requires 1 new ProductConfig entry

**Implementation**:
```python
@dataclass
class ProductConfig:
    name: str                              # "Federal Runsheets"
    project_id_env_var: str                # "BASECAMP_PROJECT_FEDERAL_RUNSHEETS"
    agency: str                            # "BLM"
    report_types: list[str]                # ["RUNSHEET"]
    workflow_strategy: Type[WorkflowStrategy]  # RunsheetWorkflowStrategy

PRODUCT_CONFIGS = {
    "federal_runsheets": ProductConfig(...),
    "federal_abstracts": ProductConfig(...),
    # ...
}
```

**Environment Variables** (in `.env` / Django settings):
```
BASECAMP_PROJECT_FEDERAL_RUNSHEETS=5612345
BASECAMP_PROJECT_FEDERAL_ABSTRACTS=5612346
BASECAMP_PROJECT_STATE_RUNSHEETS=5612347
BASECAMP_PROJECT_STATE_ABSTRACTS=5612348
```

**Alternatives Considered**:
1. **All config in database**: Rejected - adds unnecessary complexity (migrations, admin UI) for static product definitions
2. **All config in environment variables**: Rejected - would require parsing complex structures from env vars (agency, report_types, strategy mapping)
3. **Hardcoded in each strategy**: Rejected - violates DRY, project IDs duplicated, can't reconfigure without code changes

**References**:
- Django settings pattern: Use env vars for deployment-specific config (database URLs, API keys, project IDs)
- Python dataclasses: Type-safe, immutable configuration

---

## Q3: Abstract Workflow Step Definition Strategy

**Decision**: Defer exact workflow steps to implementation, use placeholder structure in code

**Rationale** (from clarification session):
- Spec explicitly defers workflow steps to implementation phase - "focus on getting basics working first"
- Abstract workflow structure is stable (6 groups: Setup, Workup, Imaging, Indexing, Assembly, Delivery)
- Exact step names and lease-specific duplication logic can be finalized by reviewing existing Basecamp abstract projects during implementation
- Hardcoding placeholder steps now enables end-to-end testing of grouped workflow creation
- Steps can be iterated based on real-world usage without refactoring core architecture

**Implementation Approach**:
```python
class AbstractWorkflowStrategy(WorkflowStrategy):
    # Placeholder structure - to be refined during implementation
    WORKFLOW_GROUPS = [
        "Setup",
        "Workup",
        "Imaging",
        "Indexing",
        "Assembly",
        "Delivery"
    ]
    
    # Example steps (to be finalized by reviewing existing Basecamp projects)
    WORKFLOW_STEPS = {
        "Setup": ["Setup Basecamp Project", "Prepare Order"],
        "Workup": [
            # Lease-specific (create once per lease):
            "File Index NMLC-{lease_number}",
            "Create Worksheet {lease_number}",
            "Review Worksheet {lease_number}",
        ],
        # ... other groups
    }
```

**Validation Strategy**:
- Phase 1 implementation: Create workflow with placeholder steps, verify structure (groups created, to-dos assigned to correct groups)
- Phase 2 refinement: Review existing "Federal Abstracts" project in Basecamp, extract exact step names
- Phase 3 iteration: Validate with stakeholders, adjust step names and lease-specific duplication logic

**Alternatives Considered**:
1. **Extract from existing Basecamp projects via API**: Rejected - adds API complexity, assumes existing projects are canonical, brittle if projects vary
2. **Block implementation until steps finalized**: Rejected - delays entire feature for a refinement task, violates "get basics working" directive
3. **User-configurable templates (Phase 3)**: Future work - current phase focuses on hardcoded workflows

**References**:
- Spec clarification Q1: "Defer workflow steps to implementation phase"
- FR-017: "System MUST create workflow steps within each group (exact steps to be finalized during implementation)"

---

## Q4: Success Message Formatting for Multi-Product Workflows

**Decision**: Display summary message with product names only, no direct links to Basecamp to-do lists

**Rationale** (from clarification session):
- Reduces UI complexity - no need to fetch and format multiple Basecamp URLs
- Basecamp URLs are long and cumbersome to display in success message
- Users already know which Basecamp projects correspond to product types
- Focuses message on what was created (product types) rather than where (specific URLs)

**Implementation**:
```python
# Success response structure
{
    "success": True,
    "workflows_created": ["Federal Runsheets", "State Abstracts"],
    "total_count": 2,
    "message": "Workflows created: Federal Runsheets, State Abstracts"
}
```

**Frontend Display**:
```
✓ Success: 2 workflows created
• Federal Runsheets
• State Abstracts
```

**Alternatives Considered**:
1. **Multiple direct links to each to-do list**: Rejected per clarification - adds API overhead to fetch to-do list URLs, clutters UI
2. **Single link to Basecamp account**: Rejected - not specific enough, user has to navigate to find created workflows
3. **No success message**: Rejected - user needs confirmation that workflows were created

**References**:
- Spec clarification Q3: "Summary only - display generic success message with total count, no direct links to individual to-do lists"
- FR-026, FR-030: Success message requirements

---

## Q5: Error Handling and Retry Strategy

**Decision**: Use existing BasecampService exponential backoff retry pattern, comprehensive logging for failures

**Rationale** (from clarification session + existing code):
- BasecampService already implements `_handle_api_error()` with exponential backoff for rate limits (429)
- Consistent behavior across all Basecamp API calls (project APIs, workflow creation)
- Reduces transient failures (network hiccups, temporary Basecamp issues)
- Comprehensive logging (order/report/lease IDs, API errors, stack traces) enables rapid diagnosis

**Implementation**:
- Workflow executor catches exceptions from BasecampService calls
- Logs failures with structured context: `logger.error("Workflow creation failed | order_id=%s | product=%s | error=%s", order_id, product_name, str(e), exc_info=True)`
- Continues processing remaining products on single product failure (partial success)
- Returns detailed error in response: `{"success": False, "error": "Basecamp API error", "failed_products": ["Federal Abstracts"]}`

**Retry Strategy** (inherited from BasecampService):
- 3 retries with exponential backoff: 1s, 2s, 4s delays
- Automatic token refresh on 401 Unauthorized
- Rate limit handling on 429 with backoff

**Alternatives Considered**:
1. **No retries, fail immediately**: Rejected - reduces reliability for transient failures
2. **Simple fixed retry (1 retry after 2s)**: Rejected - inconsistent with existing service, less effective for rate limits
3. **Celery background task with retries**: Rejected - spec requires synchronous workflow creation (user waits for completion), adds complexity

**References**:
- Spec clarification Q4: "Comprehensive - all context including order/report/lease IDs, API errors, stack traces"
- Spec clarification Q5: "Yes - retry with exponential backoff (matches existing basecamp_service.py pattern)"
- Existing code: `web/integrations/basecamp/basecamp_service.py` lines 200-250 (_handle_api_error)
- FR-023, FR-024: Logging and retry requirements

---

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Architecture | Strategy Pattern with base class + concrete strategies | Independent evolution of patterns, testable, SOLID compliant |
| Configuration | ProductConfig dataclass + environment variables | DRY, type-safe, easy to extend |
| Workflow Steps | Defer to implementation, use placeholder structure | Enables progress on core architecture, iterate based on real usage |
| Success Message | Summary with product names only | Simple UI, clear feedback without URL complexity |
| Error Handling | Exponential backoff + comprehensive logging | Consistent with existing service, reliable, debuggable |

---

## Implementation Sequencing

**Recommended Order**:
1. **Phase 1.1 - Foundational**: ProductConfig, WorkflowStrategy base class, WorkflowExecutor skeleton
2. **Phase 1.2 - Pattern A (Runsheets)**: RunsheetWorkflowStrategy, test with Federal Runsheets (simplest product)
3. **Phase 1.3 - Pattern B (Abstracts)**: AbstractWorkflowStrategy with placeholder steps, test with Federal Abstracts
4. **Phase 1.4 - Multi-Product**: Extend to State products, test multi-product orders
5. **Phase 2 - Refinement**: Finalize abstract workflow steps based on existing Basecamp projects

**Critical Path**: RunsheetWorkflowStrategy → AbstractWorkflowStrategy (abstract builds on runsheet patterns for error handling, logging)

---

## Open Questions (Not Blocking)

- **Q**: Should workflow creation be idempotent (prevent duplicate workflows)?
  - **A**: No per spec assumption 7 - "users may need to create workflows multiple times for iteration"
  
- **Q**: Should system track which orders have workflows created?
  - **A**: Out of scope per spec - "No real-time sync" (assumption 8), "Automatic workflow creation" out of scope

- **Q**: Should abstract workflow steps vary by Federal vs State?
  - **A**: Deferred to implementation - current assumption is identical structure per US3 acceptance scenario 3

---

**Status**: ✅ All research complete, ready for Phase 1 (data model, contracts, quickstart)

