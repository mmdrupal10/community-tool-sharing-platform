# Architecture Design

## Style

Layered 3-tier architecture.

```mermaid
flowchart TB
  subgraph Presentation Layer
    UI[React + TypeScript Web UI]
  end

  subgraph Business Logic Layer
    API[FastAPI Routers]
    Auth[Authentication and Authorization]
    ToolService[Tool Management]
    ReservationService[Reservation State Machine]
    Messaging[Messaging]
    Reviews[Reviews and Ratings]
    Notifications[Notification Service]
    Admin[Admin Reporting]
  end

  subgraph Data Layer
    DB[(PostgreSQL)]
  end

  UI --> API
  API --> Auth
  API --> ToolService
  API --> ReservationService
  API --> Messaging
  API --> Reviews
  API --> Notifications
  API --> Admin
  Auth --> DB
  ToolService --> DB
  ReservationService --> DB
  Messaging --> DB
  Reviews --> DB
  Notifications --> DB
  Admin --> DB
```

## Backend component responsibilities

| Component | Responsibility |
| --- | --- |
| `routers/auth.py` | Register with invite, login, current user |
| `routers/tools.py` | Listing CRUD, hide/show/delete, search, availability |
| `routers/reservations.py` | Request, approve, deny, cancel, pickup, return |
| `services/reservations.py` | Reservation state machine and overlap rules |
| `routers/messages.py` | Private message thread per reservation |
| `routers/reviews.py` | Returned-only reviews and ratings |
| `routers/notifications.py` | User notification list and read state |
| `routers/admin.py` | User suspension, listing deactivation, reports |
| `models.py` | Database entities and relationships |
| `schemas.py` | API validation and response shapes |

## Domain model

```mermaid
erDiagram
  USER ||--o{ TOOL : owns
  USER ||--o{ RESERVATION : borrows
  USER ||--o{ INVITATION : creates
  TOOL ||--o{ RESERVATION : reserved_for
  RESERVATION ||--o{ MESSAGE : has
  RESERVATION ||--o{ REVIEW : has
  RESERVATION ||--o{ DAMAGE_REPORT : has
  USER ||--o{ NOTIFICATION : receives

  USER {
    int id
    string email
    string full_name
    string role
    bool is_suspended
  }

  TOOL {
    int id
    int owner_id
    string name
    string category
    string condition
    bool is_active
    bool is_deleted
  }

  RESERVATION {
    int id
    int tool_id
    int borrower_id
    string status
    date start_date
    date end_date
  }

  MESSAGE {
    int id
    int reservation_id
    int sender_id
    text body
  }

  REVIEW {
    int id
    int reservation_id
    int reviewer_id
    int reviewee_id
    int rating
  }
```

## Reservation state machine

```mermaid
stateDiagram-v2
  [*] --> REQUESTED
  REQUESTED --> APPROVED: owner approves
  REQUESTED --> DENIED: owner denies
  REQUESTED --> CANCELLED: participant cancels
  APPROVED --> PICKED_UP: borrower confirms pickup
  APPROVED --> CANCELLED: participant cancels
  PICKED_UP --> RETURNED: owner confirms return
  RETURNED --> [*]
  DENIED --> [*]
  CANCELLED --> [*]
```

## Tradeoffs

- JWT authentication is simple and demo-friendly, but a production system would add refresh tokens and stronger session controls.
- Automatic table creation avoids migration complexity for the course, but migrations should be introduced before production.
- `photo_url` keeps the frontend simple and avoids object storage setup.
- Reminder notifications are represented in the data model but do not use a background scheduler.
