# K12 LMS

A modern Learning Management System built for K-12 education with AI-powered features for personalized learning and automated grading.

## 🚀 Phase 2 - Complete!

**Content Creation, Assignment Management, and Automated Grading are fully implemented and tested.**

### ✅ What's Working

- **🔐 JWT Authentication**: Secure login with token-based auth
- **👨‍🏫 Teacher Dashboard**: Create classes, lessons, and assignments with multiple question types
- **👨‍🎓 Student Dashboard**: Join classes, read lessons, and take assignments with immediate feedback
- **📚 Content Management**: Rich lesson creation with skill tags and structured content
- **📝 Assignment Builder**: Create quizzes with MCQ and short-answer questions
- **🤖 Auto-Grading**: Immediate MCQ scoring with detailed feedback
- **📊 Gradebook**: Teacher view of all student submissions and scores
- **🔄 Real-time Updates**: Class lists and content refresh automatically
- **📱 Responsive UI**: Works on desktop and mobile devices
- **🧪 Comprehensive Testing**: Full end-to-end smoke tests and flow validation

## Tech Stack

- **Frontend**: Next.js 15 (App Router) + TypeScript + TailwindCSS + Zustand
- **Backend**: FastAPI + Python 3.13+ + SQLite + JWT Authentication
- **Database**: SQLite with SQLAlchemy ORM
- **Testing**: pytest + FastAPI TestClient
- **Development**: Docker Compose for local development

## 🎯 Core Features (Phase 2)

### 🔐 Authentication & Access
- **JWT Authentication**: Secure login with automatic token management
- **Role-based Access**: Separate dashboards for teachers and students
- **Protected Routes**: Automatic redirection based on authentication status

### 🏫 Class Management
- **Class Creation**: Teachers create classes with unique invite codes
- **Student Enrollment**: Students join classes using invite codes
- **Class Navigation**: Tabbed interface (Overview, Lessons, Assignments, Gradebook)

### 📚 Content Creation (Teachers)
- **Lesson Builder**: Create lessons with title, content, and skill tags
- **Assignment Builder**: Create quizzes with multiple question types:
  - **MCQ Questions**: Multiple choice with options and correct answer
  - **Short Answer**: Open-ended questions with rubric keywords
- **Question Management**: Add/remove questions dynamically
- **Due Dates**: Optional assignment deadlines

### 👨‍🎓 Student Experience
- **Lesson Reading**: View lessons with structured content and skill tags
- **Assignment Taking**: Interactive assignment interface:
  - **MCQ Interface**: Radio button selection for multiple choice
  - **Short Answer**: Text area for open-ended responses
- **Immediate Feedback**: MCQ questions graded instantly with correct/incorrect indicators
- **Submission Results**: View scores and feedback after submission

### 🤖 Automated Grading
- **MCQ Auto-Grading**: Immediate scoring with 100% or 0% per question
- **Score Calculation**: Overall assignment score based on MCQ questions only
- **Short Answer Storage**: Stored for teacher review (Phase 3: AI grading)
- **Detailed Breakdown**: Per-question scoring and feedback

### 📊 Gradebook (Teachers)
- **Submission Overview**: View all student submissions for a class
- **Score Tracking**: AI scores and teacher scores side-by-side
- **Response Review**: Click to view detailed student responses
- **Sorting & Filtering**: Sort by submission date, student, or assignment

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** (see `.nvmrc` in frontend)
- **Python 3.13+** (or 3.11+)
- **Docker & Docker Compose** (optional)

### 🎯 Demo Credentials

**Ready to use after seeding:**

- **👨‍🏫 Teacher**: [teacher@example.com](mailto:teacher@example.com) / `pass`
- **👨‍🎓 Student**: [student@example.com](mailto:student@example.com) / `pass`

**Demo Class Invite Code**: `ABC123` (displayed after seeding)

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
- Sample class with invite code (`ABC123`)
- **2 Demo Lessons**:
  - "Introduction to Python" - Basic programming concepts
  - "Data Structures in Python" - Lists, tuples, and dictionaries
- **1 Demo Quiz Assignment**:
  - MCQ: "What is the correct way to create a list in Python?" (4 options)
  - Short Answer: "Explain the difference between a list and a tuple"
- Ready-to-use test data for immediate exploration

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
4. **Access Invite Code Later**: 
   - Go to class overview page (`/teacher/classes/{id}`)
   - Invite code displayed with copy button
   - Also available in class list on main dashboard
