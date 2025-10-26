# API Specification: Order Details Page Enhancement

**Feature**: 002-order-details-page  
**Created**: October 26, 2025  
**Purpose**: Define REST API contracts for order details functionality

---

## Overview

This feature primarily leverages existing API endpoints with potential query parameter additions. No new endpoints are required; we verify and potentially enhance existing ones.

**Base URL**: `http://localhost:8000` (development)  
**API Prefix**: `/api/`  
**Authentication**: JWT tokens via HTTP-only cookies  
**Content-Type**: `application/json`

---

## Endpoints

### 1. Get Single Order

**Purpose**: Retrieve complete details for a specific order

```
GET /api/orders/{id}/
```

**Path Parameters**:
| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| id        | integer | Yes     | Order ID    |

**Request Headers**:
```
Cookie: access_token={jwt_token}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "order_number": "ORD-2025-001",
  "order_date": "2025-10-15",
  "order_notes": "Special handling required",
  "delivery_link": "https://dropbox.com/folder/...",
  "report_count": 3,
  "created_at": "2025-10-15T10:30:00Z",
  "created_by": 1,
  "created_by_username": "jdoe",
  "updated_at": "2025-10-20T14:45:00Z",
  "updated_by": 2,
  "updated_by_username": "asmith"
}
```

**Error Responses**:

`404 Not Found` - Order does not exist
```json
{
  "detail": "Not found."
}
```

`401 Unauthorized` - Missing or invalid authentication
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Status**: ✅ Exists (verify implementation)

---

### 2. Get Reports by Order

**Purpose**: Retrieve all reports associated with a specific order

```
GET /api/reports/?order_id={order_id}
```

**Query Parameters**:
| Parameter | Type    | Required | Description                  |
|-----------|---------|----------|------------------------------|
| order_id  | integer | Yes      | Filter reports by order ID   |
| page      | integer | No       | Page number (default: 1)     |
| page_size | integer | No       | Results per page (default: 20) |

**Request Headers**:
```
Cookie: access_token={jwt_token}
```

