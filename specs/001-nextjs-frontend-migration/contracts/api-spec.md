# API Contract Specification

**Feature**: Next.js Frontend Migration  
**Branch**: `001-nextjs-frontend-migration`  
**Date**: 2025-10-26  
**Base URL**: `http://localhost:8000/api` (development), `https://{domain}/api` (production)

## Overview

REST API for AA Order Manager frontend. All endpoints require JWT authentication except `/auth/login/`. Tokens provided as HTTP-only cookies.

**Authentication**: JWT tokens in HTTP-only cookies (`access_token`, `refresh_token`)  
**Content-Type**: `application/json`  
**CORS**: Credentials required (`credentials: 'include'`)  
**Rate Limiting**: None (per clarifications)

## Common Responses

### Success Response Structure
```json
{
  "data": { ... },          // Single object or array
  "message": "Success",      // Optional success message
  "meta": {                  // Optional metadata
    "page": 1,
    "page_size": 20,
    "total_count": 150,
    "total_pages": 8
  }
}
```

### Error Response Structure
```json
{
  "error": {
    "message": "User-friendly error message",
    "code": "ERROR_CODE",
    "details": {              // Optional field-specific errors
      "field_name": ["Error message"]
    }
  }
}
```

### HTTP Status Codes
- `200 OK`: Successful GET, PUT, PATCH
- `201 Created`: Successful POST
- `204 No Content`: Successful DELETE
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Authentication Endpoints

### POST /auth/login/
**Description**: Authenticate user and receive JWT tokens  
**Authentication**: None (public endpoint)

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin"
}
```

**Success Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_staff": true
  }
}
```

**Cookies Set**:
- `access_token` (HTTP-only, SameSite=Lax, max-age=900 seconds / 15 minutes)
- `refresh_token` (HTTP-only, SameSite=Lax, max-age=604800 seconds / 7 days)

**Error Responses**:
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials

**Frontend Implementation**:
```typescript
const response = await fetch(`${API_URL}/auth/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // Required for cookies
  body: JSON.stringify({ username, password })
});
```

---

### POST /auth/refresh/
**Description**: Refresh expired access token using refresh token  
**Authentication**: Refresh token cookie required

**Request Body**: None (token from cookie)

**Success Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1..."
}
```

**Cookies Updated**:
- `access_token` (new token, HTTP-only, 15 min expiry)

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token

**Frontend Implementation**:
Automatic via interceptor when 401 received on API call.

---

### POST /auth/logout/
**Description**: Invalidate refresh token and clear cookies  
**Authentication**: Required (access token)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "detail": "Successfully logged out."
}
```

**Cookies Cleared**:
- `access_token` (deleted)
- `refresh_token` (blacklisted, deleted)

**Error Responses**:
- `401 Unauthorized`: Not authenticated

---

### GET /auth/user/
**Description**: Get current authenticated user profile  
**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_staff": true
}
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated

---

## Dashboard Endpoint

### GET /dashboard/
**Description**: Get dashboard overview data (integration status, stats)  
**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "user": {
    "username": "admin",
    "is_staff": true
  },
  "integrations": [
    {
      "provider": "dropbox",
      "is_connected": true,
      "is_authenticated": true,
      "last_sync": "2025-01-26T08:30:00Z",
      "blocking_problem": false
    },
    {
      "provider": "basecamp",
      "is_connected": false,
      "is_authenticated": false,
      "blocking_problem": false,
      "action_required": "Coming Soon"
    }
  ],
  "stats": {
    "total_orders": 45,
    "total_reports": 123,
    "total_leases": 456
  }
}
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated

---

## Integration Endpoints

### GET /integrations/status/
**Description**: Get status of all integrations  
**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "integrations": [
    {
      "provider": "dropbox",
      "is_connected": true,
      "is_authenticated": true,
      "last_sync": "2025-01-26T08:30:00Z",
      "blocking_problem": false,
      "cta_url": null
    },
    {
      "provider": "basecamp",
      "is_connected": false,
      "is_authenticated": false,
      "last_sync": null,
      "blocking_problem": false,
      "cta_url": null
    }
  ]
}
```

---

