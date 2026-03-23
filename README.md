# Gemini Chat — Backend API

A modular, pluggable RESTful backend built with Python and Flask. Handles user authentication (email/password and Google OAuth), JWT-based session management, and persistent chat storage via PostgreSQL. Designed as a standalone service — completely decoupled from the frontend.

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## Overview

This backend was built with a deliberate separation of concerns. It has no knowledge of the frontend, no AI logic, and no UI. Its only job is user management and data persistence — exposed through a clean REST API that any frontend can consume.

The storage layer is intentionally pluggable. Swapping PostgreSQL for any other SQL database requires changing a single line. The API contract is stable regardless of what sits underneath.

---

## Features

- **JWT authentication** — stateless, secure, industry-standard token auth
- **Email/password auth** — bcrypt password hashing, never plain text
- **Google OAuth 2.0** — full OAuth flow via Authlib
- **Per-user data isolation** — every query is scoped to the authenticated user
- **Full CRUD for chats** — create, read, update, delete conversations
- **Modular structure** — routes, models, auth, and database are fully decoupled
- **Pluggable database** — one line change to swap database engines

---

## Architecture

```
HTTP Request
      │
      ▼
Flask Router (app/__init__.py)
      │
      ├── /api/auth/*  →  routes/auth.py  →  models/user.py
      │                                            │
      └── /api/chats/* →  routes/chats.py →  models/chat.py
                                                   │
                                             database.py
                                                   │
                                            PostgreSQL
```

### Why This Structure is Modular

Each layer has a single responsibility and communicates only with the layer directly below it:

```
routes/         → HTTP only (parse request, return response, status codes)
    ↓
models/         → data structure and schema only
    ↓
database.py     → connection and initialization only
    ↓
PostgreSQL      → storage
```

Adding a new feature means adding a new file — not modifying existing ones. A new `routes/users.py` Blueprint can be registered in `__init__.py` without touching `routes/chats.py` or `routes/auth.py` at all.

### Why It is Pluggable

The database engine is configured in one place — `database.py`. Every model, route, and query uses SQLAlchemy's ORM which is database-agnostic. The application has no knowledge of which database sits underneath.

```python
# SQLite (development/testing)
"sqlite:///chats.db"

# PostgreSQL (current production)
"postgresql://user:pass@host:5432/gemini_chat"

# MySQL (hypothetical swap)
"mysql://user:pass@host:3306/gemini_chat"
```

One line. Everything else stays identical.

---

## Project Structure

```
gemini-chat-backend/
├── app/
│   ├── __init__.py          # Application factory — assembles all pieces
│   ├── database.py          # DB instance and initialization (the pluggable layer)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User schema — email, password hash, Google ID
│   │   └── chat.py          # Chat schema — messages, history, user ownership
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Register, login, Google OAuth, /me
│       └── chats.py         # CRUD endpoints, all JWT-protected
├── instance/
│   └── chats.db             # Only present in SQLite mode
├── venv/                    # Virtual environment (not committed)
├── .env                     # Environment variables (not committed)
├── .gitignore
├── Procfile                 # Tells Render how to start the app
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python version for deployment
└── run.py                   # Entry point
```

---

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL installed and running

### Installation

1. Clone the repository
```bash
git clone https://github.com/your-username/gemini-chat-backend.git
cd gemini-chat-backend
```

2. Create and activate a virtual environment
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a PostgreSQL database
```bash
psql -U postgres
```
```sql
CREATE DATABASE gemini_chat;
CREATE USER gemini_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE gemini_chat TO gemini_user;
GRANT ALL ON SCHEMA public TO gemini_user;
ALTER DATABASE gemini_chat OWNER TO gemini_user;
\q
```

