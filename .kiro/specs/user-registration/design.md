# Design Document: User Registration System

## Overview

The User Registration System extends the existing Events API to enable user management and event registration with capacity enforcement and waitlist functionality. The system will be built using the existing FastAPI framework and DynamoDB infrastructure, adding new data models, API endpoints, and business logic to handle user registration workflows.

The design maintains consistency with the existing Events API architecture while introducing three new core entities: Users, Registrations, and Waitlist entries. The system enforces capacity constraints, manages waitlist promotion, and provides users with visibility into their event commitments.

## Architecture

### System Components

The registration system integrates with the existing serverless architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Lambda (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Events     │  │    Users     │  │ Registration │      │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                   │              │
│         └─────────────────┴───────────────────┘              │
│                           │                                  │
│                  ┌────────▼────────┐                         │
│                  │  Business Logic │                         │
│                  │  - Capacity     │                         │
│                  │  - Waitlist     │                         │
│                  │  - Validation   │                         │
│                  └────────┬────────┘                         │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DynamoDB                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Events    │  │    Users     │  │ Registrations│      │
│  │    Table     │  │    Table     │  │    Table     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

1. **Events API Extension**: New endpoints coexist with existing event management endpoints
2. **DynamoDB Tables**: Three tables (Events, Users, Registrations) with appropriate indexes
3. **Lambda Handler**: Existing Mangum handler routes all requests
4. **CDK Infrastructure**: Extended to provision new DynamoDB tables

### Design Decisions

1. **Separate Tables**: Users and Registrations use dedicated DynamoDB tables rather than embedding data in Events table for better scalability and query flexibility
2. **Composite Keys**: Registrations table uses composite key (userId, eventId) for efficient lookups
3. **Denormalized Counts**: Events table stores registered count to avoid expensive count queries
4. **Waitlist as Registration Status**: Waitlist entries are stored as Registrations with status="waitlisted" and position number
5. **Atomic Operations**: Use DynamoDB conditional writes to prevent race conditions during registration

## Components and Interfaces

### API Endpoints

#### User Management

**POST /users**
- Creates a new user
- Request body: `{ "userId": string, "name": string }`
- Response: 201 Created with user object
- Errors: 400 (validation), 409 (duplicate userId)

**GET /users/{userId}**
- Retrieves user information
- Response: 200 OK with user object
- Errors: 404 (user not found)

**GET /users**
- Lists all users
- Response: 200 OK with array of user objects

#### Registration Management

**POST /events/{eventId}/register**
- Registers a user for an event
- Request body: `{ "userId": string }`
- Response: 201 Created with registration object OR waitlist confirmation
- Errors: 400 (validation), 404 (user/event not found), 409 (already registered), 422 (event full, no waitlist)

**DELETE /events/{eventId}/register/{userId}**
- Unregisters a user from an event
- Response: 200 OK with confirmation message
- Errors: 404 (registration not found)
- Side effect: Promotes first waitlisted user if applicable

**GET /users/{userId}/registrations**
- Lists all events a user is registered for
- Response: 200 OK with array of event objects (sorted by date)
- Errors: 404 (user not found)

**GET /users/{userId}/waitlist**
- Lists all events a user is waitlisted for
- Response: 200 OK with array of objects containing event details and waitlist position
- Errors: 404 (user not found)

**GET /events/{eventId}/registrations**
- Lists all users registered for an event
- Response: 200 OK with array of user objects
- Errors: 404 (event not found)

**GET /events/{eventId}/waitlist**
- Lists all users on waitlist for an event
- Response: 200 OK with array of objects containing user details and position
- Errors: 404 (event not found)

#### Event Management Extensions

**PUT /events/{eventId}**
- Extended to support `hasWaitlist` boolean field
- Existing capacity field used for capacity constraint

## Data Models

### User Model

```python
class User(BaseModel):
    userId: str          # Unique identifier (partition key)
    name: str            # User's display name
    createdAt: str       # ISO 8601 timestamp
```

**DynamoDB Schema:**
- Table: Users
- Partition Key: userId (String)
- Attributes: name, createdAt

### Registration Model

```python
class Registration(BaseModel):
    userId: str          # User identifier (partition key)
    eventId: str         # Event identifier (sort key)
    status: str          # "registered" or "waitlisted"
    position: Optional[int]  # Waitlist position (null if registered)
    registeredAt: str    # ISO 8601 timestamp
```

**DynamoDB Schema:**
- Table: Registrations
- Partition Key: userId (String)
- Sort Key: eventId (String)
- GSI: eventId-index (for querying registrations by event)
- Attributes: status, position, registeredAt

### Event Model Extensions

The existing Event model is extended with:

```python
class Event(BaseModel):
    # ... existing fields ...
    capacity: int                    # Maximum registered users
    hasWaitlist: bool = False        # Whether waitlist is enabled
    registeredCount: int = 0         # Current number of registered users
```

### Request/Response Models

```python
class UserCreate(BaseModel):
    userId: str
    name: str

class RegistrationRequest(BaseModel):
    userId: str

class RegistrationResponse(BaseModel):
    userId: str
    eventId: str
    status: str  # "registered" or "waitlisted"
    position: Optional[int] = None
    message: str

class EventWithRegistration(BaseModel):
    # All Event fields plus:
    registrationStatus: str  # "registered", "waitlisted", or "not_registered"
    waitlistPosition: Optional[int] = None
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User creation round-trip
*For any* valid userId and name, creating a user and then retrieving it should return a user with the same userId and name.
**Validates: Requirements 1.1, 1.5**

### Property 2: Event capacity and waitlist persistence
*For any* event with capacity and waitlist settings, creating or updating the event and then retrieving it should return an event with the same capacity and waitlist configuration.
**Validates: Requirements 2.1, 2.2**

### Property 3: Capacity constraint invariant
*For any* event with capacity N, the number of users with status="registered" for that event should never exceed N.
**Validates: Requirements 2.3**

### Property 4: Waitlist enabled allows overflow
*For any* event with capacity N and hasWaitlist=true, after registering N users, attempting to register an additional user should create a waitlist entry with status="waitlisted".
**Validates: Requirements 2.4, 5.1**

### Property 5: Waitlist disabled rejects overflow
*For any* event with capacity N and hasWaitlist=false, after registering N users, attempting to register an additional user should be rejected with an error indicating the event is full.
**Validates: Requirements 2.5, 4.1**

### Property 6: Successful registration creates association
*For any* user and event with available capacity (registeredCount < capacity), registering the user should create a registration record with status="registered" that can be queried.
**Validates: Requirements 3.1, 3.5**

### Property 7: Registration idempotency
*For any* user already registered for an event, attempting to register again should be rejected with an error indicating duplicate registration.
**Validates: Requirements 3.2**

### Property 8: Full event error includes capacity information
*For any* event at capacity without waitlist, attempting to register should return an error response containing both the capacity value and current registered count.
**Validates: Requirements 4.2**

### Property 9: Waitlist position ordering
*For any* event with waitlist entries, the position numbers should be sequential starting from 1, and the order should match the creation timestamp order (earlier requests get lower positions).
**Validates: Requirements 5.2**

### Property 10: Waitlist response includes position
*For any* user added to a waitlist, the response should include the waitlist position number.
**Validates: Requirements 5.3**

### Property 11: Waitlist idempotency
*For any* user already on a waitlist for an event, attempting to join the waitlist again should be rejected with an error indicating duplicate waitlist entry.
**Validates: Requirements 5.4**

### Property 12: Registration and waitlist mutual exclusivity
*For any* user and event, the user cannot simultaneously have both status="registered" and status="waitlisted" for the same event.
**Validates: Requirements 5.5**

### Property 13: Unregistration removes record
*For any* user registered for an event, unregistering should remove the registration record such that subsequent queries show no registration.
**Validates: Requirements 6.1**

### Property 14: Unregistration decrements count
*For any* event with registeredCount=N, when a user unregisters, the registeredCount should become N-1.
**Validates: Requirements 6.2, 9.2**

### Property 15: Waitlist promotion on unregistration
*For any* event at capacity with M waitlist entries (M > 0), when a registered user unregisters, the first waitlisted user (position=1) should be promoted to status="registered", their waitlist entry removed, and remaining waitlist positions decremented.
**Validates: Requirements 6.4, 6.5**

### Property 16: User registrations query completeness
*For any* user with N registrations, querying their registered events should return exactly N events, each corresponding to a registration record.
**Validates: Requirements 7.1**

### Property 17: Registration query includes event details
*For any* user's registered events query, each returned event should contain all event fields (eventId, title, description, date, location, capacity, organizer, status, hasWaitlist).
**Validates: Requirements 7.2**

### Property 18: Registered events sorted by date
*For any* user with multiple registrations, the returned events should be ordered by the date field in ascending order.
**Validates: Requirements 7.5**

### Property 19: User waitlist query completeness
*For any* user with N waitlist entries, querying their waitlist should return exactly N entries, each with event details and position.
**Validates: Requirements 8.1**

### Property 20: Waitlist query includes position and event details
*For any* user's waitlist query, each returned entry should include the waitlist position and all event fields.
**Validates: Requirements 8.2, 8.3**

### Property 21: Registration increments count
*For any* event with registeredCount=N, when a user successfully registers (not waitlisted), the registeredCount should become N+1.
**Validates: Requirements 9.1**

### Property 22: Success operations return 2xx status codes
*For any* successful API operation (create user, register, unregister, query), the HTTP response status code should be in the 2xx range (200, 201, or 204).
**Validates: Requirements 10.3**

### Property 23: Client errors return 4xx status codes
*For any* API operation that fails due to client error (invalid input, duplicate, not found, conflict), the HTTP response status code should be in the 4xx range (400, 404, 409, 422).
**Validates: Requirements 10.4**

## Error Handling

### Error Categories

1. **Validation Errors (400 Bad Request)**
   - Missing required fields (userId, name, eventId)
   - Invalid data types
   - Empty or whitespace-only strings

2. **Not Found Errors (404 Not Found)**
   - User does not exist
   - Event does not exist
   - Registration does not exist

3. **Conflict Errors (409 Conflict)**
   - Duplicate userId on user creation
   - Duplicate registration attempt
   - Duplicate waitlist entry attempt

4. **Business Logic Errors (422 Unprocessable Entity)**
   - Event is full and has no waitlist
   - Attempting to register when already waitlisted
   - Attempting to waitlist when already registered

5. **Server Errors (500 Internal Server Error)**
   - DynamoDB operation failures
   - Unexpected exceptions

### Error Response Format

All errors follow the FastAPI standard format:

```json
{
  "detail": "Descriptive error message"
}
```

For validation errors with multiple fields:

```json
{
  "detail": [
    {
      "loc": ["body", "userId"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Atomic Operations

To prevent race conditions during concurrent registrations:

1. **Registration with Capacity Check**: Use DynamoDB conditional write with condition `registeredCount < capacity`
2. **Waitlist Position Assignment**: Use atomic counter increment for position assignment
3. **Unregistration with Promotion**: Use DynamoDB transaction to atomically unregister and promote waitlisted user

## Testing Strategy

### Unit Testing

Unit tests will verify specific behaviors and edge cases:

1. **User Management**
   - Create user with valid data
   - Reject duplicate userId
   - Reject missing required fields
   - Retrieve existing user
   - Handle non-existent user

2. **Registration Logic**
   - Register user for event with capacity
   - Reject registration when event full (no waitlist)
   - Add to waitlist when event full (with waitlist)
   - Reject duplicate registration
   - Handle non-existent user/event references

3. **Unregistration Logic**
   - Remove registration successfully
   - Promote waitlisted user on unregistration
   - Update waitlist positions after promotion
   - Handle non-existent registration

4. **Query Operations**
   - List user's registrations
   - List user's waitlist entries
   - List event's registrations
   - List event's waitlist
   - Handle empty results

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs using the **Hypothesis** library for Python. Each test will run a minimum of 100 iterations.

Each property-based test must be tagged with a comment explicitly referencing the correctness property from this design document using the format: `# Feature: user-registration, Property {number}: {property_text}`

Property-based tests will focus on:

1. **Invariants**
   - Capacity constraint never violated (Property 3)
   - Registration and waitlist mutual exclusivity (Property 12)
   - Count consistency with actual registrations (Properties 14, 21)

2. **Round-trip Properties**
   - User creation and retrieval (Property 1)
   - Event capacity/waitlist persistence (Property 2)
   - Registration creation and query (Property 6)

3. **Idempotence**
   - Duplicate registration rejection (Property 7)
   - Duplicate waitlist rejection (Property 11)

4. **Metamorphic Properties**
   - Waitlist position ordering (Property 9)
   - Registered events sorting (Property 18)
   - Unregistration decrements count (Property 14)

5. **State Transitions**
   - Waitlist promotion on unregistration (Property 15)
   - Overflow handling with/without waitlist (Properties 4, 5)

### Test Data Generators

For property-based testing, we'll create generators for:

- **Random Users**: Generate valid userId (alphanumeric strings) and names
- **Random Events**: Generate events with varying capacities (1-1000) and waitlist settings
- **Registration Sequences**: Generate sequences of register/unregister operations
- **Edge Cases**: Empty strings, very long strings, boundary capacity values (0, 1, max int)

### Integration Testing

Integration tests will verify end-to-end workflows:

1. Complete registration flow: create user → create event → register → verify
2. Waitlist flow: fill event → add to waitlist → unregister → verify promotion
3. Multi-user scenarios: concurrent registrations, race conditions
4. Query operations: verify data consistency across tables

### Testing Tools

- **pytest**: Test runner and framework
- **Hypothesis**: Property-based testing library
- **moto**: Mock AWS services for local testing
- **pytest-asyncio**: Async test support if needed

## Implementation Notes

### DynamoDB Considerations

1. **Eventual Consistency**: Use consistent reads for critical operations (capacity checks)
2. **Indexes**: Create GSI on Registrations table for eventId lookups
3. **Transactions**: Use for atomic operations (unregister + promote)
4. **Conditional Writes**: Prevent race conditions during registration

### Performance Optimizations

1. **Denormalized Counts**: Store registeredCount in Events table to avoid expensive count queries
2. **Batch Operations**: Use batch get/write for listing operations when possible
3. **Pagination**: Implement pagination for large result sets (future enhancement)

### Future Enhancements

1. **Email Notifications**: Notify users when promoted from waitlist
2. **Registration Timestamps**: Track when users registered for analytics
3. **Cancellation Reasons**: Allow users to provide reason for unregistration
4. **Waitlist Expiration**: Auto-remove waitlist entries after time period
5. **Event Categories**: Filter registrations by event type
6. **User Profiles**: Extended user information (email, preferences)
