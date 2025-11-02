# Research: Integration Account Names Display

**Date**: November 2, 2025  
**Feature**: Integration Account Names Display  
**Purpose**: Document technical decisions and research findings

## Research Questions

### Q1: How to fetch Dropbox account information during OAuth?

**Decision**: Use `dbx.users_get_current_account()` from Dropbox SDK

**Rationale**:
- Already using Dropbox SDK in OAuth callback for token exchange
- `users_get_current_account()` returns `FullAccount` with `name` (DisplayNameDetails) and `email`
- Synchronous call during OAuth flow is acceptable (user is waiting for redirect anyway)
- Returns structured data: `name.display_name` (string) and `email` (string)

**Implementation**:
```python
# In dropbox_callback after token exchange
dbx = dropbox.Dropbox(oauth2_access_token=result.access_token)
account_info = dbx.users_get_current_account()
display_name = account_info.name.display_name  # e.g., "Chris Windell"
email = account_info.email  # e.g., "chris@example.com"
```

**Error Handling**: Retry once after 2 seconds (per clarifications), then save connection without account info if still failing.

---

### Q2: How to add fields to existing Django model without data loss?

**Decision**: Create standard Django migration with nullable fields initially, no default values needed

**Rationale**:
- Existing `DropboxAccount` records will have `NULL` for new fields (acceptable - shows generic "Connected")
- No backfill needed - users reconnect naturally to populate data
- Migration is reversible and safe

**Migration Strategy**:
```python
# migrations/000X_add_dropbox_account_info.py
operations = [
    migrations.AddField(
        model_name='dropboxaccount',
        name='display_name',
        field=models.CharField(max_length=255, blank=True, default=''),
    ),
    migrations.AddField(
        model_name='dropboxaccount',
        name='email',
        field=models.EmailField(blank=True, default=''),
    ),
]
```

---

### Q3: How to mask PII in logs while maintaining debuggability?

**Decision**: Create utility function to mask middle characters of names/emails

**Rationale**:
- Preserves enough info for debugging (first/last chars, domain)
- Simple regex-based approach works for most cases
- No external dependencies needed

**Masking Pattern**:
- Email: `chris@example.com` → `ch***@ex***.com`
- Name: `American Abstract LLC` → `Am***an Ab***ct LLC` (mask middle of each word >3 chars)

**Implementation Location**: `web/integrations/utils/log_masking.py` (new file)

---

### Q4: Best practice for displaying long text with ellipsis and hover tooltip?

**Decision**: Use CSS `text-overflow: ellipsis` with `title` attribute for full text on hover

**Rationale**:
- Native browser behavior (no JavaScript required)
- Works across all browsers
- Accessible (screen readers read full title)
- Simple to implement and maintain

**CSS Approach**:
```css
.account-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: [calculated from 50 char limit];
}
```

**HTML Approach**:
```tsx
<span className="account-name" title={fullAccountName}>
  {truncatedAccountName}
</span>
```

**Alternative Considered**: Third-party tooltip library (Radix UI Tooltip) - Rejected as overkill for simple hover text.

---

### Q5: Where to add account_name/connected_at to IntegrationStatus?

**Decision**: Extend `IntegrationStatus` DTO in `web/integrations/status/dto.py` and modify strategies

**Rationale**:
- DTO already exists and is used by all integration strategies
- Clean separation of concerns (data structure vs. strategy implementation)
- Serializer automatically handles new fields via DRF introspection

**Changes Required**:
1. Update `@dataclass IntegrationStatus` in `dto.py`
2. Update `BasecampStatusStrategy.assess()` to populate `account_name`
3. Update `DropboxStatusStrategy.assess()` to populate `account_name` and `account_email`
4. Extend `IntegrationStatusSerializer` to include new fields

---

### Q6: How to format connection dates in user-friendly way?

**Decision**: Use `date-fns` library's `format()` function with pattern `"MMM d, yyyy"` (e.g., "Nov 2, 2025")

**Rationale**:
- `date-fns` already in use in frontend (`format` used in existing integrations page for last_sync)
- Lightweight, tree-shakeable alternative to moment.js
- Pattern `"MMM d, yyyy"` matches existing date display patterns in the app
- Locale-aware formatting available if needed later

**Implementation**:
```typescript
import { format } from 'date-fns';
const formattedDate = format(new Date(integration.connected_at), 'MMM d, yyyy');
```

---

## Technology Decisions Summary

| Component | Technology | Reason |
|-----------|------------|--------|
| Dropbox account fetch | `users_get_current_account()` | Official SDK method, returns structured data |
| Database migration | Django migrations | Standard Django approach, reversible |
| PII masking | Custom regex utility | Simple, no dependencies, sufficient for debugging |
| UI truncation | CSS `text-overflow` + `title` | Native, accessible, no JS required |
| Date formatting | date-fns `format()` | Already in use, lightweight, locale-aware |
| DTO extension | Modify existing `IntegrationStatus` | Clean, follows existing patterns |

---

## Dependencies

**New Dependencies**: None  
**Modified Files**: 9 files (5 backend, 2 frontend, 2 specs)  
**Database Changes**: 1 migration (add 2 fields to existing table)

---

## Implementation Sequencing

**Recommended Order**:
1. **US1 (Basecamp)** - No migration needed, quick win
   - Backend: Extend status strategy
   - Frontend: Display account_name
2. **US2 (Dropbox)** - Requires migration
   - Database: Run migration
   - Backend: Fetch account info in OAuth, extend status strategy
   - Frontend: Display name and email
3. **US3 (Timestamps)** - Optional enhancement
   - Backend: Add connected_at to DTO
   - Frontend: Display formatted date

This allows incremental delivery with P1 providing immediate value while P2 progresses through migration and testing.

