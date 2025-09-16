# 🎓 K12 LMS

**A modern Learning Management System with AI-powered grading, personalized insights, and comprehensive analytics for K-12 education.**

## ✨ Features

- **🤖 AI-Powered Grading**: Semantic analysis and keyword matching for short-answer questions
- **📊 Advanced Analytics**: Misconception clustering, skill mastery tracking, and progress visualization
- **🎯 Personalized Recommendations**: AI-driven learning paths and mini-lesson suggestions
- **👨‍🏫 Teacher Tools**: Gradebook management, score overrides, and comprehensive insights
- **👨‍🎓 Student Experience**: Interactive lessons, immediate feedback, and progress tracking
- **📈 Real-time Insights**: Time-based analysis with weekly/monthly period filtering
- **📤 Data Export**: CSV export functionality for gradebook data
- **🎮 Demo Mode**: Interactive walkthrough with contextual tips and guidance

## 🛠 Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Python 3.11+
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **AI/ML**: Sentence Transformers, KMeans clustering, semantic embeddings
- **Authentication**: JWT tokens with role-based access control
- **Testing**: Pytest, comprehensive smoke tests, and E2E validation

## 🚀 Quickstart (90 seconds)

### 1. Backend Setup (30 seconds)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Seed Database (15 seconds)
```bash
# In a new terminal
cd backend
python -m db.seed
```

### 3. Frontend Setup (30 seconds)
```bash
# In a new terminal
cd frontend
npm install
npm run dev
```

### 4. Access the Application (15 seconds)
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎮 Demo Credentials

### Teacher Account
- **Email**: `teacher@example.com`
- **Password**: `pass`
- **Access**: Create classes, lessons, assignments, view insights, manage gradebook

### Student Accounts
- **Email**: `student@example.com` / **Password**: `pass`
- **Email**: `student2@example.com` / **Password**: `pass`
- **Email**: `student3@example.com` / **Password**: `pass`
- **Access**: Join classes, take assignments, view progress, get recommendations

## 🔗 Important URLs

- **Homepage**: http://localhost:3000
- **Teacher Dashboard**: http://localhost:3000/teacher
- **Student Dashboard**: http://localhost:3000/student
- **API Health**: http://localhost:8000/api/health
- **API Version**: http://localhost:8000/api/version
- **API Documentation**: http://localhost:8000/docs

## ⚠️ Known Limits

- **AI Model**: Uses local sentence-transformers model (may require internet for first download)
- **Database**: SQLite for development (not suitable for production scale)
- **File Storage**: Local file system (no cloud storage integration)
- **Real-time**: No WebSocket support (polling-based updates)
- **Mobile**: Responsive design but not mobile-optimized
- **Offline**: No offline functionality

## 📋 Implementation Phases

### ✅ Phase 1: Core Foundation
- [x] **Authentication & Authorization**: JWT-based auth with role management
- [x] **Database Models**: Users, classes, lessons, assignments, submissions
- [x] **Basic CRUD**: Create, read, update, delete operations
- [x] **API Structure**: RESTful endpoints with proper error handling

### ✅ Phase 2: AI Integration
- [x] **Embedding Service**: Sentence transformers for semantic analysis
- [x] **AI Grading**: Short-answer scoring with keyword matching
- [x] **Feedback Generation**: Automated feedback for student responses
- [x] **Score Calculation**: MCQ and short-answer scoring algorithms

### ✅ Phase 3: Advanced Features
- [x] **Teacher Overrides**: Manual score adjustment with audit trail
- [x] **Personalized Recommendations**: AI-driven learning path suggestions
- [x] **Gradebook Management**: Comprehensive submission tracking
- [x] **Content Management**: Rich lesson creation with skill tags

### ✅ Phase 4: Analytics & Insights
- [x] **Misconception Clustering**: KMeans clustering of low-scoring responses
- [x] **Skill Mastery Tracking**: Per-skill progress monitoring (0-1 scale)
- [x] **Mini-Lesson Suggestions**: Tag-based lesson recommendations
- [x] **Time-Based Analysis**: Weekly/monthly period filtering
- [x] **Progress Visualization**: Interactive charts and badges

### ✅ Phase 5: Polish & Production
- [x] **UX Polish**: Loading skeletons, error boundaries, toast notifications
- [x] **Accessibility**: ARIA attributes, keyboard navigation, focus management
- [x] **Design Tokens**: Semantic colors, consistent spacing, component variants
- [x] **Logging & Security**: Request logging, rate limiting, exception handling
- [x] **Demo Mode**: Interactive walkthrough with contextual tips
- [x] **CSV Export**: Gradebook data export functionality
- [x] **Testing**: Comprehensive health, version, and smoke tests

## 🐳 Docker Support

### Quick Docker Setup
```bash
# Build and start all services
docker compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Docker Services
- **api**: FastAPI backend on port 8000
- **web**: Next.js frontend on port 3000
- **Database**: SQLite volume mount for persistence

### Docker Commands
```bash
# Start services
docker compose up

# Start in background
docker compose up -d

# Stop services
docker compose down

# Rebuild and start
docker compose up --build

# View logs
docker compose logs -f
```

## 📚 Documentation

- **[Demo Script](docs/DEMO_SCRIPT.md)**: 5-7 minute narrated walkthrough
- **[Smoke Tests](docs/smoke-phase5.md)**: Comprehensive E2E testing guide
- **[Insights Guide](docs/insights.md)**: Teacher and student analytics guide
- **[API Documentation](http://localhost:8000/docs)**: Interactive API reference

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test

# Smoke tests (manual)
# Follow docs/smoke-phase5.md
```

### Test Coverage
- **Unit Tests**: API endpoints, business logic, data models
- **Integration Tests**: Database operations, authentication flows
- **Smoke Tests**: End-to-end user workflows
- **Performance Tests**: Response times, concurrent requests

## 🚀 Production Deployment

### Environment Variables
```bash
# Backend (.env)
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/k12_lms
ALLOWED_ORIGIN=https://yourdomain.com
API_VERSION=1.0.0
ENVIRONMENT=production

# Frontend (.env.local)
NEXT_PUBLIC_API_BASE=https://api.yourdomain.com/api
NEXT_PUBLIC_ENVIRONMENT=production
```

### Production Checklist
- [ ] Use PostgreSQL database
- [ ] Set secure SECRET_KEY
- [ ] Configure CORS for production domain
- [ ] Set up SSL certificates
- [ ] Configure reverse proxy (nginx)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Check the docs/ folder for detailed guides
- **API Reference**: Visit http://localhost:8000/docs for API documentation

---

**🎉 Ready to revolutionize K-12 education with AI-powered learning!**