**Response**: 200 OK
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 10,
      "order": {
        "id": 1,
        "order_number": "ORD-2025-001"
      },
      "report_type": "RUNSHEET",
      "legal_description": "Section 16, Township 10N, Range 5E",
      "start_date": "2020-01-01",
      "end_date": "2025-10-15",
      "report_notes": "Priority report",
      "lease_ids": [5, 12, 18],
      "leases": [
        {
          "id": 5,
          "agency": "BLM",
          "lease_number": "NMNM 12345",
          "runsheet_status": "Found",
          "runsheet_link": "https://...",
          "runsheet_archive_link": null,
          "document_archive_link": "https://...",
          "created_at": "2025-10-01T10:00:00Z",
          "updated_at": "2025-10-10T15:30:00Z",
          "created_by": {
            "id": 1,
            "username": "jdoe"
          },
          "updated_by": null
        },
        {
          "id": 12,
          "agency": "NMSLO",
          "lease_number": "NMNM 67890",
          "runsheet_status": "Pending",
          "runsheet_link": null,
          "runsheet_archive_link": null,
          "document_archive_link": null,
          "created_at": "2025-10-05T11:00:00Z",
          "updated_at": "2025-10-05T11:00:00Z",
          "created_by": {
            "id": 2,
            "username": "asmith"
          },
          "updated_by": null
        }
      ],
      "lease_count": 3,
      "created_at": "2025-10-15T11:00:00Z",
      "updated_at": "2025-10-18T09:15:00Z",
      "created_by": {
        "id": 1,
        "username": "jdoe"
      },
      "updated_by": {
        "id": 1,
        "username": "jdoe"
      }
    }
  ]
}
```

**Error Responses**:

`401 Unauthorized` - Missing or invalid authentication
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Notes**:
- Returns empty array if order has no reports
- Each report includes full `leases` array for inline display
- `lease_count` matches length of `leases` array

**Status**: ⚠️ Verify `order_id` query parameter support

---

### 3. Create Report

**Purpose**: Create a new report associated with an order

```
POST /api/reports/
```

**Request Headers**:
```
Cookie: access_token={jwt_token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "order_id": 1,
  "report_type": "RUNSHEET",
  "legal_description": "Section 16, Township 10N, Range 5E",
  "start_date": "2020-01-01",
  "end_date": "2025-10-15",
  "report_notes": "Priority report",
  "lease_ids": [5, 12, 18]
}
```

**Field Validation**:
| Field             | Type     | Required | Validation |
|-------------------|----------|----------|------------|
| order_id          | integer  | Yes      | Must reference existing order |
| report_type       | string   | Yes      | Must be: RUNSHEET, BASE_ABSTRACT, SUPPLEMENTAL_ABSTRACT, DOL_ABSTRACT |
| legal_description | string   | Yes      | Non-empty string |
| start_date        | string   | No       | ISO 8601 date format |
| end_date          | string   | No       | ISO 8601 date format, >= start_date |
| report_notes      | string   | No       | Optional text |
| lease_ids         | array    | Yes      | Non-empty array of existing lease IDs |

**Response**: 201 Created
```json
{
  "id": 11,
  "order": {
    "id": 1,
    "order_number": "ORD-2025-001"
  },
  "report_type": "RUNSHEET",
  "legal_description": "Section 16, Township 10N, Range 5E",
  "start_date": "2020-01-01",
  "end_date": "2025-10-15",
  "report_notes": "Priority report",
  "lease_ids": [5, 12, 18],
  "leases": [...],
  "lease_count": 3,
  "created_at": "2025-10-26T14:30:00Z",
  "updated_at": "2025-10-26T14:30:00Z",
  "created_by": {
    "id": 1,
    "username": "jdoe"
  },
  "updated_by": null
}
```

**Error Responses**:

`400 Bad Request` - Validation error
```json
{
  "order_id": ["This field is required."],
  "report_type": ["This field is required."],
  "legal_description": ["This field is required."],
  "lease_ids": ["This field is required."]
}
```

`400 Bad Request` - Invalid foreign key
```json
{
  "order_id": ["Invalid pk \"999\" - object does not exist."]
}
```

`401 Unauthorized`
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Status**: ✅ Exists

---

### 4. Update Report

**Purpose**: Update an existing report

```
PATCH /api/reports/{id}/
```

**Path Parameters**:
| Parameter | Type    | Required | Description |
|-----------|---------|----------|-------------|
| id        | integer | Yes      | Report ID   |

**Request Headers**:
```
Cookie: access_token={jwt_token}
Content-Type: application/json
```

**Request Body** (all fields optional for PATCH):
```json
{
  "report_type": "BASE_ABSTRACT",
  "legal_description": "Updated legal description",
  "start_date": "2020-06-01",
  "end_date": "2025-12-31",
  "report_notes": "Updated notes",
  "lease_ids": [5, 12, 18, 23]
}
```

**Response**: 200 OK
```json
{
  "id": 11,
  "order": {
    "id": 1,
    "order_number": "ORD-2025-001"
  },
  "report_type": "BASE_ABSTRACT",
  "legal_description": "Updated legal description",
  "start_date": "2020-06-01",
  "end_date": "2025-12-31",
  "report_notes": "Updated notes",
  "lease_ids": [5, 12, 18, 23],
  "leases": [...],
  "lease_count": 4,
  "created_at": "2025-10-26T14:30:00Z",
  "updated_at": "2025-10-26T15:45:00Z",
  "created_by": {
    "id": 1,
    "username": "jdoe"
  },
  "updated_by": {
    "id": 1,
    "username": "jdoe"
  }
}
```

**Error Responses**: Same as Create Report

**Status**: ✅ Exists

---

### 5. Delete Report

**Purpose**: Delete a report

```
DELETE /api/reports/{id}/
```

**Path Parameters**:
| Parameter | Type    | Required | Description |
|-----------|---------|----------|-------------|
| id        | integer | Yes      | Report ID   |

**Request Headers**:
```
Cookie: access_token={jwt_token}
```

**Response**: 204 No Content

**Error Responses**:

`404 Not Found`
```json
{
  "detail": "Not found."
}
```

`401 Unauthorized`
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Notes**:
- Associated leases are NOT deleted (M:N relationship)
- Order's `report_count` is automatically decremented

**Status**: ✅ Exists

---

### 6. Search Leases

**Purpose**: Search for leases by lease number or agency

```
GET /api/leases/?search={term}
```

**Query Parameters**:
| Parameter | Type    | Required | Description |
|-----------|---------|----------|-------------|
| search    | string  | No       | Search term (filters by lease_number or agency) |
| page      | integer | No       | Page number (default: 1) |
| page_size | integer | No       | Results per page (default: 20) |

**Request Headers**:
```
Cookie: access_token={jwt_token}
```

**Response**: 200 OK
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5,
      "agency": "BLM",
      "lease_number": "NMNM 12345",
      "runsheet_status": "Found",
      "runsheet_link": "https://...",
      "runsheet_archive_link": null,
      "document_archive_link": "https://...",
      "created_at": "2025-10-01T10:00:00Z",
      "updated_at": "2025-10-10T15:30:00Z",
      "created_by": {
        "id": 1,
        "username": "jdoe"
      },
      "updated_by": null
    },
    {
      "id": 12,
      "agency": "NMSLO",
      "lease_number": "NMNM 12399",
      "runsheet_status": "Pending",
      "runsheet_link": null,
      "runsheet_archive_link": null,
      "document_archive_link": null,
      "created_at": "2025-10-05T11:00:00Z",
      "updated_at": "2025-10-05T11:00:00Z",
      "created_by": {
        "id": 2,
        "username": "asmith"
      },
      "updated_by": null
    }
  ]
}
```

