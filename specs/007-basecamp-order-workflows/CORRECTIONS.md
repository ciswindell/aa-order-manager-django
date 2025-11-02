# Phase 3 Corrections - Federal Runsheet Workflow

**Date**: 2025-11-02  
**Status**: ✅ COMPLETED

## Issue Description

The initial Phase 3 implementation had incorrect behavior for handling multiple reports with the same lease:

### Previous (Incorrect) Behavior
- Created 1 to-do per **report**
- Each to-do only showed its own legal description
- Label was "Legal Description:" instead of "Reports Needed:"
- Archive link labeled "Archive:" instead of "Lease Data:"

### Corrected Behavior
- Creates 1 to-do per **unique lease** (groups reports by lease number)
- Each to-do lists ALL legal descriptions from reports sharing that lease
- "Reports Needed:" section with bulleted list
- "Lease Data:" section with archive link

## Example

**Order with 2 Federal Runsheet Reports**:
- Report 1: Lease NMNM 11111, Legal Desc: "Sec 1: N2"
- Report 2: Lease NMNM 11111, Legal Desc: "Sec 17: NW, S2"

**Creates**:
```
✅ ONE to-do: "NMNM 11111 - Previous Report"

Description:
Reports Needed:
- Sec 1: N2
- Sec 17: NW, S2

Lease Data: https://www.dropbox.com/...
```

## Technical Changes

### File: `web/orders/services/workflow/strategies/runsheet.py`

#### 1. Replaced `_extract_leases()` with `_group_reports_by_lease()`

**Before**: Returned flat list of unique Lease objects, losing report associations
```python
def _extract_leases(self, reports, agency) -> list:
    # Returned deduplicated lease list
    # Lost information about which reports reference each lease
```

**After**: Returns dictionary mapping lease_number → (reports_list, lease_object)
```python
def _group_reports_by_lease(self, reports, agency) -> dict[str, tuple[list["Report"], "Lease"]]:
    # Groups reports by lease number
    # Preserves all reports that reference each lease
    # Example: {"NMNM 11111": ([report1, report2], lease_obj)}
```

#### 2. Updated `create_workflow()` Method

**Changes**:
- Line 54: Call `_group_reports_by_lease()` instead of `_extract_leases()`
- Line 72: Pass `grouped_reports` to `_create_todos()`
- Line 83: Count uses `len(grouped_reports)` (unique leases, not total leases)

#### 3. Rewrote `_create_todos()` Method

**Before**: 
- Accepted `leases: list` parameter
- Used first report's legal description for all to-dos
- Labels: "Legal Description:" and "Archive:"

**After**:
- Accepts `grouped_reports: dict[str, tuple[list["Report"], "Lease"]]` parameter
- Iterates over grouped reports by lease number
- For each unique lease:
  - Collects ALL legal descriptions from reports
  - Builds "Reports Needed:" section with bullet points
  - Adds "Lease Data:" section with archive link
  - Proper formatting with blank line between sections

**Description Format**:
```
Reports Needed:
- [legal description from report 1]
- [legal description from report 2]
- [legal description from report N]

Lease Data: [archive link]
```

## Testing Checklist

After correction:
- ✅ Order with 2 reports, same lease → 1 to-do with 2 legal descriptions
- ✅ Order with 2 reports, different leases → 2 to-dos, each with 1 legal description
- ✅ "Reports Needed:" label appears correctly
- ✅ "Lease Data:" label appears (not "Archive:")
- ✅ Archive link is optional (handles null gracefully)
- ✅ Legal descriptions shown as bulleted list
- ✅ Blank line between sections for readability

## Verification

```bash
# Django check passes
docker compose exec web python3 manage.py check
# System check identified no issues (0 silenced).

# No linter errors
# PEP 8 compliant
```

## Key Insight

**Important Database Relationship**: 
- Runsheet reports are 1:1 with leases (never multiple leases per report)
- BUT multiple reports can reference the same lease
- Therefore, grouping at the workflow level is necessary to create 1 to-do per unique lease with all related reports' legal descriptions

---

## Correction 2: Date Range Formatting (2025-11-02)

### Issue Description

Legal descriptions in the "Reports Needed:" section were not including date ranges from the report's `start_date` and `end_date` fields.

### Corrected Behavior

Each report's legal description now includes date ranges following these rules:

| Condition | Format | Example |
|-----------|--------|---------|
| Both dates present | `{desc} from M/D/YYYY to M/D/YYYY` | `Sec 1: N2 from 1/1/1979 to 2/2/1988` |
| No dates | `{desc}` | `Sec 1: N2` |
| Only start date | `{desc} from M/D/YYYY to present` | `Sec 1: N2 from 1/1/1979 to present` |
| Only end date | `{desc} from inception to M/D/YYYY` | `Sec 1: N2 from inception to 2/2/1988` |

**Date Format**: `M/D/YYYY` (no zero-padding, e.g., `1/1/1979` not `01/01/1979`)

### Technical Implementation

#### Created Shared Utility Module

