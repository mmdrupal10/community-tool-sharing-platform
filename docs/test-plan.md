# Test Plan

## Automated test coverage

Backend tests are located in `backend/tests` and cover the highest-risk business rules:

- Owner-only approval.
- No overlapping approved/picked-up reservations.
- Cancellation blocked after pickup.
- End-to-end reservation workflow.
- Review blocked before return.
- Non-participant blocked from messages.
- Admin suspension.

Run:

```bash
cd backend
pytest
```

## Manual test cases

| ID | Related story | Preconditions | Steps | Expected result |
| --- | --- | --- | --- | --- |
| TC-001 | Invite-only registration | Unused invite token exists | Register with matching email and token | Account is created and token is marked used |
| TC-002 | Login/logout | User account exists | Login with valid credentials | User sees dashboard |
| TC-003 | Add tool | Member is logged in | Create listing with name, description, category, condition | Tool appears under My Tools |
| TC-004 | Search tool | Active listings exist | Browse by keyword/category | Matching active tools appear |
| TC-005 | Hide tool | Owner owns a visible listing | Hide listing | Listing disappears from browse but remains in My Tools |
| TC-006 | Request reservation | Tool has no active overlap | Request valid date range | Reservation is created as REQUESTED |
| TC-007 | Invalid date range | Borrower is requesting | End date before start date | API rejects request |
| TC-008 | Approve request | Owner has incoming REQUESTED reservation | Owner approves | Status becomes APPROVED |
| TC-009 | Deny request | Owner has incoming REQUESTED reservation | Owner denies | Status becomes DENIED |
| TC-010 | Non-owner approval | Non-owner is logged in | Attempt approve request | API rejects action |
| TC-011 | Pickup | Borrower has APPROVED reservation | Borrower marks picked up | Status becomes PICKED_UP |
| TC-012 | Cancel after pickup | Reservation is PICKED_UP | Attempt cancellation | API rejects cancellation |
| TC-013 | Return | Owner has PICKED_UP reservation | Owner confirms return | Status becomes RETURNED |
| TC-014 | Review after return | Reservation is RETURNED | Participant submits review | Review is saved |
| TC-015 | Review before return | Reservation is APPROVED | Participant submits review | API rejects review |
| TC-016 | Message participant | Participant opens reservation thread | Send message | Message appears in thread and notification is created |
| TC-017 | Damage report | Borrower has PICKED_UP reservation | Submit damage report | Report is saved and owner notified |
| TC-018 | Admin suspend user | Admin logged in | Suspend a member | Member can no longer log in |
| TC-019 | Admin hide listing | Admin logged in | Deactivate listing | Listing is hidden from browse |
| TC-020 | Admin report | Demo data exists | Open admin reports | Counts by users, tools, reservations, reviews, damage reports appear |
