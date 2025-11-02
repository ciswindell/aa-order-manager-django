# API Contract: Basecamp Order Workflows

**Feature**: Basecamp Order Workflows  
**Branch**: `007-basecamp-order-workflows`  
**Date**: 2025-11-02

## Overview

This document defines the API contract for triggering Basecamp workflow creation from orders. The API follows Django REST Framework conventions with JSON request/response bodies, JWT authentication via HTTP-only cookies, and CORS with credentials.

---

## Endpoint: Trigger Workflow Creation

### Request

**HTTP Method**: `POST`  
**URL Pattern**: `/api/orders/{order_id}/workflows/`  
**Authentication**: Required (JWT access token in HTTP-only cookie)

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `order_id` | integer | Yes | Primary key of the Order to create workflows for |

**Query Parameters**: None

**Request Headers**:
```http
Content-Type: application/json
Cookie: access_token=<jwt_token>; refresh_token=<jwt_token>
```

**Request Body**: None (empty POST)

---

### Response

**Success Response (200 OK)** - Workflows created

**Response Headers**:
```http
Content-Type: application/json
```

**Response Body**:
```json
{
  "success": true,
  "workflows_created": ["Federal Runsheets", "Federal Abstracts"],
  "total_count": 2,
  "message": "Workflows created: Federal Runsheets, Federal Abstracts"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` for 200 response |
| `workflows_created` | array[string] | List of product names that successfully created workflows |
| `total_count` | integer | Count of successful workflows (length of `workflows_created`) |
| `message` | string | Human-readable success message listing product names |

---

**Partial Success Response (200 OK)** - Some products failed

**Response Body**:
```json
{
  "success": true,
  "workflows_created": ["Federal Runsheets"],
  "failed_products": ["Federal Abstracts"],
  "total_count": 1,
  "message": "Workflows created: Federal Runsheets (1 product failed)"
}
```

**Additional Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `failed_products` | array[string] | List of product names that encountered errors |

---

**No Applicable Products Response (200 OK)** - Order has no applicable reports

**Response Body**:
```json
{
  "success": false,
  "workflows_created": [],
  "total_count": 0,
  "message": "No workflows to create for this order"
}
```

---

### Error Responses

**400 Bad Request** - Invalid order ID

```json
{
  "success": false,
  "error": "Invalid order ID",
  "message": "Order ID must be a positive integer"
}
```

---

**401 Unauthorized** - Missing or invalid JWT token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Note**: Standard Django REST Framework authentication error response

---

**403 Forbidden** - User does not have permission to access this order

```json
{
  "success": false,
  "error": "Forbidden",
  "message": "You do not have permission to create workflows for this order"
}
```

---

**404 Not Found** - Order does not exist

```json
{
  "success": false,
  "error": "Order not found",
  "message": "Order with ID {order_id} does not exist"
}
```

---

**422 Unprocessable Entity** - Missing Basecamp connection

```json
{
  "success": false,
  "error": "Basecamp not connected",
  "message": "Basecamp integration is not connected. Please connect your Basecamp account."
}
```

---

**422 Unprocessable Entity** - Missing project ID configuration

```json
{
  "success": false,
  "error": "Configuration error",
  "message": "Missing project ID configuration for Federal Runsheets. Please contact support."
}
```

---

**500 Internal Server Error** - Basecamp API failure (all products failed)

```json
{
  "success": false,
  "error": "Workflow creation failed",
  "message": "Failed to create workflows. Please try again later.",
  "failed_products": ["Federal Runsheets", "Federal Abstracts"]
}
```

**Note**: This response occurs when ALL applicable products fail (total failure). For partial success (some products succeed), return 200 OK with `failed_products` array.

---

### Status Code Summary

| Status Code | Condition |
|-------------|-----------|
| **200 OK** | Workflows created successfully (full or partial success) OR no applicable products |
| **400 Bad Request** | Invalid request parameters (non-integer order ID) |
| **401 Unauthorized** | Missing or invalid authentication |
| **403 Forbidden** | User lacks permission to access this order |
| **404 Not Found** | Order does not exist |
| **422 Unprocessable Entity** | Business logic error (missing Basecamp connection, configuration error) |
| **500 Internal Server Error** | Total failure - all applicable products failed to create workflows |

