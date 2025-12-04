#!/bin/bash

# Test event without waitlist
API_URL="https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod"

echo "=== Testing Event Without Waitlist ==="
echo ""

# Create event with capacity 1 and NO waitlist
echo "1. Creating event with capacity 1 and NO waitlist..."
curl -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "event-no-waitlist-001",
    "title": "No Waitlist Event",
    "description": "Testing registration without waitlist",
    "date": "2024-12-25",
    "location": "Test Location",
    "capacity": 1,
    "organizer": "Test Organizer",
    "status": "active",
    "hasWaitlist": false
  }'
echo ""
echo ""

# Register first user (should succeed)
echo "2. Registering user-001 (should succeed)..."
curl -X POST "$API_URL/events/event-no-waitlist-001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-001"
  }'
echo ""
echo ""

# Try to register second user (should be rejected)
echo "3. Registering user-002 (should be rejected - event full)..."
curl -X POST "$API_URL/events/event-no-waitlist-001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-002"
  }'
echo ""
echo ""

echo "=== Test Complete ==="
