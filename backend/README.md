# K12 LMS Backend

A FastAPI backend for the K12 Learning Management System with AI-powered features.

## Prerequisites

- Python 3.11+
- pip

## Getting Started

### Installation

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

### Development

Run the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

- Interactive docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## Environment Variables

Create a `.env` file with the following variables:

```env
DATABASE_URL=sqlite:///./k12.db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Database Setup

### Seeding Data

Run the seeding script to populate the database with demo data:

```bash
python ../db/seed.py
```

This will create:
- Demo teacher and student accounts
- Sample class with lessons and assignments
- Test data for development

### Demo Credentials

- **Teacher**: `teacher@example.com` / `pass`
- **Student**: `student@example.com` / `pass`

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Classes
- `GET /api/classes` - Get user's classes
- `POST /api/classes` - Create new class (teacher only)
- `POST /api/classes/join` - Join class with invite code (student only)
- `GET /api/classes/{id}/invite` - Get class invite code (teacher only)

### Lessons
- `GET /api/lessons` - Get lessons
- `POST /api/lessons` - Create lesson (teacher only)
- `GET /api/lessons/{id}` - Get specific lesson

### Assignments
- `GET /api/assignments` - Get assignments
- `POST /api/assignments` - Create assignment (teacher only)
- `GET /api/assignments/{id}` - Get specific assignment
- `POST /api/assignments/{id}/submit` - Submit assignment (student only)

### AI Features
- `POST /api/grading/short-answer` - Grade short answer (teacher only)
- `GET /api/recommendations` - Get lesson recommendations

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with PassLib
- **AI/ML**: sentence-transformers for embeddings
- **Validation**: Pydantic for data validation

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── security.py      # Authentication & security
│   ├── db/
│   │   ├── base.py          # Database base class
│   │   ├── models.py        # SQLAlchemy models
│   │   └── session.py       # Database session
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # AI and business logic services
│   └── main.py              # FastAPI application
├── requirements.txt
└── README.md
```

## CORS Configuration

The backend is configured to accept requests from `http://localhost:3000` (frontend URL) for development.

## Development Notes

- Uses SQLite for simplicity in development
- JWT tokens for stateless authentication
- AI services are placeholder implementations ready for enhancement
- All endpoints require authentication except login
- Role-based access control (teacher/student permissions)
