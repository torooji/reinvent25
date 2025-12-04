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

## Event Schema

Events have the following properties:

- `eventId` (string, required) - Unique identifier
- `title` (string, required) - Event title
- `description` (string, required) - Event description
- `date` (string, required) - Event date
- `location` (string, required) - Event location
- `capacity` (integer, required) - Maximum attendees
- `organizer` (string, required) - Event organizer
- `status` (string, required) - Event status (e.g., "active", "cancelled")

## API Endpoints

**Base URL**: `https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/`

### List Events
```bash
GET /events
GET /events?status=active
```

### Get Event
```bash
GET /events/{eventId}
```

### Create Event
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
  "status": "active"
}
```

### Update Event
```bash
PUT /events/{eventId}
Content-Type: application/json

{
  "title": "Updated Title",
  "capacity": 600
}
```

### Delete Event
```bash
DELETE /events/{eventId}
```

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

### Create an event
```bash
curl -X POST https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "api-test-event-456",
    "title": "API Gateway Test Event",
    "description": "Testing API Gateway integration",
    "date": "2024-12-15",
    "location": "API Test Location",
    "capacity": 200,
    "organizer": "API Test Organizer",
    "status": "active"
  }'
```

### List all events
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events
```

### Filter by status
```bash
curl 'https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events?status=active'
```

### Get specific event
```bash
curl https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/api-test-event-456
```

### Update event
```bash
curl -X PUT https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/api-test-event-456 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated API Gateway Test Event",
    "capacity": 250
  }'
```

### Delete event
```bash
curl -X DELETE https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod/events/api-test-event-456
```

## Features

- ✅ Full CRUD operations
- ✅ Query filtering by status
- ✅ Input validation with Pydantic
- ✅ CORS enabled for web access
- ✅ Serverless architecture
- ✅ Error handling
- ✅ DynamoDB for scalable storage

## License

MIT
