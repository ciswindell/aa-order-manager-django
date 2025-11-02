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

## Commit Status

Changes committed in: `feat: Implement Federal Runsheet workflow automation (Phase 3)` (d794da0)

This correction document will be included in next commit as supplementary documentation.

