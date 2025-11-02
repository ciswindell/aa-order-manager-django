# Basecamp Workflow Templates - Implementation Guide

## Overview

This guide outlines the path from current Basecamp OAuth integration to a full database-driven workflow template system that allows business users to configure Basecamp task creation through Django Admin.

**Current Status**: Phase 1 (API Service Extension) is complete. Phase 2 (Hardcoded Workflows) is now specified and ready for implementation. The system supports 4 product types across 2 distinct workflow patterns (Runsheet vs Abstract).

## Current State

### ✅ What's Already Built
- **Basecamp OAuth 2.0 Integration**: Complete authentication flow
- **Token Management**: Automatic refresh with encryption at rest
- **Database Models**: `BasecampAccount` for storing user credentials
- **API Endpoints**: `/connect`, `/disconnect`, `/callback`, `/status`
- **Frontend Integration**: React components and API client
- **Basecamp API Service** ⭐ NEW: Complete project/task management methods
  - List and retrieve projects
  - Create to-do lists with duplicate detection
  - Create and update tasks with assignees and due dates
  - Create groups to organize tasks
  - Add comments and notes
  - Full error handling and logging

### ❌ What's Missing
- **Workflow Creation Logic**: No code to create complete workflows from orders (Phase 2 - now specified with dual patterns)
- **Template System**: No database models or template processing for configurable workflows (Phase 3 - may not be needed)

### ⚠️ Known Issues
- **OAuth Account Selection**: When user has access to multiple Basecamp accounts (e.g., "American Abstract LLC" and "Dudley Land Company"), the system automatically selects the first account without prompting. This can result in connecting the wrong account.

---

## Strategic Approach: 4 Phases

### Phase 0: OAuth Account Selection (Optional Enhancement)

**Goal**: Allow users to choose which Basecamp account to connect when they have access to multiple accounts

**Current Behavior**: 
- OAuth callback automatically selects `accounts[0]` (first account) from authorization response
- User has no control over which account gets connected
- Must manually update database to switch accounts

**Proposed Solution**:
1. Detect multiple accounts in OAuth callback
2. Store account list in session
3. Redirect to account selection page
4. User chooses desired account
5. Complete connection with selected account

**Components**:

1. **Backend: Update OAuth Callback** (`web/api/views/integrations.py`)
   ```python
   # In basecamp_callback function (around line 377)
   accounts = auth_details.get("accounts", [])
   
   if len(accounts) > 1:
       # Store accounts in session for selection
       request.session['basecamp_pending_accounts'] = [
           {'id': acc['id'], 'name': acc['name']} 
           for acc in accounts
       ]
       request.session['basecamp_pending_tokens'] = {
           'access_token': access_token,
           'refresh_token': refresh_token
       }
       # Redirect to account selection page
       return redirect("http://localhost:3000/basecamp/select-account")
   else:
       # Auto-select single account (current behavior)
       account = accounts[0]
       # ... continue with existing logic
   ```

2. **Backend: Add Account Selection Endpoint** (`web/api/views/integrations.py`)
   ```python
   @api_view(['POST'])
   @permission_classes([IsAuthenticated])
   def select_basecamp_account(request):
       """Complete Basecamp OAuth with user-selected account."""
       account_id = request.data.get('account_id')
       
       # Retrieve pending data from session
       pending_accounts = request.session.get('basecamp_pending_accounts', [])
       pending_tokens = request.session.get('basecamp_pending_tokens', {})
       
       # Validate selection
       selected = next((a for a in pending_accounts if a['id'] == account_id), None)
       if not selected:
           return Response({'error': 'Invalid account selection'}, status=400)
       
       # Save tokens with selected account
       tokens = {
           'access_token': pending_tokens['access_token'],
           'refresh_token': pending_tokens['refresh_token'],
           'account_id': str(selected['id']),
           'account_name': selected['name'],
           'expires_at': None,
           'scope': '',
           'token_type': 'Bearer',
       }
       save_tokens_for_user(request.user, tokens, provider='basecamp')
       
       # Clear session
       del request.session['basecamp_pending_accounts']
       del request.session['basecamp_pending_tokens']
       
       return Response({'message': 'Account connected', 'account': selected})
   ```

