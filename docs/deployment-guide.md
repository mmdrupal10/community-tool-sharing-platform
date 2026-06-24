# Deployment Guide

## Local release validation

1. Build and start containers.

```bash
docker compose up --build
```

2. Seed data.

```bash
docker compose exec backend python -m app.seed
```

3. Validate backend.

```bash
curl http://localhost:8000/health
```

4. Validate frontend.

Open `http://localhost:5173` and log in with a demo account.

5. Run backend tests.

```bash
docker compose exec backend pytest
```

## Environment variables

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy database connection string |
| `SECRET_KEY` | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Login token lifetime |
| `FRONTEND_ORIGIN` | CORS origin allowed by the backend |
| `VITE_API_URL` | Frontend API base URL |

## Release readiness checklist

- [ ] Backend tests pass.
- [ ] Frontend build passes.
- [ ] Seed data creates demo users and tools.
- [ ] API docs load at `/docs`.
- [ ] Main demo flow succeeds end-to-end.
- [ ] Known limitations are documented in README.