### POST /integrations/dropbox/connect/
**Description**: Initiate Dropbox OAuth connection flow  
**Authentication**: Required (staff only)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "authorization_url": "https://www.dropbox.com/oauth2/authorize?client_id=..."
}
```

**Frontend Implementation**: Redirect user to `authorization_url`

**Error Responses**:
- `403 Forbidden`: User not staff
- `500 Internal Server Error`: OAuth configuration error

---

### POST /integrations/dropbox/disconnect/
**Description**: Disconnect Dropbox integration and revoke tokens  
**Authentication**: Required (staff only)

**Request Body**: None

**Success Response** (200 OK):
```json
{
  "detail": "Dropbox disconnected successfully."
}
```

**Error Responses**:
- `403 Forbidden`: User not staff
- `404 Not Found`: Dropbox not connected

---

## Order Endpoints

### GET /orders/
**Description**: List all orders (paginated)  
**Authentication**: Required

**Query Parameters**:
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 20, max: 100): Items per page
- `ordering` (string, optional): Sort field (`order_date`, `-order_date`, `order_number`, etc.)

**Success Response** (200 OK):
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order_number": "ORD-2025-001",
      "order_date": "2025-01-15",
      "delivery_link": "https://example.com/delivery/ord-001",
      "report_count": 3,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-16T14:22:00Z",
      "created_by": {
        "id": 1,
        "username": "admin"
      },
      "updated_by": {
        "id": 1,
        "username": "admin"
      }
    }
  ]
}
```

---

### POST /orders/
**Description**: Create new order  
**Authentication**: Required

**Request Body**:
```json
{
  "order_number": "ORD-2025-001",
  "order_date": "2025-01-15",
  "delivery_link": "https://example.com/delivery/ord-001"  // Optional
}
```

**Success Response** (201 Created):
```json
{
  "id": 1,
  "order_number": "ORD-2025-001",
  "order_date": "2025-01-15",
  "delivery_link": "https://example.com/delivery/ord-001",
  "report_count": 0,
  "created_at": "2025-01-26T10:00:00Z",
  "updated_at": "2025-01-26T10:00:00Z",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "updated_by": {
    "id": 1,
    "username": "admin"
  }
}
```

**Error Responses**:
- `400 Bad Request`: Validation errors (missing fields, invalid date format, invalid URL)

**Validation Rules**:
- `order_number`: required, max 255 characters
- `order_date`: required, valid date format (YYYY-MM-DD), not future date
- `delivery_link`: optional, valid URL format if provided

---

