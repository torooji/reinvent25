from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import boto3
from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime
import os

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
events_table_name = os.environ.get('EVENTS_TABLE_NAME', 'Events')
users_table_name = os.environ.get('USERS_TABLE_NAME', 'Users')
registrations_table_name = os.environ.get('REGISTRATIONS_TABLE_NAME', 'Registrations')

events_table = dynamodb.Table(events_table_name)
users_table = dynamodb.Table(users_table_name)
registrations_table = dynamodb.Table(registrations_table_name)


# Data Models
class Event(BaseModel):
    eventId: str
    title: str
    description: str
    date: str
    location: str
    capacity: int
    organizer: str
    status: str
    hasWaitlist: bool = False
    registeredCount: int = 0


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    organizer: Optional[str] = None
    status: Optional[str] = None
    hasWaitlist: Optional[bool] = None


class User(BaseModel):
    userId: str
    name: str
    createdAt: Optional[str] = None


class UserCreate(BaseModel):
    userId: str
    name: str


class Registration(BaseModel):
    userId: str
    eventId: str
    status: str  # "registered" or "waitlisted"
    position: Optional[int] = None
    registeredAt: str


class RegistrationRequest(BaseModel):
    userId: str


class RegistrationResponse(BaseModel):
    userId: str
    eventId: str
    status: str
    position: Optional[int] = None
    message: str


