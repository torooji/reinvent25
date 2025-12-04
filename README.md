# Events API

A serverless REST API for managing events, built with FastAPI and deployed on AWS using Lambda, API Gateway, and DynamoDB.

## Architecture

- **Backend**: FastAPI (Python)
- **Database**: DynamoDB
- **Deployment**: AWS Lambda + API Gateway
- **Infrastructure**: AWS CDK (Python)

## Project Structure

```
.
├── backend/              # FastAPI application
│   ├── main.py          # API endpoints and business logic
│   ├── lambda_handler.py # Lambda entry point
│   └── requirements.txt  # Python dependencies
├── infrastructure/       # AWS CDK infrastructure code
│   ├── app.py           # CDK app entry point
│   ├── stacks/          # CDK stack definitions
│   └── requirements.txt  # CDK dependencies
└── lambda-layer/        # Lambda layer with dependencies
```

## Data Schemas

### Event Schema

Events have the following properties:

- `eventId` (string, required) - Unique identifier
- `title` (string, required) - Event title
- `description` (string, required) - Event description
- `date` (string, required) - Event date
- `location` (string, required) - Event location
- `capacity` (integer, required) - Maximum attendees
- `organizer` (string, required) - Event organizer
- `status` (string, required) - Event status (e.g., "active", "cancelled")
- `hasWaitlist` (boolean, optional, default: false) - Whether waitlist is enabled
- `registeredCount` (integer, optional, default: 0) - Current number of registered users

### User Schema

Users have the following properties:

- `userId` (string, required) - Unique identifier
- `name` (string, required) - User's display name
- `createdAt` (string, auto-generated) - ISO 8601 timestamp

### Registration Schema

Registrations track user-event associations:

- `userId` (string, required) - User identifier
- `eventId` (string, required) - Event identifier
- `status` (string, required) - "registered" or "waitlisted"
- `position` (integer, optional) - Waitlist position (only for waitlisted status)
- `registeredAt` (string, auto-generated) - ISO 8601 timestamp

## API Endpoints

**Base URL**: `https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/`

### Event Management

#### List Events
```bash
GET /events
GET /events?status=active
```

#### Get Event
```bash
GET /events/{eventId}
```

#### Create Event
```bash
POST /events
Content-Type: application/json

{
  "eventId": "event-123",
  "title": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-12-15",
  "location": "San Francisco, CA",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "active",
  "hasWaitlist": true
}
```

#### Update Event
```bash
PUT /events/{eventId}
Content-Type: application/json

{
  "title": "Updated Title",
  "capacity": 600,
  "hasWaitlist": true
}
```

#### Delete Event
```bash
DELETE /events/{eventId}
```

### User Management

#### Create User
```bash
POST /users
Content-Type: application/json

{
  "userId": "user-123",
  "name": "John Doe"
}
```

#### Get User
```bash
GET /users/{userId}
```

#### List Users
```bash
GET /users
```

### Registration Management

#### Register for Event
```bash
POST /events/{eventId}/register
Content-Type: application/json

{
  "userId": "user-123"
}
```

Response when registered:
```json
{
  "userId": "user-123",
  "eventId": "event-123",
  "status": "registered",
  "position": null,
  "message": "Successfully registered for event"
}
```

Response when waitlisted:
```json
{
  "userId": "user-123",
  "eventId": "event-123",
  "status": "waitlisted",
  "position": 1,
  "message": "Event is full. Added to waitlist at position 1"
}
```

#### Unregister from Event
```bash
DELETE /events/{eventId}/register/{userId}
```

Response:
```json
{
  "message": "Successfully unregistered from event",
  "promoted_user": "user-456"  // Only present if someone was promoted from waitlist
}
```

#### Get User's Registrations
```bash
GET /users/{userId}/registrations
```

Returns array of events the user is registered for, sorted by date.

#### Get User's Waitlist
```bash
GET /users/{userId}/waitlist
```

Returns array of events the user is waitlisted for, with `waitlistPosition` included.

#### Get Event Registrations
```bash
GET /events/{eventId}/registrations
```

Returns array of users registered for the event.

#### Get Event Waitlist
```bash
GET /events/{eventId}/waitlist
```

Returns array of users on the waitlist, sorted by position, with `waitlistPosition` included.

## Setup & Deployment

### Prerequisites

- Python 3.12+
- Node.js (for AWS CDK CLI)
- AWS CLI configured with credentials
- Docker (optional, for local testing)

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Deploy Infrastructure

1. Install CDK CLI:
```bash
npm install -g aws-cdk
```