### GET /orders/{id}/
**Description**: Get single order details  
**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": 1,
  "order_number": "ORD-2025-001",
  "order_date": "2025-01-15",
  "delivery_link": "https://example.com/delivery/ord-001",
  "report_count": 3,
  "reports": [
    {
      "id": 1,
      "report_type": "Runsheet",
      "legal_description": "Section 12, Township 5N",
      "lease_count": 5
    }
  ],
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-16T14:22:00Z",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "updated_by": {
    "id": 1,
    "username": "admin"
  }
}
```

**Error Responses**:
- `404 Not Found`: Order does not exist

---

### PATCH /orders/{id}/
**Description**: Partially update order  
**Authentication**: Required

**Request Body** (partial):
```json
{
  "order_number": "ORD-2025-001-UPDATED",
  "delivery_link": "https://example.com/new-delivery"
}
```

**Success Response** (200 OK): Same as GET /orders/{id}/

**Error Responses**:
- `400 Bad Request`: Validation errors
- `404 Not Found`: Order does not exist

---

### DELETE /orders/{id}/
**Description**: Delete order  
**Authentication**: Required

**Success Response** (204 No Content): Empty response

**Error Responses**:
- `400 Bad Request`: Order has associated reports (cannot delete)
- `404 Not Found`: Order does not exist

**Business Rule**: Cannot delete order if it has associated reports. Return error with message: "Cannot delete order with existing reports. Delete reports first."

---

## Report Endpoints

### GET /reports/
**Description**: List all reports (paginated, filterable)  
**Authentication**: Required

**Query Parameters**:
- `page` (integer, default: 1)
- `page_size` (integer, default: 20)
- `order` (integer, optional): Filter by order ID
- `report_type` (string, optional): Filter by type
- `ordering` (string, optional): Sort field

**Success Response** (200 OK):
```json
{
  "count": 250,
  "next": "http://localhost:8000/api/reports/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "order": {
        "id": 1,
        "order_number": "ORD-2025-001"
      },
      "report_type": "Runsheet",
      "legal_description": "Section 12, Township 5N, Range 3W",
      "report_date": "2025-01-20",
      "lease_count": 5,
      "created_at": "2025-01-15T11:00:00Z",
      "updated_at": "2025-01-20T09:15:00Z",
      "created_by": {
        "id": 1,
        "username": "admin"
      },
      "updated_by": {
        "id": 2,
        "username": "researcher"
      }
    }
  ]
}
```

---

### POST /reports/
**Description**: Create new report  
**Authentication**: Required

**Request Body**:
```json
{
  "order": 1,
  "report_type": "Runsheet",
  "legal_description": "Section 12, Township 5N, Range 3W",
  "report_date": "2025-01-20"  // Optional
}
```

**Success Response** (201 Created): Same structure as GET

**Validation Rules**:
- `order`: required, must reference existing order
- `report_type`: required, must be one of: "Runsheet", "Base Abstract", "Current Owner", "Full Abstract", "Title Opinion", "Other"
- `legal_description`: required, text field
- `report_date`: optional, valid date format, cannot be future date

---

### GET /reports/{id}/
**Description**: Get single report with nested leases  
**Authentication**: Required

**Success Response** (200 OK):
```json
{
  "id": 1,
  "order": {
    "id": 1,
    "order_number": "ORD-2025-001"
  },
  "report_type": "Runsheet",
  "legal_description": "Section 12, Township 5N, Range 3W",
  "report_date": "2025-01-20",
  "lease_count": 5,
  "leases": [
    {
      "id": 1,
      "agency_name": "BLM",
      "lease_number": "NM-12345",
      "runsheet_status": "Found"
    }
  ],
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-20T09:15:00Z",
  "created_by": {
    "id": 1,
    "username": "admin"
  },
  "updated_by": {
    "id": 2,
    "username": "researcher"
  }
}
```

---

### PATCH /reports/{id}/
**Description**: Partially update report  
**Authentication**: Required

**Request Body** (partial):
```json
{
  "legal_description": "Updated legal description",
  "report_date": "2025-01-21"
}
```

**Success Response** (200 OK): Same as GET

---

### DELETE /reports/{id}/
**Description**: Delete report  
**Authentication**: Required

**Success Response** (204 No Content)

**Error Responses**:
- `400 Bad Request`: Report has associated leases
- `404 Not Found`: Report does not exist

---

## Lease Endpoints

### GET /leases/
**Description**: List all leases (paginated, filterable)  
**Authentication**: Required

**Query Parameters**:
- `page` (integer, default: 1)
- `page_size` (integer, default: 20)
- `report` (integer, optional): Filter by report ID
- `agency_name` (string, optional): Filter by agency
- `ordering` (string, optional): Sort field

**Success Response** (200 OK):
```json
{
  "count": 1500,
  "next": "http://localhost:8000/api/leases/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "report": {
        "id": 1,
        "order_number": "ORD-2025-001"
      },
      "agency_name": "BLM",
      "lease_number": "NM-12345",
      "runsheet_link": "https://dropbox.com/sh/abc123/runsheet.pdf",
      "runsheet_archive_link": "https://dropbox.com/sh/abc123",
      "runsheet_status": "Found",
      "document_archive_link": "https://dropbox.com/sh/xyz789/documents",
      "created_at": "2025-01-15T12:00:00Z",
      "updated_at": "2025-01-22T16:45:00Z",
      "created_by": {
        "id": 1,
        "username": "admin"
      },
      "updated_by": {
        "id": 1,
        "username": "admin"
      }
    }
  ]
}
```

---

### POST /leases/
**Description**: Create new lease  
**Authentication**: Required

**Request Body**:
```json
{
  "report": 1,
  "agency_name": "BLM",
  "lease_number": "NM-12345"
}
```

**Success Response** (201 Created): Same structure as GET

**Validation Rules**:
- `report`: required, must reference existing report
- `agency_name`: required, max 255 characters
- `lease_number`: required, max 255 characters

**Note**: `runsheet_link` and `runsheet_status` populated by background Celery tasks (not user-editable)

---

### GET /leases/{id}/
**Description**: Get single lease details  
**Authentication**: Required

**Success Response** (200 OK): Same structure as list item

---

### PATCH /leases/{id}/
**Description**: Partially update lease  
**Authentication**: Required

**Request Body** (partial):
```json
{
  "agency_name": "Updated Agency",
  "lease_number": "NM-12345-A"
}
```

**Success Response** (200 OK): Same as GET

**Note**: Cannot edit `runsheet_link`, `runsheet_status` (managed by Celery)

---

### DELETE /leases/{id}/
**Description**: Delete lease  
**Authentication**: Required

**Success Response** (204 No Content)

---

## CORS Configuration

**Allowed Origins** (development):
- `http://localhost:3000` (Next.js dev server)

