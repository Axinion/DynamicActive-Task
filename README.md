# K12 LMS

A modern Learning Management System built for K-12 education with AI-powered features for personalized learning and automated grading.

## Tech Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + TailwindCSS
- **Backend**: FastAPI + Python 3.11+ + SQLite
- **AI/ML**: sentence-transformers for embeddings and content recommendations
- **Database**: SQLite with SQLAlchemy ORM
- **Development**: Docker Compose for local development

## Features

- **Role-based Access**: Separate dashboards for teachers and students
- **Class Management**: Create classes, generate invite codes, manage enrollments
- **Content Creation**: Build lessons and assignments with skill tagging
- **AI Grading**: Automated scoring for short-answer questions with explanations
- **Smart Recommendations**: AI-powered lesson suggestions based on student progress
- **Real-time Analytics**: Track student performance and engagement

## Getting Started

### Prerequisites

- Node.js 18+ (see `.nvmrc` in frontend)
- Python 3.11+
- Docker & Docker Compose (optional)

### Quick Start with Docker

```bash
# Clone and start all services
git clone <repo-url>
cd k12-lms
docker compose up
```

Visit `http://localhost:3000` for the frontend and `http://localhost:8000/docs` for the API documentation.

### Manual Setup

#### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

#### Database Seeding

```bash
# From backend directory with venv activated
python ../db/seed.py
```

This will create demo data including:
- Teacher account: `teacher@example.com` / `pass`
- Student account: `student@example.com` / `pass`
- Sample class with lessons and assignments
- Test submissions and responses

### Demo Credentials

After seeding the database, you can use these credentials:

- **Teacher**: `teacher@example.com` / `pass`
- **Student**: `student@example.com` / `pass`

## Project Structure

```
k12-lms/
├── frontend/          # Next.js + Tailwind frontend
├── backend/           # FastAPI + SQLite backend
├── db/               # Database migrations and seeds
├── tests/            # Backend tests
├── docker-compose.yml # Development environment
└── README.md
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Development

- Frontend runs on `http://localhost:3000`
- Backend API runs on `http://localhost:8000`
- CORS is configured for local development
- Hot reloading enabled for both frontend and backend

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