2. Set up Python environment:
```bash
cd infrastructure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Bootstrap CDK (first time only):
```bash
cdk bootstrap aws://ACCOUNT_ID/REGION
```

4. Deploy:
```bash
cdk deploy
```

## Usage Examples

### Event Management

#### Create an event with waitlist
```bash
curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "tech-conf-2024",
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "date": "2024-12-15",
    "location": "San Francisco, CA",
    "capacity": 100,
    "organizer": "Tech Corp",
    "status": "active",
    "hasWaitlist": true
  }'
```

#### List all events
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events
```

#### Filter by status
```bash
curl 'https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events?status=active'
```

#### Get specific event
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024
```

#### Update event
```bash
curl -X PUT https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Tech Conference 2024",
    "capacity": 150
  }'
```

#### Delete event
```bash
curl -X DELETE https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024
```

### User Management

#### Create users
```bash
curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "alice-001",
    "name": "Alice Johnson"
  }'

curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "bob-002",
    "name": "Bob Smith"
  }'
```

#### Get user
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users/alice-001
```

#### List all users
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users
```

### Registration Workflow

#### Register for an event
```bash
curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024/register \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "alice-001"
  }'
```

#### Unregister from an event
```bash
curl -X DELETE https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024/register/alice-001
```

#### Get user's registrations
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users/alice-001/registrations
```

#### Get user's waitlist
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users/alice-001/waitlist
```

#### Get event registrations
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024/registrations
```

#### Get event waitlist
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/tech-conf-2024/waitlist
```

### Complete Registration Workflow Example

```bash
# 1. Create an event with capacity 2 and waitlist enabled
curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "workshop-001",
    "title": "Python Workshop",
    "description": "Hands-on Python programming workshop",
    "date": "2024-12-20",
    "location": "Tech Hub",
    "capacity": 2,
    "organizer": "Code Academy",
    "status": "active",
    "hasWaitlist": true
  }'

# 2. Create users
curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users \
  -H "Content-Type: application/json" \
  -d '{"userId": "user-1", "name": "Alice"}'

curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users \
  -H "Content-Type: application/json" \
  -d '{"userId": "user-2", "name": "Bob"}'

curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/users \
  -H "Content-Type: application/json" \
  -d '{"userId": "user-3", "name": "Charlie"}'

# 3. Register first two users (will succeed)
curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/workshop-001/register \
  -H "Content-Type: application/json" \
  -d '{"userId": "user-1"}'

curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/workshop-001/register \
  -H "Content-Type: application/json" \
  -d '{"userId": "user-2"}'

# 4. Register third user (will be waitlisted)
curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/workshop-001/register \
  -H "Content-Type: application/json" \
  -d '{"userId": "user-3"}'

# 5. Check event registrations (should show 2 users)
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/workshop-001/registrations

# 6. Check event waitlist (should show user-3 at position 1)
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/workshop-001/waitlist

# 7. Unregister user-1 (user-3 will be automatically promoted)
curl -X DELETE https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/workshop-001/register/user-1

# 8. Check registrations again (should show user-2 and user-3)
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/workshop-001/registrations

# 9. Check waitlist again (should be empty)
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/workshop-001/waitlist
```

### Waitlist Behavior

When an event has `hasWaitlist: true`:
- Users can register until capacity is reached
- Additional registration attempts create waitlist entries with sequential positions
- When a registered user unregisters, the first person on the waitlist (position 1) is automatically promoted
- Remaining waitlist positions are decremented after promotion

When an event has `hasWaitlist: false`:
- Users can register until capacity is reached
- Additional registration attempts are rejected with a 422 error
- Error message includes current capacity and registered count

## Features

### Event Management
- ✅ Full CRUD operations for events
- ✅ Query filtering by status
- ✅ Capacity constraints with configurable limits
- ✅ Optional waitlist functionality

### User Management
- ✅ User creation and retrieval
- ✅ Duplicate user detection

### Registration System
- ✅ Event registration with capacity enforcement
- ✅ Automatic waitlist management when events are full
- ✅ Waitlist promotion on unregistration
- ✅ Query user registrations and waitlist status
- ✅ Query event registrations and waitlist

### Technical Features
- ✅ Input validation with Pydantic
- ✅ CORS enabled for web access
- ✅ Serverless architecture (Lambda + API Gateway)
- ✅ Comprehensive error handling
- ✅ DynamoDB for scalable storage with GSI for efficient queries
- ✅ Atomic operations for count management

## License

MIT