3. **Frontend: Account Selection Page** (`frontend/src/app/basecamp/select-account/page.tsx`)
   ```tsx
   export default function SelectBasecampAccount() {
     const [accounts, setAccounts] = useState([]);
     const [selected, setSelected] = useState(null);
     
     const handleConnect = async () => {
       await api.post('/integrations/basecamp/select-account', {
         account_id: selected
       });
       router.push('/dashboard?basecamp=connected');
     };
     
     return (
       <div>
         <h1>Select Basecamp Account</h1>
         <p>You have access to multiple Basecamp accounts. Which one would you like to connect?</p>
         
         <RadioGroup value={selected} onChange={setSelected}>
           {accounts.map(account => (
             <Radio key={account.id} value={account.id}>
               {account.name}
             </Radio>
           ))}
         </RadioGroup>
         
         <Button onClick={handleConnect} disabled={!selected}>
           Connect Selected Account
         </Button>
       </div>
     );
   }
   ```

4. **API Route** (`web/api/urls.py`)
   ```python
   path(
       "integrations/basecamp/select-account/",
       select_basecamp_account,
       name="basecamp_select_account",
   ),
   ```

**Testing Strategy**:
- Test with account that has access to multiple Basecamp accounts
- Verify account list appears in selection UI
- Confirm selected account is stored correctly
- Verify connection with wrong account shows error

**User Experience Flow**:
1. User clicks "Connect Basecamp"
2. User authorizes app on Basecamp
3. **NEW**: If multiple accounts → Redirect to selection page
4. **NEW**: User sees list: "American Abstract LLC", "Dudley Land Company"
5. **NEW**: User selects "American Abstract LLC"
6. **NEW**: User clicks "Continue"
7. Connection completes with selected account
8. Dashboard shows "Connected to American Abstract LLC"

**Benefits**:
- ✅ User control over account selection
- ✅ Prevents connecting wrong account
- ✅ Clear indication of which account is active
- ✅ No manual database editing needed
- ✅ Better user experience

**Edge Cases**:
- Session expires before selection → Show error, restart OAuth flow
- User closes selection page → Session data remains, can return to selection
- Only one account available → Auto-select (no change from current behavior)

**Estimated Time**: 1-2 days

**Priority**: Optional - Current workaround (manual database update) works but this provides better UX

---

### Phase 1: Extend Basecamp API Service ⭐ *Currently In Progress*

**Goal**: Add methods to interact with Basecamp projects, to-do lists, and tasks

**Location**: `web/integrations/basecamp/basecamp_service.py`

**New Methods Needed**:
- List all projects for an account
- Get specific project details
- Create to-do list within a project
- Create to-do (task) within a to-do list
- Update existing to-do
- Add comments/notes to tasks

