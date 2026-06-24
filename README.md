# Community Tool Sharing Platform

ICS 613 Software Engineering course project for a private neighborhood tool lending community.

The project is intentionally simple and organized for a class demo. It implements the required stack:

- Frontend: React + TypeScript + Vite
- Backend: Python + FastAPI + SQLAlchemy + Pydantic
- Database: PostgreSQL
- Tests: Pytest for critical backend business rules
- CI/CD: GitHub Actions workflow for backend tests and frontend build

## Implemented features

- Invite-only user registration and JWT login/logout
- User profile update
- Tool listing create, update, hide, show, soft delete, browse, search, and detail views
- Reservation workflow: `REQUESTED -> APPROVED -> PICKED_UP -> RETURNED`
- Alternative reservation paths: `REQUESTED -> DENIED`, `REQUESTED -> CANCELLED`, and `APPROVED -> CANCELLED`
- No overlapping `APPROVED` or `PICKED_UP` reservations for the same tool
- Owner-only approval/denial and return confirmation
- Borrower-only pickup confirmation
- Cancellation blocked after pickup
- Private reservation message thread
- Notifications for important status changes and messages
- Reviews and ratings only after `RETURNED`
- Damage reports during or after pickup
- Member dashboard
- Admin user suspension, tool deactivation, damage report view, and basic reports
- Seeded demo data for walkthroughs

## Quick start with Docker

1. Copy environment settings:

```bash
cp .env.example .env
```

2. Start PostgreSQL, backend, and frontend:

```bash
docker compose up --build
```

3. Seed demo data in a second terminal:

```bash
docker compose exec backend python -m app.seed
```

4. Open the application:

- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Demo accounts

All seeded users use password `password123`.

| Role | Email |
| --- | --- |
| Admin | admin@example.com |
| Tool owner | owner@example.com |
| Borrower | borrower@example.com |
| Member | member@example.com |

Unused invite token for registration testing:

```text
DEMO-INVITE-NEW
```

The token is tied to `newneighbor@example.com`.

## Local development without Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://toolshare:toolshare@localhost:5432/toolshare
export SECRET_KEY=change-this-development-secret
uvicorn app.main:app --reload
```

Seed data:

```bash
python -m app.seed
```

Run tests:

```bash
pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Build check:

```bash
npm run build
```

## Project structure

```text
community-tool-sharing-platform/
  backend/
    app/
      routers/        API endpoints
      services/       Business rules and workflows
      models.py       SQLAlchemy data model
      schemas.py      Pydantic request/response schemas
      seed.py         Demo data
    tests/            Automated rule and permission tests
  frontend/
    src/
      api/            Fetch client
      auth/           Auth context
      components/     Shared UI components
      pages/          Main application screens
  docs/               Architecture, API, sprint, QA, and issue planning docs
  docker-compose.yml  Local PostgreSQL + backend + frontend
```

## Important business rules

The backend enforces these rules in `backend/app/services/reservations.py`:

- The end date must be on or after the start date.
- Owners cannot borrow their own tools.
- Only active, non-deleted tools can be reserved.
- A tool cannot have overlapping `APPROVED` or `PICKED_UP` reservations.
- Only the tool owner can approve or deny a reservation request.
- Only the borrower can mark an approved reservation as picked up.
- Only the tool owner can mark a picked-up reservation as returned.
- Cancellation is only allowed from `REQUESTED` or `APPROVED`.
- Reviews are only accepted after `RETURNED`.

## Suggested demo script

1. Log in as `borrower@example.com`.
2. Browse tools and request the Cordless Drill.
3. Log out and log in as `owner@example.com`.
4. Approve the incoming request.
5. Log back in as the borrower and mark the reservation as picked up.
6. Log in as the owner and mark the reservation as returned.
7. Log in as the borrower and submit a review.
8. Log in as `admin@example.com` and view reports, users, and tools.

## Known limitations

- Table creation is automatic for class convenience; a production system should use Alembic migrations.
- Photo upload is represented by a `photo_url` field instead of file storage.
- Reminder notifications are modeled as normal notifications; no background scheduler is included.
- Password reset is listed in the user stories but intentionally left as a future enhancement.
- The UI is functional and responsive, but intentionally not polished beyond course needs.