@app.get("/events")
def list_events(status: Optional[str] = Query(None)):
    try:
        if status:
            response = events_table.scan(FilterExpression=Attr('status').eq(status))
        else:
            response = events_table.scan()
        return response.get('Items', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/{event_id}")
def get_event(event_id: str):
    try:
        response = events_table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        return response['Item']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events", status_code=201)
def create_event(event: Event):
    try:
        events_table.put_item(Item=event.dict())
        return event.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/events/{event_id}")
def update_event(event_id: str, event_update: EventUpdate):
    try:
        # Check if event exists
        response = events_table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Build update expression
        update_data = {k: v for k, v in event_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expr_attr_names = {f"#{k}": k for k in update_data.keys()}
        expr_attr_values = {f":{k}": v for k, v in update_data.items()}
        
        response = events_table.update_item(
            Key={'eventId': event_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ReturnValues="ALL_NEW"
        )
        return response['Attributes']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    try:
        # Check if event exists
        response = events_table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        events_table.delete_item(Key={'eventId': event_id})
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# User Management Endpoints
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    """Create a new user"""
    try:
        # Check if user already exists
        response = users_table.get_item(Key={'userId': user.userId})
        if 'Item' in response:
            raise HTTPException(status_code=409, detail=f"User with userId '{user.userId}' already exists")
        
        # Create user with timestamp
        user_data = {
            'userId': user.userId,
            'name': user.name,
            'createdAt': datetime.utcnow().isoformat()
        }
        users_table.put_item(Item=user_data)
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}")
def get_user(user_id: str):
    """Get user by ID"""
    try:
        response = users_table.get_item(Key={'userId': user_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="User not found")
        return response['Item']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users")
def list_users():
    """List all users"""
    try:
        response = users_table.scan()
        return response.get('Items', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Registration Helper Functions
def get_event_or_404(event_id: str):
    """Get event or raise 404"""
    response = events_table.get_item(Key={'eventId': event_id})
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="Event not found")
    return response['Item']


def get_user_or_404(user_id: str):
    """Get user or raise 404"""
    response = users_table.get_item(Key={'userId': user_id})
    if 'Item' not in response:
        raise HTTPException(status_code=404, detail="User not found")
    return response['Item']


def get_registration(user_id: str, event_id: str):
    """Get registration if exists"""
    response = registrations_table.get_item(Key={'userId': user_id, 'eventId': event_id})
    return response.get('Item')


def create_registration_record(user_id: str, event_id: str, status: str, position: Optional[int] = None):
    """Create a registration record"""
    registration_data = {
        'userId': user_id,
        'eventId': event_id,
        'status': status,
        'registeredAt': datetime.utcnow().isoformat()
    }
    if position is not None:
        registration_data['position'] = position
    
    registrations_table.put_item(Item=registration_data)
    return registration_data


def increment_registered_count(event_id: str):
    """Atomically increment registered count for an event"""
    events_table.update_item(
        Key={'eventId': event_id},
        UpdateExpression='SET registeredCount = if_not_exists(registeredCount, :zero) + :inc',
        ExpressionAttributeValues={':inc': 1, ':zero': 0}
    )


def decrement_registered_count(event_id: str):
    """Atomically decrement registered count for an event"""
    events_table.update_item(
        Key={'eventId': event_id},
        UpdateExpression='SET registeredCount = registeredCount - :dec',
        ExpressionAttributeValues={':dec': 1}
    )


def get_next_waitlist_position(event_id: str):
    """Get the next waitlist position for an event"""
    response = registrations_table.query(
        IndexName='eventId-index',
        KeyConditionExpression=Key('eventId').eq(event_id),
        FilterExpression=Attr('status').eq('waitlisted')
    )
    waitlist_entries = response.get('Items', [])
    if not waitlist_entries:
        return 1
    return max(entry.get('position', 0) for entry in waitlist_entries) + 1


def is_event_full(event):
    """Check if event is at capacity"""
    registered_count = event.get('registeredCount', 0)
    capacity = event.get('capacity', 0)
    return registered_count >= capacity


def handle_registration(user_id: str, event_id: str):
    """Handle registration logic with capacity and waitlist checks"""
    # Validate user and event exist
    user = get_user_or_404(user_id)
    event = get_event_or_404(event_id)
    
    # Check if already registered or waitlisted
    existing_registration = get_registration(user_id, event_id)
    if existing_registration:
        status = existing_registration.get('status')
        if status == 'registered':
            raise HTTPException(status_code=409, detail="User is already registered for this event")
        elif status == 'waitlisted':
            raise HTTPException(status_code=409, detail="User is already on the waitlist for this event")
    
    # Check capacity
    if is_event_full(event):
        # Event is full
        has_waitlist = event.get('hasWaitlist', False)
        if not has_waitlist:
            # No waitlist - reject registration
            raise HTTPException(
                status_code=422,
                detail=f"Event is full. Capacity: {event['capacity']}, Registered: {event.get('registeredCount', 0)}"
            )
        else:
            # Add to waitlist
            position = get_next_waitlist_position(event_id)
            registration = create_registration_record(user_id, event_id, 'waitlisted', position)
            return RegistrationResponse(
                userId=user_id,
                eventId=event_id,
                status='waitlisted',
                position=position,
                message=f"Event is full. Added to waitlist at position {position}"
            )
    else:
        # Event has capacity - register user
        registration = create_registration_record(user_id, event_id, 'registered')
        increment_registered_count(event_id)
        return RegistrationResponse(
            userId=user_id,
            eventId=event_id,
            status='registered',
            position=None,
            message="Successfully registered for event"
        )


# Registration Endpoints
@app.post("/events/{event_id}/register", status_code=201)
def register_for_event(event_id: str, request: RegistrationRequest):
    """Register a user for an event"""
    try:
        result = handle_registration(request.userId, event_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def promote_from_waitlist(event_id: str):
    """Promote the first person from waitlist to registered"""
    # Find first waitlisted user (position = 1)
    response = registrations_table.query(
        IndexName='eventId-index',
        KeyConditionExpression=Key('eventId').eq(event_id),
        FilterExpression=Attr('status').eq('waitlisted') & Attr('position').eq(1)
    )
    
    waitlist_entries = response.get('Items', [])
    if not waitlist_entries:
        return None
    
    first_waitlisted = waitlist_entries[0]
    user_id = first_waitlisted['userId']
    
    # Update status to registered and remove position
    registrations_table.update_item(
        Key={'userId': user_id, 'eventId': event_id},
        UpdateExpression='SET #status = :registered REMOVE #position',
        ExpressionAttributeNames={'#status': 'status', '#position': 'position'},
        ExpressionAttributeValues={':registered': 'registered'}
    )
    
    # Decrement positions for remaining waitlist entries
    response = registrations_table.query(
        IndexName='eventId-index',
        KeyConditionExpression=Key('eventId').eq(event_id),
        FilterExpression=Attr('status').eq('waitlisted')
    )
    
    for entry in response.get('Items', []):
        if entry.get('position', 0) > 1:
            registrations_table.update_item(
                Key={'userId': entry['userId'], 'eventId': event_id},
                UpdateExpression='SET #position = #position - :dec',
                ExpressionAttributeNames={'#position': 'position'},
                ExpressionAttributeValues={':dec': 1}
            )
    
    return user_id


def handle_unregistration(user_id: str, event_id: str):
    """Handle unregistration logic with waitlist promotion"""
    # Check if registration exists
    registration = get_registration(user_id, event_id)
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    status = registration.get('status')
    
    # Delete registration
    registrations_table.delete_item(Key={'userId': user_id, 'eventId': event_id})
    
    # If user was registered (not waitlisted), decrement count and promote from waitlist
    if status == 'registered':
        decrement_registered_count(event_id)
        
        # Check if there's a waitlist to promote from
        promoted_user = promote_from_waitlist(event_id)
        
        if promoted_user:
            # Increment count for promoted user
            increment_registered_count(event_id)
            return {
                "message": "Successfully unregistered from event",
                "promoted_user": promoted_user
            }
    
    return {"message": "Successfully unregistered from event"}


@app.delete("/events/{event_id}/register/{user_id}")
def unregister_from_event(event_id: str, user_id: str):
    """Unregister a user from an event"""
    try:
        result = handle_unregistration(user_id, event_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Query Endpoints
@app.get("/users/{user_id}/registrations")
def get_user_registrations(user_id: str):
    """Get all events a user is registered for"""
    try:
        # Verify user exists
        get_user_or_404(user_id)
        
        # Query registrations for user with status="registered"
        response = registrations_table.query(
            KeyConditionExpression=Key('userId').eq(user_id),
            FilterExpression=Attr('status').eq('registered')
        )
        
        registrations = response.get('Items', [])
        
        # Fetch event details for each registration
        events = []
        for reg in registrations:
            event_response = events_table.get_item(Key={'eventId': reg['eventId']})
            if 'Item' in event_response:
                events.append(event_response['Item'])
        
        # Sort by date
        events.sort(key=lambda x: x.get('date', ''))
        
        return events
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}/waitlist")
def get_user_waitlist(user_id: str):
    """Get all events a user is waitlisted for"""
    try:
        # Verify user exists
        get_user_or_404(user_id)
        
        # Query registrations for user with status="waitlisted"
        response = registrations_table.query(
            KeyConditionExpression=Key('userId').eq(user_id),
            FilterExpression=Attr('status').eq('waitlisted')
        )
        
        waitlist_entries = response.get('Items', [])
        
        # Fetch event details and include position
        results = []
        for entry in waitlist_entries:
            event_response = events_table.get_item(Key={'eventId': entry['eventId']})
            if 'Item' in event_response:
                event_data = event_response['Item']
                event_data['waitlistPosition'] = entry.get('position')
                results.append(event_data)
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/{event_id}/registrations")
def get_event_registrations(event_id: str):
    """Get all users registered for an event"""
    try:
        # Verify event exists
        get_event_or_404(event_id)
        
        # Query registrations for event with status="registered"
        response = registrations_table.query(
            IndexName='eventId-index',
            KeyConditionExpression=Key('eventId').eq(event_id),
            FilterExpression=Attr('status').eq('registered')
        )
        
        registrations = response.get('Items', [])
        
        # Fetch user details for each registration
        users = []
        for reg in registrations:
            user_response = users_table.get_item(Key={'userId': reg['userId']})
            if 'Item' in user_response:
                users.append(user_response['Item'])
        
        return users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/{event_id}/waitlist")
def get_event_waitlist(event_id: str):
    """Get all users on waitlist for an event"""
    try:
        # Verify event exists
        get_event_or_404(event_id)
        
        # Query registrations for event with status="waitlisted"
        response = registrations_table.query(
            IndexName='eventId-index',
            KeyConditionExpression=Key('eventId').eq(event_id),
            FilterExpression=Attr('status').eq('waitlisted')
        )
        
        waitlist_entries = response.get('Items', [])
        
        # Fetch user details and include position
        results = []
        for entry in waitlist_entries:
            user_response = users_table.get_item(Key={'userId': entry['userId']})
            if 'Item' in user_response:
                user_data = user_response['Item']
                user_data['waitlistPosition'] = entry.get('position')
                results.append(user_data)
        
        # Sort by position
        results.sort(key=lambda x: x.get('waitlistPosition', 0))
        
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
