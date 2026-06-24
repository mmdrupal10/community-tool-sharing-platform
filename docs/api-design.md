# API Design

Base URL: `http://localhost:8000`

Authentication: JWT bearer token in the `Authorization` header.

## Auth

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/auth/register` | Create account with invitation token |
| POST | `/auth/login` | Log in and receive JWT |
| GET | `/auth/me` | Get current user |

## Invitations

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/invitations` | Create an invite token |
| GET | `/invitations/pending` | Admin list of unused invites |

## Tools

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/tools?q=&category=` | Browse/search active tools |
| GET | `/tools/mine` | List my tools |
| POST | `/tools` | Create tool listing |
| GET | `/tools/{tool_id}` | Tool detail |
| PUT | `/tools/{tool_id}` | Update my tool |
| PATCH | `/tools/{tool_id}/hide` | Hide my tool |
| PATCH | `/tools/{tool_id}/show` | Show my tool |
| DELETE | `/tools/{tool_id}` | Soft-delete my tool |
| GET | `/tools/{tool_id}/availability` | Approved/picked-up date windows |

## Reservations

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/reservations` | Request reservation |
| GET | `/reservations/incoming` | Requests for my tools |
| GET | `/reservations/outgoing` | My borrowing reservations |
| GET | `/reservations/{reservation_id}` | Reservation detail |
| POST | `/reservations/{reservation_id}/approve` | Owner approval |
| POST | `/reservations/{reservation_id}/deny` | Owner denial |
| POST | `/reservations/{reservation_id}/cancel` | Participant cancellation before pickup |
| POST | `/reservations/{reservation_id}/pickup` | Borrower pickup confirmation |
| POST | `/reservations/{reservation_id}/return` | Owner return confirmation |

## Collaboration

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/messages/{reservation_id}` | List reservation messages |
| POST | `/messages/{reservation_id}` | Send reservation message |
| GET | `/notifications` | List my notifications |
| PATCH | `/notifications/{notification_id}/read` | Mark notification read |
| POST | `/reviews/{reservation_id}` | Review after returned |
| GET | `/reviews/users/{user_id}` | Reviews for a user |
| POST | `/damage-reports/{reservation_id}` | Borrower damage report |

## Admin

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/admin/users` | List users |
| PATCH | `/admin/users/{user_id}/suspend` | Suspend/unsuspend user |
| GET | `/admin/tools` | List all visible/hidden tools |
| PATCH | `/admin/tools/{tool_id}/activation` | Hide/show listing as admin |
| GET | `/admin/reports` | Basic counts and status summaries |
| GET | `/damage-reports` | Admin list of damage reports |
