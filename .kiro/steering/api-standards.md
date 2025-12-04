---
inclusion: fileMatch
fileMatchPattern: '**/backend/**/*.py'
---

# API Standards and Conventions

## REST API Conventions

### HTTP Methods

- **GET**: Retrieve resources (read-only, idempotent)
- **POST**: Create new resources (non-idempotent)
- **PUT**: Update existing resources (idempotent, full replacement)
- **PATCH**: Partial update of resources (idempotent)
- **DELETE**: Remove resources (idempotent)

### HTTP Status Codes

#### Success Codes
- **200 OK**: Successful GET, PUT, PATCH, or DELETE
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful request with no response body

#### Client Error Codes
- **400 Bad Request**: Invalid request format or validation error
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Resource conflict (e.g., duplicate)
- **422 Unprocessable Entity**: Validation error with details

#### Server Error Codes
- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: Service temporarily unavailable

## JSON Response Format Standards

### Success Response Format

```json
{
  "data": { ... },
  "metadata": {
    "timestamp": "2024-12-03T00:00:00Z"
  }
}
```

For single resources, return the object directly:
```json
{
  "id": "123",
  "name": "Example",
  "status": "active"
}
```

For collections, return an array:
```json
[
  { "id": "1", "name": "Item 1" },
  { "id": "2", "name": "Item 2" }
]
```

### Error Response Format

Always return errors in a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors with multiple fields:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

## API Design Guidelines

1. **Use plural nouns for resource endpoints**: `/events`, `/users`
2. **Use path parameters for resource IDs**: `/events/{eventId}`
3. **Use query parameters for filtering**: `/events?status=active`
4. **Return appropriate status codes** for all operations
5. **Include proper error handling** with descriptive messages
6. **Validate all input** using Pydantic models
7. **Enable CORS** for web access when needed
8. **Use consistent naming**: camelCase for JSON fields
9. **Document all endpoints** with clear descriptions
10. **Handle edge cases**: missing resources, invalid IDs, etc.

## FastAPI Best Practices

- Use Pydantic models for request/response validation
- Leverage FastAPI's automatic OpenAPI documentation
- Use dependency injection for shared logic
- Implement proper exception handlers
- Use HTTPException for error responses
- Add response models to endpoints for type safety
