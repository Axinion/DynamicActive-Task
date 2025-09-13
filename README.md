# K12 LMS

A modern Learning Management System built for K-12 education with AI-powered features for personalized learning and automated grading.

## 🚀 Phase 1 - Complete!

**Authentication, Class Management, and Core User Flows are fully implemented and tested.**

### ✅ What's Working

- **🔐 JWT Authentication**: Secure login with token-based auth
- **👨‍🏫 Teacher Dashboard**: Create classes, generate invite codes, manage enrollments
- **👨‍🎓 Student Dashboard**: Join classes with invite codes, view enrolled classes
- **🔄 Real-time Updates**: Class lists refresh automatically after actions
- **📱 Responsive UI**: Works on desktop and mobile devices
- **🧪 Comprehensive Testing**: Full end-to-end smoke tests

## Tech Stack

- **Frontend**: Next.js 15 (App Router) + TypeScript + TailwindCSS + Zustand
- **Backend**: FastAPI + Python 3.13+ + SQLite + JWT Authentication
- **Database**: SQLite with SQLAlchemy ORM
- **Testing**: pytest + FastAPI TestClient
- **Development**: Docker Compose for local development

## 🎯 Core Features (Phase 1)

- **🔐 JWT Authentication**: Secure login with automatic token management
- **👥 Role-based Access**: Separate dashboards for teachers and students
- **🏫 Class Management**: Create classes, generate unique invite codes
- **📝 Student Enrollment**: Join classes using invite codes
- **🔄 Real-time Updates**: Automatic list refresh after actions
- **📱 Modern UI**: Clean, responsive design with loading states
- **🧪 Comprehensive Testing**: Full end-to-end smoke tests

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** (see `.nvmrc` in frontend)
- **Python 3.13+** (or 3.11+)
- **Docker & Docker Compose** (optional)

### 🎯 Demo Credentials

**Ready to use after seeding:**

- **👨‍🏫 Teacher**: [teacher@example.com](mailto:teacher@example.com) / `pass`
- **👨‍🎓 Student**: [student@example.com](mailto:student@example.com) / `pass`

### 🔧 Development Commands

#### Backend Setup & Run

```bash
# Setup
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup & Run

```bash
# Setup
cd frontend
npm install

# Run
npm run dev
```

#### Database Seeding

```bash
# Option 1: Use convenience script (from project root)
./make_seed.sh

# Option 2: Manual seeding (from backend directory with venv activated)
python ../db/seed.py
```

**Seeding creates:**
- Demo teacher and student accounts
- Sample class with invite code
- Ready-to-use test data

### 🐳 Docker Setup (Alternative)

```bash
# Clone and start all services
git clone <repo-url>
cd k12-lms
docker compose up
```

Visit `http://localhost:3000` for frontend and `http://localhost:8000/docs` for API docs.

## 🔄 User Flows

### 🔐 Authentication Flow

1. **Login**: Enter credentials → JWT token stored locally
2. **Auto-restore**: Token automatically restored on page refresh via `/auth/me`
3. **Role-based Redirect**: Teachers → `/teacher`, Students → `/student`
4. **Protected Routes**: Unauthenticated users redirected to `/login`

### 👨‍🏫 Teacher Flow

1. **Create Class**: Click "Create Class" → Enter class name
2. **Get Invite Code**: Modal shows unique invite code (e.g., `ABC123`)
3. **Share Code**: Copy code and share with students
4. **View Classes**: See all created classes with student counts
5. **Manage**: View and manage class enrollments

### 👨‍🎓 Student Flow

1. **Join Class**: Enter invite code in "Join a Class" form
2. **Success**: Toast notification "Joined!" appears
3. **View Classes**: See all enrolled classes
4. **Ready to Learn**: Access class content and assignments

## 🧪 Testing

### Run Comprehensive Smoke Tests

```bash
# Run all tests with detailed output
./run_tests.sh

# Or run directly
cd backend && source .venv/bin/activate && python3 ../tests/test_auth_and_classes_flow.py
```

**Tests cover:**
- ✅ Teacher login → Class creation → Invite code generation
- ✅ Student login → Class joining → Enrollment verification
- ✅ Error scenarios (invalid credentials, unauthorized access)
- ✅ JWT authentication and token validation
- ✅ Data persistence and relationship integrity

## 🛠️ Troubleshooting

### Common Issues

#### **CORS Errors**
- **Problem**: Frontend can't connect to backend
- **Solution**: Ensure backend is running on `http://localhost:8000`
- **Check**: Backend logs for CORS configuration

#### **Missing Environment Variables**
- **Problem**: Backend fails to start
- **Solution**: Copy `.env.example` to `.env` in backend directory
- **Required**: `SECRET_KEY` and `ACCESS_TOKEN_EXPIRE_MINUTES`

#### **Invalid Invite Code**
- **Problem**: Student can't join class
- **Solution**: Verify invite code is correct (case-sensitive, 6-8 characters)
- **Check**: Teacher dashboard shows current invite code

#### **Database Issues**
- **Problem**: Tables not created or data missing
- **Solution**: Run `./make_seed.sh` to recreate database and seed data
- **Check**: Ensure SQLite file `k12.db` exists in project root

#### **Frontend Build Errors**
- **Problem**: TypeScript or build errors
- **Solution**: Run `npm run build` in frontend directory to see detailed errors
- **Check**: Ensure all dependencies are installed with `npm install`

### Development URLs

- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

## 📁 Project Structure

```
k12-lms/
├── frontend/              # Next.js 15 + TypeScript + Tailwind
│   ├── app/              # App Router pages and layouts
│   ├── components/       # Reusable UI components
│   ├── lib/             # API clients and utilities
│   └── package.json     # Frontend dependencies
├── backend/              # FastAPI + SQLite backend
│   ├── app/             # FastAPI application
│   │   ├── api/         # API routes and endpoints
│   │   ├── core/        # Security and configuration
│   │   ├── db/          # Database models and session
│   │   └── schemas/     # Pydantic models
│   └── requirements.txt # Backend dependencies
├── db/                   # Database migrations and seeds
│   └── seed.py          # Demo data seeding script
├── tests/                # Backend tests
│   ├── test_auth_and_classes_flow.py  # Comprehensive smoke tests
│   └── requirements.txt # Test dependencies
├── docker-compose.yml    # Development environment
├── make_seed.sh         # Database seeding convenience script
├── run_tests.sh         # Test execution convenience script
└── README.md            # This file
```

## 🔮 Future Features (Phase 2+)

- **📚 Content Creation**: Lessons and assignments with rich text editor
- **🤖 AI Grading**: Automated scoring for short-answer questions
- **📊 Analytics**: Student performance tracking and insights
- **💬 Communication**: Teacher-student messaging and announcements
- **📱 Mobile App**: React Native mobile application
- **🔔 Notifications**: Real-time updates and alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run tests: `./run_tests.sh`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

---

**🎉 Phase 1 Complete!** The K12 LMS now has a solid foundation with authentication, class management, and core user flows. Ready for Phase 2 development!
