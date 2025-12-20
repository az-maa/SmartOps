# Smart OPS Backend

Backend API for Smart OPS - Server Monitoring Platform

## 🏗️ Architecture

```
smartops-backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Domain models
│   ├── schemas/             # Pydantic schemas (API contracts)
│   ├── controllers/         # API route handlers
│   ├── services/            # Business logic
│   ├── repositories/        # Database access layer
│   ├── core/                # Core utilities (security, dependencies)
│   └── database/            # Database connection
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Supabase

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Copy your project URL and keys
3. Create `.env` file:

```bash
cp .env.example .env
```

4. Edit `.env` with your Supabase credentials:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
SECRET_KEY=generate-random-key-here
```

**To generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Run the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: http://localhost:8000

- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## 📝 API Endpoints

### Authentication

#### Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

# Response: Same as register
```

#### Get Current User
```bash
GET /api/auth/me
Authorization: Bearer <your-token>

# Response
{
  "id": "uuid-here",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🧪 Testing with Postman/cURL

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Login (save the token)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Get User Info (use token from step 2)

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 Database Schema (Supabase)

The database tables are already created in your Supabase project:

- **users** - User accounts
- **servers** - Monitored servers
- **metrics** - Time-series metrics data
- **anomalies** - Detected anomalies
- **predictions** - AI predictions

## 🔄 Development Workflow

### Adding a New Entity (e.g., Server)

1. **Create Model** (`app/models/server.py`)
   - Define domain model with Pydantic

2. **Create Schemas** (`app/schemas/server.py`)
   - Define request/response schemas

3. **Create Repository** (`app/repositories/server_repository.py`)
   - Implement database operations

4. **Create Service** (`app/services/server_service.py`)
   - Implement business logic

5. **Create Controller** (`app/controllers/server_controller.py`)
   - Define API routes

6. **Register Router** (in `app/main.py`)
   - Add router to FastAPI app

## 🎯 Next Steps

- [ ] ✅ User authentication (DONE)
- [ ] Implement Server CRUD
- [ ] Implement Metrics endpoints
- [ ] Implement Anomaly detection integration
- [ ] Implement Predictions endpoints
- [ ] Add input validation
- [ ] Add rate limiting
- [ ] Add logging
- [ ] Write tests

## 🐛 Troubleshooting

### Common Issues

**ModuleNotFoundError**
```bash
# Make sure you're in the right directory and venv is activated
pip install -r requirements.txt
```

**Supabase Connection Error**
- Check your `.env` file has correct credentials
- Verify Supabase project is active
- Check RLS policies are set correctly

**Import Errors**
```bash
# Run from project root:
python -m uvicorn app.main:app --reload
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 🤝 Team Communication

- Daily standup in group chat
- Integration meetings: Days 8, 11, 14
- Block time: Max 30 min before asking for help