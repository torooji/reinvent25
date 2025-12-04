#!/bin/bash

# Test script for user registration workflow
API_URL="https://wzrke7u7ke.execute-api.us-west-2.amazonaws.com/prod"

echo "=== Testing User Registration Workflow ==="
echo ""

# 1. Create users
echo "1. Creating users..."
curl -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-001",
    "name": "Alice Johnson"
  }'
echo ""

curl -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-002",
    "name": "Bob Smith"
  }'
echo ""

curl -X POST "$API_URL/users" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-003",
    "name": "Charlie Brown"
  }'
echo ""
echo ""

# 2. Create an event with capacity 2 and waitlist enabled
echo "2. Creating event with capacity 2 and waitlist enabled..."
curl -X POST "$API_URL/events" \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "event-reg-test-001",
    "title": "Registration Test Event",
    "description": "Testing registration with capacity and waitlist",
    "date": "2024-12-20",
    "location": "Test Location",
    "capacity": 2,
    "organizer": "Test Organizer",
    "status": "active",
    "hasWaitlist": true
  }'
echo ""
echo ""

# 3. Register first user (should succeed)
echo "3. Registering user-001 (should succeed)..."
curl -X POST "$API_URL/events/event-reg-test-001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-001"
  }'
echo ""
echo ""

# 4. Register second user (should succeed)
echo "4. Registering user-002 (should succeed)..."
curl -X POST "$API_URL/events/event-reg-test-001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-002"
  }'
echo ""
echo ""

# 5. Register third user (should be waitlisted)
echo "5. Registering user-003 (should be waitlisted)..."
curl -X POST "$API_URL/events/event-reg-test-001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-003"
  }'
echo ""
echo ""

# 6. Check user-001's registrations
echo "6. Checking user-001's registrations..."
curl "$API_URL/users/user-001/registrations"
echo ""
echo ""

# 7. Check user-003's waitlist
echo "7. Checking user-003's waitlist..."
curl "$API_URL/users/user-003/waitlist"
echo ""
echo ""

# 8. Check event registrations
echo "8. Checking event registrations..."
curl "$API_URL/events/event-reg-test-001/registrations"
echo ""
echo ""

# 9. Check event waitlist
echo "9. Checking event waitlist..."
curl "$API_URL/events/event-reg-test-001/waitlist"
echo ""
echo ""

# 10. Unregister user-001 (should promote user-003 from waitlist)
echo "10. Unregistering user-001 (should promote user-003)..."
curl -X DELETE "$API_URL/events/event-reg-test-001/register/user-001"
echo ""
echo ""

# 11. Check event registrations after promotion
echo "11. Checking event registrations after promotion..."
curl "$API_URL/events/event-reg-test-001/registrations"
echo ""
echo ""

# 12. Check event waitlist after promotion (should be empty)
echo "12. Checking event waitlist after promotion..."
curl "$API_URL/events/event-reg-test-001/waitlist"
echo ""
echo ""

# 13. Check user-003's registrations (should now be registered)
echo "13. Checking user-003's registrations..."
curl "$API_URL/users/user-003/registrations"
echo ""
echo ""

echo "=== Test Complete ==="