**Search Behavior**:
- Filters leases where `lease_number` contains the search term (case-insensitive)
- OR where `agency` matches the search term (case-insensitive)
- Example: `search=NMNM 123` returns leases with numbers containing "NMNM 123"
- Example: `search=BLM` returns all BLM leases

**Error Responses**:

`401 Unauthorized`
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Notes**:
- Returns all leases if `search` parameter is omitted
- Empty string for `search` returns all leases
- Client-side filtering is acceptable for <10K leases, but server-side is preferred for scalability

**Status**: ⚠️ Verify `search` query parameter support (may need to add)

---

### 7. Create Lease

**Purpose**: Create a new lease (used by inline lease creation)

```
POST /api/leases/
```

**Request Headers**:
```
Cookie: access_token={jwt_token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "agency": "BLM",
  "lease_number": "NMNM 99999"
}
```

**Field Validation**:
| Field        | Type   | Required | Validation |
|--------------|--------|----------|------------|
| agency       | string | Yes      | Must be: BLM or NMSLO |
| lease_number | string | Yes      | Non-empty, unique per agency |

**Response**: 201 Created
```json
{
  "id": 25,
  "agency": "BLM",
  "lease_number": "NMNM 99999",
  "runsheet_status": "Pending",
  "runsheet_link": null,
  "runsheet_archive_link": null,
  "document_archive_link": null,
  "created_at": "2025-10-26T16:00:00Z",
  "updated_at": "2025-10-26T16:00:00Z",
  "created_by": {
    "id": 1,
    "username": "jdoe"
  },
  "updated_by": null
}
```

**Error Responses**:

`400 Bad Request` - Validation error
```json
{
  "agency": ["This field is required."],
  "lease_number": ["This field is required."]
}
```

`400 Bad Request` - Duplicate lease
```json
{
  "non_field_errors": ["The fields agency, lease_number must make a unique set."]
}
```

`401 Unauthorized`
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Notes**:
- Newly created leases start with `runsheet_status = "Pending"`
- Background Celery tasks will populate runsheet links and update status
- Runsheet fields are not user-editable

**Status**: ✅ Exists

---

### 8. Update Order

**Purpose**: Update order details from order details page

```
PATCH /api/orders/{id}/
```

**Path Parameters**:
| Parameter | Type    | Required | Description |
|-----------|---------|----------|-------------|
| id        | integer | Yes      | Order ID    |

**Request Headers**:
```
Cookie: access_token={jwt_token}
Content-Type: application/json
```

**Request Body** (all fields optional for PATCH):
```json
{
  "order_number": "ORD-2025-001-UPDATED",
  "order_date": "2025-10-20",
  "order_notes": "Updated notes",
  "delivery_link": "https://newlink.com/..."
}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "order_number": "ORD-2025-001-UPDATED",
  "order_date": "2025-10-20",
  "order_notes": "Updated notes",
  "delivery_link": "https://newlink.com/...",
  "report_count": 3,
  "created_at": "2025-10-15T10:30:00Z",
  "created_by": 1,
  "created_by_username": "jdoe",
  "updated_at": "2025-10-26T16:30:00Z",
  "updated_by": 1,
  "updated_by_username": "jdoe"
}
```

**Error Responses**: Similar to Get Single Order

**Status**: ✅ Exists

---

### 9. Delete Order

**Purpose**: Delete an order (with cascade checks)

```
DELETE /api/orders/{id}/
```

**Path Parameters**:
| Parameter | Type    | Required | Description |
|-----------|---------|----------|-------------|
| id        | integer | Yes      | Order ID    |

**Request Headers**:
```
Cookie: access_token={jwt_token}
```

**Response**: 204 No Content

**Error Responses**:

`400 Bad Request` - Order has reports
```json
{
  "error": "Cannot delete order with 3 associated reports. Delete reports first."
}
```