5. **Create Content**: 
   - **Lessons**: Add lessons with title, content, and skill tags
   - **Assignments**: Build quizzes with MCQ and short-answer questions
6. **Monitor Progress**: View gradebook with student submissions and scores
7. **Manage Classes**: Access class details via tabbed navigation

### 👨‍🎓 Student Flow

1. **Join Class**: Enter invite code in "Join a Class" form
2. **Success**: Toast notification "Joined!" appears
3. **Access Content**:
   - **Read Lessons**: View lesson content with skill tags
   - **Take Assignments**: Complete quizzes with immediate MCQ feedback
4. **View Results**: 
   - **MCQ Questions**: Immediate scoring (100% or 0% per question)
   - **Short Answer**: "Awaiting Grading" status (Phase 3: AI grading)
5. **Track Progress**: Monitor completed assignments and scores

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login` - User login with email/password
- `GET /api/auth/me` - Get current user information

### Classes
- `POST /api/classes` - Create new class (teacher only)
- `GET /api/classes` - List classes (role-based: owned vs enrolled)
- `POST /api/classes/join` - Join class with invite code (student only)
- `GET /api/classes/{id}/invite` - Get/regenerate invite code (teacher only)

### Lessons
- `POST /api/lessons` - Create lesson (teacher only)
- `GET /api/lessons?class_id={id}` - List lessons for class
- `GET /api/lessons/{id}` - Get specific lesson details

### Assignments
- `POST /api/assignments` - Create assignment with questions (teacher only)
- `GET /api/assignments?class_id={id}` - List assignments for class
- `GET /api/assignments/{id}` - Get assignment with questions
- `POST /api/assignments/{id}/submit` - Submit assignment (student only)

### Gradebook
- `GET /api/gradebook?class_id={id}` - Get submissions for class (teacher only)

## 🧪 Testing

### Automated Tests

```bash
# Run all automated tests with detailed output
./run_tests.sh

# Or run directly
cd backend && source .venv/bin/activate && python3 ../tests/test_auth_and_classes_flow.py
```

### Manual Smoke Tests

For comprehensive manual testing of Phase 2 features, see the detailed smoke test script:

📋 **[Phase 2 Manual Smoke Test Script](docs/smoke-phase2.md)**

This script covers:
- Teacher content creation (lessons and assignments)
- Student content access and submission
- MCQ auto-grading verification
- Short answer "awaiting grading" status
- Gradebook functionality

**Tests cover:**
- ✅ **Phase 1**: Teacher login → Class creation → Invite code generation
- ✅ **Phase 1**: Student login → Class joining → Enrollment verification
- ✅ **Phase 2**: Teacher creates lessons → Student accesses content
- ✅ **Phase 2**: Teacher creates assignments → Student submits → Auto-grading
- ✅ **MCQ Auto-Grading**: Correct/incorrect answer scoring verification
- ✅ **Short Answer Storage**: Proper storage with null scores awaiting grading
- ✅ **Error scenarios**: Invalid credentials, unauthorized access, validation errors
- ✅ **JWT authentication**: Token validation and role-based access control
- ✅ **Data persistence**: Relationship integrity and proper data storage

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
├── docs/                 # Documentation
│   └── smoke-phase2.md  # Manual smoke test script for Phase 2
├── tests/                # Backend tests
│   ├── test_auth_and_classes_flow.py  # Phase 1 comprehensive smoke tests
│   ├── test_lessons_flow.py          # Phase 2 lessons flow tests
│   ├── test_assignments_flow.py      # Phase 2 assignments flow tests
│   └── requirements.txt # Test dependencies
├── docker-compose.yml    # Development environment
├── make_seed.sh         # Database seeding convenience script
├── run_tests.sh         # Test execution convenience script
└── README.md            # This file
```

## 🔮 Future Features (Phase 3+)

- **🤖 AI Grading**: Automated scoring for short-answer questions using LLM
- **📊 Advanced Analytics**: Student performance tracking and insights
- **💬 Communication**: Teacher-student messaging and announcements
- **📱 Mobile App**: React Native mobile application
- **🔔 Notifications**: Real-time updates and alerts
- **🎯 Adaptive Learning**: Personalized content recommendations
- **📈 Progress Tracking**: Detailed learning analytics and reports

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

**🎉 Phase 2 Complete!** The K12 LMS now has a comprehensive learning platform with content creation, assignment management, automated grading, and gradebook functionality. Ready for Phase 3 AI-powered features!