5. Create `.env`
```
FLASK_ENV=development
FLASK_PORT=5000
DATABASE_URL=postgresql://gemini_user:your_password@localhost:5432/gemini_chat
JWT_SECRET_KEY=your-long-random-jwt-secret
SECRET_KEY=your-long-random-flask-secret
FRONTEND_URL=http://localhost:3000
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

6. Start the server
```bash
python run.py
```

Tables are created automatically on first run.

---

## API Reference

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|--------------|-------------|
| POST | `/auth/register` | No | Create account with email/password |
| POST | `/auth/login` | No | Login, returns JWT token |
| GET | `/auth/google` | No | Redirect to Google login |
| GET | `/auth/google/callback` | No | Google OAuth callback |
| GET | `/auth/me` | Yes | Get current user info |

### Chat Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|--------------|-------------|
| GET | `/chats` | Yes | Get all chats for current user |
| POST | `/chats` | Yes | Create a new chat |
| PUT | `/chats/:id` | Yes | Update an existing chat |
| DELETE | `/chats/:id` | Yes | Delete a chat |

All protected endpoints require:
```
Authorization: Bearer <jwt_token>
```

### Example Requests

**Register**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'
```

**Login**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'
```

**Get Chats**
```bash
curl http://localhost:5000/api/chats \
  -H "Authorization: Bearer <your_token>"
```

---

## Security

- Passwords are hashed with bcrypt — never stored in plain text
- JWTs are signed with a secret key — cannot be forged without the key
- Every chat endpoint filters by `user_id` — users can never access each other's data
- CORS is restricted to the configured frontend URL only
- Debug mode is disabled in production — no internal errors exposed to users
- Secret keys are environment variables — never hardcoded or committed to GitHub

---

## Development vs Production

| Setting | Development | Production |
|---------|------------|------------|
| `FLASK_ENV` | `development` | `production` |
| Debug mode | On | Off |
| `DATABASE_URL` | Local PostgreSQL | Render PostgreSQL |
| `FRONTEND_URL` | `localhost:3000` | Vercel URL |
| Server | `python run.py` | Gunicorn via Procfile |
| Secret keys | Simple strings | Long random strings |

---

## Deployment (Render)

1. Push your repo to GitHub (`.env` is gitignored — never committed)

2. Go to [render.com](https://render.com)

3. Create a PostgreSQL database
   - **New** → **PostgreSQL** → free tier
   - Copy the **Internal Database URL**

4. Create a Web Service
   - **New** → **Web Service** → connect your GitHub repo
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 4 "app:create_app()"`

5. Add environment variables in Render dashboard
```
FLASK_ENV=production
DATABASE_URL=<Internal Database URL from step 3>
JWT_SECRET_KEY=<long random string>
SECRET_KEY=<different long random string>
FRONTEND_URL=https://your-app.vercel.app
GOOGLE_CLIENT_ID=<from Google Cloud Console>
GOOGLE_CLIENT_SECRET=<from Google Cloud Console>
```

6. Add production callback URL in Google Cloud Console
```
https://your-backend.onrender.com/api/auth/google/callback
```

7. Update `NEXT_PUBLIC_API_URL` in your Vercel frontend to:
```
https://your-backend.onrender.com/api
```

---

## Swapping the Database

This is the pluggable architecture in action. To switch databases:

1. Install the new driver
```bash
# MySQL
pip install pymysql

# SQLite (no install needed)
```

2. Change one line in `app/database.py`
```python
# PostgreSQL (current)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

# SQLite (development/testing)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chats.db"

# MySQL
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:pass@host/db"
```

3. Update `requirements.txt`
```bash
pip freeze > requirements.txt
```

Every model, every route, every query stays identical.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | Yes | `development` or `production` |
| `FLASK_PORT` | No | Port to run on (default 5000) |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `JWT_SECRET_KEY` | Yes | Signs JWT tokens — keep secret |
| `SECRET_KEY` | Yes | Encrypts Flask sessions — keep secret |
| `FRONTEND_URL` | Yes | Allowed CORS origin |
| `GOOGLE_CLIENT_ID` | Yes | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Yes | From Google Cloud Console |

---

## Related

- [Chatbot](https://github.com/aliaayaghi/Chatbot) — Next.js frontend

---

## Future Improvements

- [ ] Token refresh — prevent users from being logged out every hour
- [ ] Pagination on `GET /chats` — handle large chat histories
- [ ] Search endpoint — `GET /chats?search=keyword`
- [ ] Database migrations with Alembic
- [ ] Rate limiting on auth endpoints with Flask-Limiter
- [ ] Email verification on registration
- [ ] Move tokens to httpOnly cookies for better XSS protection

---

## License

MIT