---

## Implementation Notes

### Authentication & Authorization

- **Authentication**: Django REST Framework `IsAuthenticated` permission class
- **Authorization**: Verify user has access to this order (check `order.created_by == request.user` or implement org-level access control)
- **Token Location**: JWT access token read from `access_token` HTTP-only cookie
- **Token Refresh**: Automatic via Django middleware (existing implementation)

---

### Request Validation

**Order ID Validation**:
```python
# URL converter handles integer parsing
# View validates order exists:
try:
    order = Order.objects.get(pk=order_id)
except Order.DoesNotExist:
    return Response({"success": False, "error": "Order not found", ...}, status=404)
```

**Basecamp Connection Validation**:
```python
# Check user has active Basecamp account before workflow execution
from integrations.models import BasecampAccount
if not BasecampAccount.objects.filter(user=request.user, access_token__isnull=False).exists():
    return Response({"success": False, "error": "Basecamp not connected", ...}, status=422)
```

---

### Workflow Execution

**Flow**:
1. Validate request (authentication, order exists, Basecamp connected)
2. Instantiate `WorkflowExecutor`
3. Call `executor.execute(order_id, user_id)`
4. Handle `WorkflowResult`:
   - If `success == True` and `failed_products` empty: 200 OK with full success
   - If `success == True` and `failed_products` non-empty: 200 OK with partial success
   - If `success == False` and `workflows_created` empty: 200 OK with no applicable products
   - If exception raised: 500 Internal Server Error

**Example View Implementation**:
```python
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trigger_workflow(request, order_id):
    # 1. Validate order exists
    try:
        order = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        return Response({
            "success": False,
            "error": "Order not found",
            "message": f"Order with ID {order_id} does not exist"
        }, status=404)
    
    # 2. Validate Basecamp connection
    if not BasecampAccount.objects.filter(user=request.user, access_token__isnull=False).exists():
        return Response({
            "success": False,
            "error": "Basecamp not connected",
            "message": "Basecamp integration is not connected. Please connect your Basecamp account."
        }, status=422)
    
    # 3. Execute workflows
    executor = WorkflowExecutor()
    try:
        result = executor.execute(order_id=order.id, user_id=request.user.id)
    except ValueError as e:
        # Configuration errors (missing project IDs)
        return Response({
            "success": False,
            "error": "Configuration error",
            "message": str(e)
        }, status=422)
    except Exception as e:
        # Total failure (all products failed)
        logger.error("Workflow execution failed | order_id=%s | user_id=%s", order.id, request.user.id, exc_info=True)
        return Response({
            "success": False,
            "error": "Workflow creation failed",
            "message": "Failed to create workflows. Please try again later."
        }, status=500)
    
    # 4. Return result
    serializer = WorkflowResultSerializer(result)
    return Response(serializer.data, status=200)
```

---

### Logging

**Success Logging** (INFO level):
```python
logger.info(
    "Workflow creation succeeded | order_id=%s | user_id=%s | products=%s | count=%d",
    order.id,
    request.user.id,
    ", ".join(result.workflows_created),
    result.total_count,
)
```

**Partial Success Logging** (WARNING level):
```python
logger.warning(
    "Workflow creation partial success | order_id=%s | user_id=%s | succeeded=%s | failed=%s",
    order.id,
    request.user.id,
    ", ".join(result.workflows_created),
    ", ".join(result.failed_products),
)
```

**Failure Logging** (ERROR level):
```python
logger.error(
    "Workflow creation failed | order_id=%s | user_id=%s | products=%s | error=%s",
    order.id,
    request.user.id,
    ", ".join(result.failed_products),
    str(e),
    exc_info=True,  # Include stack trace
)
```

---

### Performance Considerations

- **Timeout**: Workflow creation is synchronous, spec requires <30s for 10 reports (SC-002)
- **Retry Strategy**: Exponential backoff for Basecamp API calls (inherited from BasecampService)
- **Parallel Execution**: Products are created sequentially (simpler error handling, acceptable for <30s constraint)
- **Database Queries**: Optimize with `select_related('order')` and `prefetch_related('leases')` on reports

---

## URL Configuration