**File**: `web/orders/services/workflow/utils.py`

```python
def format_report_description(report: "Report") -> str:
    """
    Format report legal description with date range.
    Handles all 4 cases: both dates, no dates, only start, only end.
    """
    # Implementation with conditional date range formatting
```

**Why Shared**: This formatting logic is used across all 4 product types (Federal/State × Runsheets/Abstracts), following DRY principles.

#### Updated RunsheetWorkflowStrategy

**File**: `web/orders/services/workflow/strategies/runsheet.py`

**Changes**:
- Line 8: Import `format_report_description` utility
- Line 235-236: Use `format_report_description(report)` instead of raw `report.legal_description`
- Lines 201-206: Updated docstring with date range examples

**Example Output**:
```
Reports Needed:
- Sec 1: N2 from 1/1/1979 to 2/2/1988
- Sec 17: NW, S2 from 3/15/1985 to present

Lease Data: https://www.dropbox.com/...
```

### Reusability

The `format_report_description()` utility will be used by:
- ✅ RunsheetWorkflowStrategy (Federal & State)
- 🔜 AbstractWorkflowStrategy (Federal & State) - Phase 4+

### Verification

```bash
# Django check passes
docker compose exec web python3 manage.py check
# System check identified no issues (0 silenced).

# No linter errors
# PEP 8 compliant
```

---

## Correction 3: HTML Formatting for Basecamp Descriptions (2025-11-02)

### Issue Description

To-do descriptions were using plain text formatting, which doesn't render well in Basecamp. Basecamp supports HTML, which provides better visual structure with bold headers, bulleted lists, and clickable links.

### Corrected Behavior

To-do descriptions now use HTML formatting for improved readability:

**Before (Plain Text)**:
```
Reports Needed:
- Sec 1: N2 from 1/1/1979 to 2/2/1988
- Sec 17: NW, S2 from 3/15/1985 to present

Lease Data: https://www.dropbox.com/...
```

**After (HTML)**:
```html
<strong>Reports Needed:</strong>
<ul>
  <li>Sec 1: N2 from <strong>1/1/1979</strong> to <strong>2/2/1988</strong></li>
  <li>Sec 17: NW, S2 from <strong>3/15/1985</strong> to <strong>present</strong></li>
</ul>
<strong>Lease Data:</strong> <a href="https://www.dropbox.com/...">https://www.dropbox.com/...</a>
```

**Benefits**:
- ✅ Bold section headers ("Reports Needed:", "Lease Data:")
- ✅ Proper bulleted list formatting
- ✅ Bold dates for emphasis
- ✅ Clickable archive links
- ✅ Better visual hierarchy in Basecamp UI

### Technical Implementation

#### Updated Utility Module

**File**: `web/orders/services/workflow/utils.py`

**Added Function**:
```python
def format_report_description_html(report: "Report") -> str:
    """
    Format report legal description with date range as HTML.
    Uses <strong> tags to emphasize dates.
    """
    # Implementation with HTML date formatting
```

**Why Both Plain Text and HTML?**
- `format_report_description()` - Plain text version (kept for backward compatibility)
- `format_report_description_html()` - HTML version (used by all workflows)

#### Updated RunsheetWorkflowStrategy

**File**: `web/orders/services/workflow/strategies/runsheet.py`

**Changes**:
- Line 8: Import `format_report_description_html` instead of plain text version
- Lines 230-249: Build HTML description with:
  - `<strong>` tags for section headers
  - `<ul>` and `<li>` tags for bulleted lists
  - `<a>` tags for clickable archive links
  - No line breaks needed (HTML handles formatting)
- Lines 201-207: Updated docstring with HTML format example

**HTML Structure**:
```python
html_parts = []
html_parts.append("<strong>Reports Needed:</strong>")
html_parts.append("<ul>")
for report in reports_for_lease:
    formatted_desc = format_report_description_html(report)
    html_parts.append(f"<li>{formatted_desc}</li>")
html_parts.append("</ul>")
html_parts.append(f'<strong>Lease Data:</strong> <a href="{url}">{url}</a>')
description = "".join(html_parts)
```

### Reusability

The HTML formatting will be used by **all 4 product types**:
- ✅ Federal Runsheets (Phase 3)
- ✅ State Runsheets (Phase 5)
- 🔜 Federal Abstracts (Phase 4) - will use HTML formatting
- 🔜 State Abstracts (Phase 6) - will use HTML formatting

### Verification

```bash
# Django check passes
docker compose exec web python3 manage.py check
# System check identified no issues (0 silenced).

# No linter errors
# PEP 8 compliant
```

### Expected Basecamp Rendering

In Basecamp, the HTML will render as:

**Reports Needed:**
• Sec 1: N2 from **1/1/1979** to **2/2/1988**
• Sec 17: NW, S2 from **3/15/1985** to **present**

**Lease Data:** [clickable link]

---

## Commit Status

Initial changes committed in: `feat: Implement Federal Runsheet workflow automation (Phase 3)` (d794da0)

Corrections 1, 2, & 3 pending commit.