`404 Not Found`
```json
{
  "detail": "Not found."
}
```

`401 Unauthorized`
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Notes**:
- Backend prevents deletion if reports exist
- Frontend should check `report_count` and warn user

**Status**: ✅ Exists (verify cascade protection)

---

## Authentication

All endpoints require JWT authentication via HTTP-only cookies.

**Login** (to obtain tokens):
```
POST /api/auth/login/
Content-Type: application/json

{
  "username": "jdoe",
  "password": "password123"
}
```

**Response**: Sets HTTP-only cookies
```
Set-Cookie: access_token=eyJ...; HttpOnly; SameSite=Lax; Secure
Set-Cookie: refresh_token=eyJ...; HttpOnly; SameSite=Lax; Secure

{
  "user": {
    "id": 1,
    "username": "jdoe",
    "email": "jdoe@example.com",
    "is_staff": false
  }
}
```

**Logout**:
```
POST /api/auth/logout/
Cookie: access_token={jwt_token}
```

**Refresh Token**:
```
POST /api/auth/refresh/
Cookie: refresh_token={jwt_token}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message"
}
```

Or for validation errors:
```json
{
  "field_name": ["Error message 1", "Error message 2"]
}
```

### HTTP Status Codes

| Code | Meaning            | Usage |
|------|--------------------|-------|
| 200  | OK                 | Successful GET, PATCH, PUT |
| 201  | Created            | Successful POST |
| 204  | No Content         | Successful DELETE |
| 400  | Bad Request        | Validation errors, business logic errors |
| 401  | Unauthorized       | Missing or invalid authentication |
| 403  | Forbidden          | Authenticated but not authorized |
| 404  | Not Found          | Resource does not exist |
| 500  | Internal Server Error | Server error (unhandled exception) |

---

## Backend Implementation Checklist

- [x] `/api/orders/{id}/` - Get single order (verify exists)
- [ ] `/api/reports/?order_id={id}` - Verify `order_id` filter works
- [ ] `/api/reports/` response includes full `leases` array (verify serializer)
- [ ] `/api/leases/?search={term}` - Add `search` parameter support if needed
- [x] `/api/reports/` - Create report (existing)
- [x] `/api/reports/{id}/` - Update report (existing)
- [x] `/api/reports/{id}/` - Delete report (existing)
- [x] `/api/leases/` - Create lease (existing)
- [x] `/api/orders/{id}/` - Update order (existing)
- [ ] `/api/orders/{id}/` - Delete with cascade check (verify protection)

---

## Frontend API Client Functions

**Recommended additions to `/lib/api/orders.ts`**:

```typescript
// Get single order
export async function getOrder(id: number): Promise<Order> {
  const response = await api.get(`/api/orders/${id}/`);
  return response.data;
}
```

**Recommended additions to `/lib/api/leases.ts`**:

```typescript
// Search leases
export async function searchLeases(term: string): Promise<Lease[]> {
  const response = await api.get(`/api/leases/?search=${term}&page_size=100`);
  return response.data.results;
}
```

---

## Testing Checklist

### Manual Testing

- [ ] Get order details for existing order
- [ ] Get order details for non-existent order (404)
- [ ] Filter reports by order ID
- [ ] Create report with valid data
- [ ] Create report with invalid data (validation errors)
- [ ] Update report with new leases
- [ ] Delete report
- [ ] Search leases by number
- [ ] Search leases by agency
- [ ] Create lease with valid data
- [ ] Create duplicate lease (should fail)
- [ ] Update order from details page
- [ ] Attempt to delete order with reports (should fail)
- [ ] Delete order without reports (should succeed)

### API Testing Tools

```bash
# Using curl
curl -H "Cookie: access_token=$TOKEN" http://localhost:8000/api/orders/1/
curl -H "Cookie: access_token=$TOKEN" http://localhost:8000/api/reports/?order_id=1
curl -H "Cookie: access_token=$TOKEN" http://localhost:8000/api/leases/?search=NMNM

# Using httpie
http GET localhost:8000/api/orders/1/ Cookie:"access_token=$TOKEN"
```

---

## Summary

**Total Endpoints**: 9  
**Existing**: 7-8 (most already implemented)  
**New**: 0 (only query parameter additions)  
**Backend Changes**: Minimal (verify query params, add if missing)  
**Authentication**: JWT via HTTP-only cookies  
**Status Codes**: Standard REST (200, 201, 204, 400, 401, 404)

**API Contract Status**: ✅ Complete - All endpoints documented with request/response formats