**Django URL Pattern**:
```python
# web/api/urls.py
from django.urls import path
from orders.views.workflows import trigger_workflow

urlpatterns = [
    # ... existing patterns
    path("orders/<int:order_id>/workflows/", trigger_workflow, name="trigger_workflow"),
]
```

**Full URL**: `http://localhost:8000/api/orders/123/workflows/`

---

## Serializers

### WorkflowResultSerializer

**Source**: `web/api/serializers/workflows.py` (NEW)

```python
from rest_framework import serializers

class WorkflowResultSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    workflows_created = serializers.ListField(child=serializers.CharField())
    failed_products = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    total_count = serializers.IntegerField()
    message = serializers.CharField()
    
    def to_representation(self, instance):
        # instance is WorkflowResult dataclass
        data = {
            "success": instance.success,
            "workflows_created": instance.workflows_created,
            "total_count": instance.total_count,
            "message": self._build_message(instance),
        }
        
        if instance.failed_products:
            data["failed_products"] = instance.failed_products
        
        return data
    
    def _build_message(self, instance):
        if not instance.success and instance.total_count == 0:
            return "No workflows to create for this order"
        
        if instance.failed_products:
            return f"Workflows created: {', '.join(instance.workflows_created)} ({len(instance.failed_products)} product(s) failed)"
        
        return f"Workflows created: {', '.join(instance.workflows_created)}"
```

---

## Frontend Integration

### API Client

**Source**: `frontend/src/lib/api/workflows.ts` (NEW)

```typescript
import axios from 'axios';

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
    { withCredentials: true } // Include JWT cookies
  );
  return response.data;
}
```

---

### React Component Usage

**Button Handler**:
```typescript
import { useState } from 'react';
import { triggerWorkflow } from '@/lib/api/workflows';
import { Button } from '@/components/ui/button';

export function PushToBasecampButton({ orderId }: { orderId: number }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setLoading(true);
    setError(null);
    
    try {
      const result = await triggerWorkflow(orderId);
      setResult(result);
      
      if (result.success) {
        // Show success toast
        toast.success(result.message);
      } else {
        // Show warning toast (no applicable products)
        toast.warning(result.message);
      }
    } catch (err) {
      // Handle error responses (422, 500)
      const message = err.response?.data?.message || 'Failed to create workflows';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Button 
      onClick={handleClick} 
      disabled={loading}
    >
      {loading ? 'Creating...' : 'Push to Basecamp'}
    </Button>
  );
}
```

---

## Testing Examples

### Manual Testing with curl

**Success Request**:
```bash
curl -X POST http://localhost:8000/api/orders/123/workflows/ \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<jwt_token>" \
  -v
```

**Expected Response (200 OK)**:
```json
{
  "success": true,
  "workflows_created": ["Federal Runsheets", "Federal Abstracts"],
  "total_count": 2,
  "message": "Workflows created: Federal Runsheets, Federal Abstracts"
}
```

---

**Order Not Found Request**:
```bash
curl -X POST http://localhost:8000/api/orders/99999/workflows/ \
  -H "Cookie: access_token=<jwt_token>" \
  -v
```

**Expected Response (404 Not Found)**:
```json
{
  "success": false,
  "error": "Order not found",
  "message": "Order with ID 99999 does not exist"
}
```

---

**Missing Basecamp Connection Request**:
```bash
# User has no BasecampAccount
curl -X POST http://localhost:8000/api/orders/123/workflows/ \
  -H "Cookie: access_token=<jwt_token>" \
  -v
```

**Expected Response (422 Unprocessable Entity)**:
```json
{
  "success": false,
  "error": "Basecamp not connected",
  "message": "Basecamp integration is not connected. Please connect your Basecamp account."
}
```

---

## Security Considerations

- **CSRF Protection**: Django's CSRF middleware automatically validates POST requests from same-origin frontend
- **CORS**: `django-cors-headers` configured to allow credentials from frontend origin only
- **Rate Limiting**: Consider adding rate limiting (e.g., 10 requests per minute per user) for production
- **Authorization**: Ensure users can only trigger workflows for orders they have access to
- **Input Validation**: Order ID validated by Django URL converter (must be integer)
- **Error Messages**: User-friendly messages for frontend, detailed errors in server logs only

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-02 | 1.0.0 | Initial API contract for workflow trigger endpoint |