**Allowed Origins** (production):
- Configured domain (e.g., `https://orders.example.com`)

**Required Headers**:
- `Access-Control-Allow-Credentials: true`
- `Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type, Authorization`

## Security Headers

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (production only)

## Pagination

All list endpoints use Django REST Framework's `PageNumberPagination`:
- Default `page_size`: 20
- Max `page_size`: 100
- Query parameters: `page`, `page_size`

**Response Meta**:
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/orders/?page=3",
  "previous": "http://localhost:8000/api/orders/?page=1",
  "results": [...]
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_FAILED` | Invalid credentials or token |
| `TOKEN_EXPIRED` | Access token expired (trigger refresh) |
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `PERMISSION_DENIED` | Insufficient permissions |
| `DELETE_RESTRICTED` | Cannot delete due to dependencies |
| `SERVER_ERROR` | Internal server error |

## Frontend TypeScript Types

```typescript
// User
interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;
}

// Order
interface Order {
  id: number;
  order_number: string;
  order_date: string; // ISO date format
  delivery_link?: string;
  report_count: number;
  created_at: string;
  updated_at: string;
  created_by: User;
  updated_by: User;
}

// Report
interface Report {
  id: number;
  order: { id: number; order_number: string };
  report_type: 'Runsheet' | 'Base Abstract' | 'Current Owner' | 'Full Abstract' | 'Title Opinion' | 'Other';
  legal_description: string;
  report_date?: string;
  lease_count: number;
  created_at: string;
  updated_at: string;
  created_by: User;
  updated_by: User;
}

// Lease
interface Lease {
  id: number;
  report: { id: number; order_number: string };
  agency_name: string;
  lease_number: string;
  runsheet_link?: string;
  runsheet_archive_link?: string;
  runsheet_status: 'Found' | 'Not Found' | 'Pending';
  document_archive_link?: string;
  created_at: string;
  updated_at: string;
  created_by: User;
  updated_by: User;
}

// Integration Status
interface IntegrationStatus {
  provider: 'dropbox' | 'basecamp';
  is_connected: boolean;
  is_authenticated: boolean;
  last_sync?: string;
  blocking_problem: boolean;
  action_required?: string;
  cta_url?: string;
}

// Paginated Response
interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

// API Error
interface APIError {
  error: {
    message: string;
    code: string;
    details?: Record<string, string[]>;
  };
}
```

## Implementation Notes

1. All timestamps in ISO 8601 format (UTC)
2. All URLs validated on backend (format, accessibility)
3. Audit fields (created_by, updated_by) set automatically from request.user
4. No rate limiting implemented per clarifications
5. HTTP-only cookies used for JWT tokens (XSS protection)
6. CORS credentials required for all authenticated requests
7. Token refresh automatic via interceptor on 401 response
8. Manual pagination controls (no infinite scroll)
9. Optimistic updates recommended for better UX (with rollback on error)
10. Toast notifications for all success/error responses

## Testing Endpoints

**Health Check** (not authenticated):
```bash
curl http://localhost:8000/api/health/
# Response: {"status": "ok"}
```

**Login**:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  -c cookies.txt  # Save cookies
```

**Authenticated Request**:
```bash
curl http://localhost:8000/api/orders/ \
  -b cookies.txt  # Send cookies
```

## Next Steps

- Implement backend API endpoints in Django (api/views/, api/serializers/)
- Generate frontend API client (lib/api/)
- Implement TanStack Query hooks (hooks/)
- Create UI components for each page
- Test all endpoints with Postman or curl
- Validate error handling and edge cases

