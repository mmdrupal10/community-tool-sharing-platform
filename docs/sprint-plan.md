# Agile Sprint Plan

## Sprint 0: Setup and requirements

- Create GitHub repository, branch protection, project board, and README stub.
- Finalize roles, scope, user stories, acceptance criteria, assumptions, and risks.
- Prepare initial demo seed data plan.

## Sprint 1: First vertical slice

Goal: show a complete, simple path from login to reservation request.

- Backend auth, user model, tool model, reservation model.
- Frontend login, browse tools, request reservation.
- Seed users and tools.
- Tests for date validation and overlap detection.

## Sprint 2: Reservation workflow

Goal: implement the required state machine.

- Owner approve/deny.
- Borrower pickup.
- Owner return.
- Cancellation rules.
- Incoming/outgoing reservation dashboard.
- Tests for owner-only approval, no cancellation after pickup, and no overlaps.

## Sprint 3: Trust and coordination

Goal: add community trust features.

- Private message threads.
- Notifications.
- Reviews after returned.
- Damage reports.
- Availability calendar endpoint.

## Sprint 4: Admin and release readiness

Goal: finish course deliverables.

- Admin reports.
- Suspend users.
- Hide/deactivate listings.
- Manual QA packet.
- Deployment guide and seeded data.
- Final demo script and known limitations.