**Resources**: 
- [Basecamp 3 API Documentation](https://github.com/basecamp/bc3-api)
- Follow existing pattern in `basecamp_service.py`

**Testing Strategy**:
- Test each method manually in Django shell
- Use your actual Basecamp account for testing
- Verify tasks appear correctly in Basecamp UI

**Status**: ✅ **Completed** (specs/004-basecamp-project-api/)

**Estimated Time**: 1-2 days

---

### Phase 2: Hardcoded Workflow Proof of Concept

**Goal**: Create working workflows that generate Basecamp tasks from Orders for all 4 product types (no templates yet)

**Why This Step?**: Validates the integration works end-to-end before investing in template system complexity

---

#### Understanding the Two Workflow Patterns

The system supports **4 product types** across **2 distinct workflow patterns**:

##### Pattern A: Runsheet Workflows (Lease-Centric)

**Products**: Federal Runsheets (BLM), State Runsheets (NMSLO)

**Structure**:
- **1 to-do list per ORDER**: "Order 1946 - 20251023"
- **1 to-do per LEASE**: "NMNM 110339" or "NMNM 110339 - Previous Report"
- **No groups** within to-do list
- **Naming suffix**: "Previous Report" only if `lease.runsheet_report_found = True`

**Example Basecamp Structure**:
```
📋 To-do List: "Order 1946 - 20251023"
  └─ Delivery Link: https://dropbox.com/...
  
  ✓ NMNM 110339 - Previous Report
    └─ Legal Description: 22S-25E, Sec. 13-Lots 1, 4
    └─ Lease Data: https://dropbox.com/runsheet_archive
  
  □ NMNM 112898 - Previous Report
  □ NMNM 106965 - Previous Report
```

**Business Logic**:
```python
# Filter: Reports where report_type='RUNSHEET' AND leases.agency='BLM' (or 'NMSLO')
# One to-do list per order
# One to-do per lease with that agency
```

---

##### Pattern B: Abstract Workflows (Report-Centric, Grouped by Department)

**Products**: Federal Abstracts (BLM), State Abstracts (NMSLO)

**Structure**:
- **1 to-do list per REPORT** (not per order): "Order 1765- Base Abstract 4793 - 20250715"
- **Fixed workflow steps** (not per lease): Setup → Workup → Imaging → Indexing → Assembly → Delivery
- **Grouped by department**: Each phase is a Basecamp group
- **Some steps repeat per lease**: e.g., "Create Abstract Worksheet NMNM 0467934"

**Example Basecamp Structure**:
```
📋 To-do List: "Order 1765- Base Abstract 4793 - 20250715"
  └─ Type: Base
  └─ Dates: Inception
  └─ Leases: NMNM 0467934, NMNM 0558581
  └─ Lands: 17S-30E, Sec. 33-NE
  └─ Delivery Link: https://dropbox.com/...
  
  📁 Setup
    □ Setup Abstract Todos
  
  📁 Workup
    □ Workup - See Abstract 4794
    □ Microfilm SRP - See Abstract 4794
  
  📁 Imaging
    □ Unfiled Documents - See Abstract 4794
    □ Imaging - See Abstract 4794
  
  📁 Indexing
    □ File Index - See Abstract 4794
    □ File Index NMLC 0028936A
    □ Create Abstract Worksheet NMNM 0467934
    □ Create Abstract Worksheet NMNM 0558581
    □ Review Abstract Worksheet NMNM 0467934
    □ Review Abstract Worksheet NMNM 0558581
  
  📁 Assembly
    □ Assemble Abstract
    □ Review Abstract
  
  📁 Delivery
    □ Deliver Base Abstract
```

**Business Logic**:
```python
# Filter: Reports where report_type='BASE_ABSTRACT' AND leases.agency='BLM' (or 'NMSLO')
# One to-do list per report (not per order)
# Fixed workflow steps with some steps duplicated per lease
# Steps organized into department groups (Setup, Workup, Imaging, etc.)
```

---

#### Multi-Product Orders

**Key Requirement**: A single order may contain multiple product types simultaneously.

**Example Order**:
- 2 Federal Runsheet reports (BLM agency)
- 1 Federal Abstract report (BLM agency)
- 1 State Runsheet report (NMSLO agency)

**Expected Basecamp Result**:
- Creates to-do list in **Federal Runsheets** project (1 list for all BLM runsheet leases)
- Creates to-do list in **Federal Abstracts** project (1 list for the abstract report)
- Creates to-do list in **State Runsheets** project (1 list for all NMSLO runsheet leases)

**Total**: 3 to-do lists across 3 different Basecamp projects from 1 order

---

#### Architecture Recommendation: Strategy Pattern

Given the fundamentally different structures (lease-centric vs. report-centric, grouped vs. flat), recommend implementing:

**1. Abstract Strategy Interface**:
```python
class WorkflowStrategy:
    def should_create_workflow(order) -> bool
    def create_workflow(order) -> dict
```

**2. Two Concrete Strategies**:
- `RunsheetWorkflowStrategy`: Implements Pattern A
- `AbstractWorkflowStrategy`: Implements Pattern B (with group creation)

**3. Configuration-Driven Product Mapping**:
```python
PRODUCT_CONFIGS = {
    'federal_runsheets': {
        'strategy': RunsheetWorkflowStrategy,
        'project_id_key': 'federal_runsheets',
        'agency': 'BLM',
    },
    'federal_abstracts': {
        'strategy': AbstractWorkflowStrategy,
        'project_id_key': 'federal_abstracts',
        'agency': 'BLM',
    },
    # ... etc
}
```

**Benefits**:
- ✅ DRY: No duplicated logic between similar products (Federal/State Runsheets share strategy)
- ✅ SOLID: Open/Closed Principle - add new products by adding config, not code
- ✅ Maintainable: Workflow changes isolated to one strategy class
- ✅ Testable: Each strategy independently testable

---

#### Components to Build

1. **Workflow Service** (`web/orders/services/basecamp_workflow.py`)
   - Strategy classes: `RunsheetWorkflowStrategy`, `AbstractWorkflowStrategy`
   - Product configuration dictionary
   - Executor class that delegates to appropriate strategy
   - Public API: `create_workflow_for_order(order_id, user, product_key)`
   - Public API: `create_all_workflows_for_order(order_id, user)` (creates all applicable)

2. **Configuration** (`web/order_manager_project/settings.py`)
   ```python
   BASECAMP_PROJECT_IDS = {
       'federal_runsheets': os.getenv('BASECAMP_PROJECT_IDS__FEDERAL_RUNSHEETS'),
       'federal_abstracts': os.getenv('BASECAMP_PROJECT_IDS__FEDERAL_ABSTRACTS'),
       'state_runsheets': os.getenv('BASECAMP_PROJECT_IDS__STATE_RUNSHEETS'),
       'state_abstracts': os.getenv('BASECAMP_PROJECT_IDS__STATE_ABSTRACTS'),
   }
   ```

3. **API Endpoint** (`web/api/views/orders.py`)
   ```python
   POST /api/orders/{order_id}/create-basecamp-workflow/
   
   Body (optional):
   {
       "product": "federal_runsheets",  // Create specific product
       "all": false                      // Or create all applicable
   }
   
   # Default: creates all applicable workflows
   ```

4. **Frontend Button** (`frontend/src/app/orders/[id]/page.tsx`)
   - "Push to Basecamp" button on order details page
   - Calls API with no body (creates all applicable workflows)
   - Shows success toast: "Workflows created: Federal Runsheets, Federal Abstracts"
   - Optionally displays links to created to-do lists

---

#### Data Model Relationships

**Filtering Logic**:
```python
# For Federal Runsheets:
reports = order.reports.filter(
    report_type='RUNSHEET',
    leases__agency='BLM'
).distinct()

# For Federal Abstracts:
reports = order.reports.filter(
    report_type='BASE_ABSTRACT',
    leases__agency='BLM'
).distinct()
```

**Key Fields**:
- `Order.order_number` - Used in to-do list name
- `Order.order_date` - Used in to-do list name (format: YYYYMMDD)
- `Order.delivery_link` - Attached to to-do list description
- `Report.report_type` - Filter criterion (RUNSHEET vs BASE_ABSTRACT)
- `Report.legal_description` - Used in to-do descriptions
- `Lease.agency` - Filter criterion (BLM vs NMSLO)
- `Lease.lease_number` - Used in to-do names
- `Lease.runsheet_report_found` - Determines "Previous Report" suffix
- `Lease.runsheet_archive_link` - Added to runsheet to-do descriptions

---

#### Testing Strategy

**Phase 2a: Test Federal Runsheets First**:
1. Create test order with BLM runsheet reports
2. Call `create_workflow_for_order(order_id, user, 'federal_runsheets')`
3. Verify to-do list created in Federal Runsheets project
4. Verify one to-do per BLM lease
5. Verify "Previous Report" suffix logic works

**Phase 2b: Test Federal Abstracts**:
1. Create test order with BLM abstract reports
2. Call `create_workflow_for_order(order_id, user, 'federal_abstracts')`
3. Verify one to-do list per report
4. Verify all workflow steps created
5. Verify groups created (Setup, Workup, etc.)
6. Verify lease-specific steps duplicated correctly

**Phase 2c: Test Multi-Product Order**:
1. Create order with both runsheets and abstracts (BLM and NMSLO)
2. Call `create_all_workflows_for_order(order_id, user)`
3. Verify workflows created in all 4 projects
4. Verify each workflow follows correct pattern

**Phase 2d: Frontend Integration**:
1. Add "Push to Basecamp" button to order details page
2. Test button creates all applicable workflows
3. Verify success/error messages display correctly

---

#### Edge Cases to Handle

1. **Order with no applicable reports**: Return success=False, message="No workflows to create"
2. **Missing project ID configuration**: Return clear error about missing env var
3. **Basecamp API failures**: Log error, continue with other products, return partial success
4. **Duplicate to-do list names**: Basecamp allows duplicates, but BasecampService already prevents this
5. **Empty legal descriptions or missing links**: Handle gracefully (empty strings)

---

#### Success Criteria

- ✅ "Push to Basecamp" button creates workflows for all 4 product types
- ✅ Runsheet workflows match expected structure (1 list per order, to-dos per lease)
- ✅ Abstract workflows match expected structure (1 list per report, grouped steps)
- ✅ Multi-product orders create multiple to-do lists in correct projects
- ✅ All to-dos contain correct data (legal descriptions, links, lease numbers)
- ✅ Error handling provides clear feedback to users
- ✅ Code follows SOLID/DRY principles

---

#### Estimated Time

- **Phase 2a (Federal Runsheets)**: 1-2 days
- **Phase 2b (Federal Abstracts)**: 2-3 days (more complex with groups)
- **Phase 2c (Multi-Product + State products)**: 1 day (reuse strategies)
- **Phase 2d (Frontend Integration)**: 0.5 days
- **Testing & Polish**: 1 day

**Total**: 5-7 days

---

#### Deliverable

Working "Push to Basecamp" feature that:
1. Detects which product types are present in an order
2. Creates appropriate workflows in correct Basecamp projects
3. Handles both simple (runsheet) and complex (abstract with groups) workflows
4. Provides clear feedback on success/failure
5. Serves as foundation for Phase 3 template system (if needed)

---

### Phase 3: Database-Driven Template System

**Goal**: Replace hardcoded workflow with configurable templates managed through Django Admin

#### Step 3a: Create Template Models

**Location**: `web/integrations/models.py`

**New Models**:

1. **WorkflowTemplate**
   - Name and description
   - Active status flag
   - Ordering for multiple templates
   
2. **TaskTemplate**
   - Belongs to a workflow template
   - Name template (supports Django template variables like `{{order.order_number}}`)
   - Description template
   - Field mappings for assignee and due date
   - Ordering within workflow
   
3. **SubtaskTemplate** (optional)
   - Belongs to a task template
   - Name template
   - Conditional creation logic (only create if field matches value)
   - Ordering within task
   
4. **NoteTemplate** (optional)
   - Belongs to task or workflow
   - Content template for adding notes/links

**Migration**: Generate and apply Django migrations

**Estimated Time**: 1 day

---

#### Step 3b: Template Processor

**Location**: `web/integrations/basecamp/template_processor.py`

**Purpose**: Converts template + order data into structured data ready for API calls

**Functionality**:
- Build Django template context from Order object (includes related reports, leases)
- Render template strings (e.g., `"Order {{order.order_number}}"` → `"Order 1943"`)
- Evaluate conditional logic (should subtask be created?)
- Map field names to actual values (e.g., `assigned_to_field="project_manager"` → user ID)
- Return structured dict with all processed data

**Key Design Decision**: Use Django's built-in template engine for variable replacement

**Estimated Time**: 2 days

---

#### Step 3c: Workflow Executor

**Location**: `web/integrations/basecamp/workflow_executor.py`

**Purpose**: Takes processed template data and makes actual Basecamp API calls

**Functionality**:
- Create to-do list
- Iterate through tasks and create each one
- Create subtasks for each task
- Add comments/notes
- Handle API errors gracefully
- Log execution results

**Error Handling**: 
- Wrap API calls in try/except
- Log failures without stopping entire workflow
- Return detailed execution report

**Estimated Time**: 2 days

---

#### Step 3d: Update Workflow Service

**Location**: `web/orders/services/basecamp_workflow.py`

**Changes**:
- Accept template ID parameter (or use default)
- Fetch template from database
- Instantiate TemplateProcessor
- Process template with order data
- Instantiate WorkflowExecutor with BasecampService
- Execute processed workflow
- Return execution report

**Estimated Time**: 1 day

---

#### Step 3e: Django Admin Interface

**Location**: `web/integrations/admin.py`

**Purpose**: Allow business users to create and edit workflow templates

**Admin Features**:
- List view of all templates (with active status)
- Inline editing for tasks within workflow
- Inline editing for subtasks within tasks
- Preview functionality (optional: render template with sample data)
- Duplicate template functionality (optional)

**UX Considerations**:
- Use StackedInline for better readability
- Add help text for template variable syntax
- Consider using django-admin-sortable for drag-and-drop ordering

**Estimated Time**: 1-2 days

---

#### Step 3f: Audit Log (Optional)

**Location**: `web/integrations/models.py`

**New Model**: `WorkflowExecution`
- Links to Order and WorkflowTemplate
- Timestamp
- User who triggered it
- Success/failure status
- JSON field with execution details
- Basecamp to-do list URL

**Purpose**: Track which workflows were created and troubleshoot failures

**Estimated Time**: 1 day

---

**Phase 3 Total Time**: 7-10 days

---

## Quick Win Strategy

For fastest time-to-value:

### Week 1: Core API ✅ **Phase 1 Complete**
- Days 1-2: ✅ Implement Phase 1 (API methods)
- Phase 1 Status: Complete and tested

### Week 2: Hardcoded Workflows (Phase 2) - Ready to Start
- Days 1-2: Implement Federal Runsheets (simple pattern)
- Days 3-5: Implement Federal Abstracts (complex pattern with groups)
- Days 6-7: Extend to State products + frontend integration
- End of Week 2: Working "Push to Basecamp" feature for all 4 product types

### Week 3+: Template System (Phase 3 - Optional)
- Only proceed if workflows need frequent changes
- Phase 2's Strategy pattern may be sufficient for stable workflows
- Can defer until business need is validated

### Optional: OAuth Account Selection
- 1-2 days to implement Phase 0
- Can be done anytime (independent of other phases)
- Improves UX but not blocking

---

## Decision Points

### After Phase 0 (Optional)
**Question**: Do users need to choose between multiple Basecamp accounts?
- ✅ Yes → Implement Phase 0 for account selection
- ❌ No, single account or manual selection is fine → Skip Phase 0

### After Phase 1
**Question**: Do the API methods work correctly?
- ✅ Yes → Proceed to Phase 2
- ❌ No → Debug API integration, review Basecamp docs

### After Phase 2
**Question**: Do the hardcoded workflows (with Strategy pattern) meet business needs?
- ✅ Yes, and workflows are stable → **Stop here** (Phase 2 is production-ready)
- ⚠️ Yes, but workflow steps change frequently → Consider Phase 3 templates
- ⚠️ Yes, but need to add new product types often → Strategy pattern handles this (stay in Phase 2)
- ❌ No, workflow structure is wrong → Iterate on strategies before adding complexity

**Note**: Phase 2 now uses Strategy pattern, making it production-quality. Phase 3 templates add complexity that may not be needed if workflows are relatively stable.

### During Phase 3
**Question**: What template features are essential vs. nice-to-have?
- **Essential**: WorkflowTemplate, TaskTemplate, basic variable replacement
- **Nice-to-Have**: SubtaskTemplates, conditional logic, audit logs
- **Can Add Later**: Preview mode, duplicate templates, advanced field mappings

---

## Technical Considerations

### Template Variable Syntax
Use Django template syntax: `{{variable}}`, `{{object.field}}`, `{{object.related.field}}`

### Available Context Variables
Based on your Order model:
- `order.order_number`
- `order.order_date`
- `order.delivery_link`
- `reports` (list of reports)
- `leases` (via reports)

### Assignee Mapping Strategy
Options:
1. Store Basecamp user IDs directly in templates (brittle)
2. Map Django User to Basecamp user (requires lookup table)
3. Store field name (e.g., "project_manager") and add field to Order model

**Recommendation**: Option 3 for flexibility

### Error Handling Philosophy
- **Template Processing Errors**: Fail fast, show error in admin preview
- **API Call Errors**: Log but continue, return partial success report
- **Missing Data**: Use fallback defaults (empty assignee, no due date)

---

## Testing Strategy

### Phase 1 Testing
```bash
python manage.py shell
# Test each BasecampService method manually
```

### Phase 2 Testing
- Create test orders via Django admin
- Call workflow creation API
- Verify in Basecamp UI

### Phase 3 Testing
- Create templates via Django admin
- Process template with test order (unit test)
- Execute full workflow (integration test)
- Verify output matches expectations

---

## Success Metrics

### Phase 1 Success
- All API methods successfully create/retrieve Basecamp data
- Error handling works for API failures
- Rate limiting handled gracefully

### Phase 2 Success
- Single button click creates full workflow in Basecamp
- All expected tasks, subtasks, and links appear correctly
- Assignees and due dates populated from order data

### Phase 3 Success
- Non-technical users can create workflow templates via Django Admin
- Template changes take effect immediately (no code deployment)
- Templates render correctly with different order data
- Audit trail shows execution history

---

## Future Enhancements (Out of Scope)

- Bidirectional sync (update order when Basecamp tasks change)
- Automatic workflow creation on order creation (signal-based)
- Multiple templates per order type
- Template versioning and rollback
- Bulk workflow creation for multiple orders
- Integration with Basecamp schedule/milestones
- File uploads from Dropbox links to Basecamp

---

## Resources

- **Basecamp 3 API**: https://github.com/basecamp/bc3-api
- **Django Template Engine**: https://docs.djangoproject.com/en/stable/ref/templates/language/
- **Existing Integration Pattern**: See `web/integrations/dropbox/` for reference
- **Project Specs**: `/specs/003-basecamp-integration/`

---

## Questions to Clarify Before Starting

1. **Basecamp Project Selection**: How do users select which Basecamp project to use?
   - Manual input each time?
   - Stored in Order model?
   - Configured per order type?

2. **Assignee Mapping**: How are Django users mapped to Basecamp users?
   - Manual ID entry in templates?
   - Lookup table?
   - Order field references?

3. **Template Scope**: One universal template or multiple templates per order type?

4. **Timing**: When should workflows be created?
   - Manual button click?
   - Automatic on order status change?
   - Scheduled/batch creation?

5. **Error Handling**: If workflow creation fails, should it retry automatically?

---

## Recommendation

**Phase 1 is now complete!** ✅ You can successfully create projects, to-do lists, tasks, groups, and comments via `BasecampService`. The integration is solid and tested with the American Abstract LLC account.

**Next Steps**:

1. **Phase 2 (Recommended Next)**: Implement hardcoded workflows using Strategy pattern
   - Start with Federal Runsheets (simplest pattern)
   - Validate end-to-end workflow creation
   - Add Federal Abstracts (complex pattern with groups)
   - Extend to State products (reuse strategies)
   - Estimated: 5-7 days

2. **Phase 3 (Future)**: Build database-driven template system
   - Only needed if workflows change frequently
   - Phase 2's Strategy pattern may be sufficient for stable workflows
   - Can defer until business need is proven

3. **Phase 0 (Optional)**: Add OAuth account selection UI
   - Improves UX but not blocking
   - Can be implemented anytime (1-2 days)
   - Independent of workflow functionality

**Important Discovery**: Your workflows have **two fundamentally different patterns** (Runsheet vs Abstract). Phase 2 now accounts for this with a Strategy pattern approach that handles:
- Runsheet workflows: Lease-centric, flat structure
- Abstract workflows: Report-centric, grouped by department, more complex

The Strategy pattern gives you SOLID/DRY code while supporting both patterns cleanly. Phase 3's template system may not be necessary if the workflows remain relatively stable.

