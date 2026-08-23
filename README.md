# Knora Authentication Backend

High-performance, modular, production-ready authentication microservice for **Knora** built with Python 3.11+, FastAPI, Pydantic v2, and MongoDB (async Motor driver).

---

## Features

- **Authentication Methods**:
  - Email + Password (`POST /api/auth/login/email-password`)
  - Mobile + Password (`POST /api/auth/login/mobile-password`)
  - Email + 6-digit OTP (`POST /api/auth/login/email-otp/send`, `verify`)
  - Mobile + 6-digit OTP (`POST /api/auth/login/mobile-otp/send`, `verify`)
  - Google OAuth 2.0 / OpenID Connect (`GET /api/auth/google/login`, `callback`)
- **Signup & Verification**:
  - Full registration flow (`POST /api/auth/signup`)
  - Email & Mobile OTP verification (`POST /api/auth/verification/...`)
  - Input normalization (email lowercase, E.164 phone formatting, name trimming)
- **Security & Tokens**:
  - Argon2id password hashing via `argon2-cffi`
  - JWT access tokens (short-lived) + Refresh token rotation stored in MongoDB
  - Single-use OTP tokens with TTL expiration and attempt limits
  - User enumeration & brute-force protection
- **Architecture**:
  - Layered separation (`Route -> Service -> Repository -> MongoDB`)
  - Provider abstractions (`EmailProvider`, `SmsProvider`)
  - OpenAPI standard response envelopes

---

## Local Development Instructions

### 1. Requirements

- Python 3.11+
- MongoDB running at `mongodb://localhost:27017/`

### 2. Setup Virtual Environment & Install Dependencies

```bash
cd knora-backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Open interactive API documentation in your browser:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 5. Running Automated Tests

```bash
pytest -v tests/
```
