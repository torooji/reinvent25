# Implementation Plan

- [ ] 1. Set up data models and DynamoDB tables
  - Create Pydantic models for User, Registration, and extended Event
  - Define request/response models for API endpoints
  - Update CDK stack to provision Users and Registrations DynamoDB tables with appropriate keys and indexes
  - Update Events table schema to include hasWaitlist and registeredCount fields
  - _Requirements: 1.1, 2.1, 2.2, 9.1_

- [ ]* 1.1 Write property test for user creation round-trip
  - **Property 1: User creation round-trip**
  - **Validates: Requirements 1.1, 1.5**

- [ ]* 1.2 Write property test for event capacity and waitlist persistence
  - **Property 2: Event capacity and waitlist persistence**
  - **Validates: Requirements 2.1, 2.2**

- [ ] 2. Implement user management endpoints
  - Create POST /users endpoint for user creation with validation
  - Create GET /users/{userId} endpoint for retrieving user details
  - Create GET /users endpoint for listing all users
  - Implement duplicate userId detection and error handling
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 2.1 Write property test for HTTP status codes on user operations
  - **Property 22: Success operations return 2xx status codes**
  - **Property 23: Client errors return 4xx status codes**
  - **Validates: Requirements 10.3, 10.4**

- [ ] 3. Implement core registration logic
  - Create registration service function that checks capacity and creates registration records
  - Implement capacity constraint enforcement (registeredCount < capacity)
  - Implement atomic counter increment for registeredCount on successful registration
  - Add validation for user and event existence
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 9.1_

- [ ]* 3.1 Write property test for capacity constraint invariant
  - **Property 3: Capacity constraint invariant**
  - **Validates: Requirements 2.3**

- [ ]* 3.2 Write property test for successful registration
  - **Property 6: Successful registration creates association**
  - **Validates: Requirements 3.1, 3.5**

- [ ]* 3.3 Write property test for registration idempotency
  - **Property 7: Registration idempotency**
  - **Validates: Requirements 3.2**

- [ ]* 3.4 Write property test for registration increments count
  - **Property 21: Registration increments count**
  - **Validates: Requirements 9.1**

- [ ] 4. Implement waitlist functionality
  - Add logic to detect when event is at capacity
  - Implement waitlist entry creation with position assignment
  - Create atomic position counter for waitlist ordering
  - Add validation to prevent duplicate waitlist entries
  - Implement mutual exclusivity check (cannot be both registered and waitlisted)
  - _Requirements: 2.4, 2.5, 4.1, 4.2, 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 4.1 Write property test for waitlist enabled allows overflow
  - **Property 4: Waitlist enabled allows overflow**
  - **Validates: Requirements 2.4, 5.1**

- [ ]* 4.2 Write property test for waitlist disabled rejects overflow
  - **Property 5: Waitlist disabled rejects overflow**
  - **Validates: Requirements 2.5, 4.1**

- [ ]* 4.3 Write property test for full event error includes capacity info
  - **Property 8: Full event error includes capacity information**
  - **Validates: Requirements 4.2**

- [ ]* 4.4 Write property test for waitlist position ordering
  - **Property 9: Waitlist position ordering**
  - **Validates: Requirements 5.2**

- [ ]* 4.5 Write property test for waitlist response includes position
  - **Property 10: Waitlist response includes position**
  - **Validates: Requirements 5.3**

- [ ]* 4.6 Write property test for waitlist idempotency
  - **Property 11: Waitlist idempotency**
  - **Validates: Requirements 5.4**

- [ ]* 4.7 Write property test for registration and waitlist mutual exclusivity
  - **Property 12: Registration and waitlist mutual exclusivity**
  - **Validates: Requirements 5.5**

- [ ] 5. Implement registration endpoint
  - Create POST /events/{eventId}/register endpoint
  - Wire up capacity checking and registration logic
  - Wire up waitlist logic for full events
  - Implement error responses for various failure scenarios
  - Return appropriate status codes and response bodies
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 5.1, 5.3_

- [ ] 6. Implement unregistration logic and endpoint
  - Create unregistration service function that removes registration records
  - Implement atomic counter decrement for registeredCount
  - Add waitlist promotion logic (find first waitlisted user, promote to registered)
  - Implement position reordering for remaining waitlist entries after promotion
  - Use DynamoDB transaction for atomic unregister + promote operation
  - Create DELETE /events/{eventId}/register/{userId} endpoint
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 9.2_

- [ ]* 6.1 Write property test for unregistration removes record
  - **Property 13: Unregistration removes record**
  - **Validates: Requirements 6.1**

- [ ]* 6.2 Write property test for unregistration decrements count
  - **Property 14: Unregistration decrements count**
  - **Validates: Requirements 6.2, 9.2**

- [ ]* 6.3 Write property test for waitlist promotion on unregistration
  - **Property 15: Waitlist promotion on unregistration**
  - **Validates: Requirements 6.4, 6.5**

- [ ] 7. Implement user registration query endpoints
  - Create GET /users/{userId}/registrations endpoint
  - Query Registrations table by userId with status="registered"
  - Fetch full event details for each registration
  - Sort results by event date in ascending order
  - Handle non-existent user and empty results
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 7.1 Write property test for user registrations query completeness
  - **Property 16: User registrations query completeness**
  - **Validates: Requirements 7.1**

- [ ]* 7.2 Write property test for registration query includes event details
  - **Property 17: Registration query includes event details**
  - **Validates: Requirements 7.2**

- [ ]* 7.3 Write property test for registered events sorted by date
  - **Property 18: Registered events sorted by date**
  - **Validates: Requirements 7.5**

- [ ] 8. Implement user waitlist query endpoints
  - Create GET /users/{userId}/waitlist endpoint
  - Query Registrations table by userId with status="waitlisted"
  - Fetch full event details and include position for each entry
  - Handle non-existent user and empty results
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ]* 8.1 Write property test for user waitlist query completeness
  - **Property 19: User waitlist query completeness**
  - **Validates: Requirements 8.1**

- [ ]* 8.2 Write property test for waitlist query includes position and event details
  - **Property 20: Waitlist query includes position and event details**
  - **Validates: Requirements 8.2, 8.3**

- [ ] 9. Implement event registration query endpoints
  - Create GET /events/{eventId}/registrations endpoint
  - Query Registrations table using GSI on eventId with status="registered"
  - Fetch user details for each registration
  - Create GET /events/{eventId}/waitlist endpoint
  - Query Registrations table using GSI on eventId with status="waitlisted"
  - Sort waitlist results by position
  - _Requirements: 7.1, 8.1_

- [ ] 10. Add Hypothesis testing framework setup
  - Install Hypothesis library in backend requirements.txt
  - Create test configuration file for Hypothesis settings (minimum 100 iterations)
  - Create custom generators for Users, Events, and Registration sequences
  - Set up test fixtures for DynamoDB mocking with moto
  - _Requirements: All (testing infrastructure)_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Update infrastructure deployment
  - Deploy updated CDK stack with new DynamoDB tables
  - Verify table creation and indexes
  - Update environment variables for Lambda function
  - Test deployed endpoints with sample requests
  - _Requirements: All (deployment)_

- [ ] 13. Update documentation
  - Update README.md with new API endpoints and examples
  - Document User and Registration schemas
  - Add usage examples for registration workflows
  - Document waitlist behavior and promotion logic
  - _Requirements: All (documentation)_
