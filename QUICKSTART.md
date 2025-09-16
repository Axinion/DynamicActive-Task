# 🚀 K12 LMS - Quick Start Guide

## ✅ **Current Status**
- ✅ Backend: Working (http://localhost:8000)
- ✅ Frontend: Working (http://localhost:3000)
- ✅ Database: Seeded with demo data
- ✅ All issues resolved

## 🎯 **How to Run**

### **Option 1: Manual Start (Recommended)**

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### **Option 2: Docker (Alternative)**
```bash
./docker-setup.sh
```

## 🔑 **Login Credentials**

**Teacher:**
- Email: `teacher@example.com`
- Password: `pass`

**Students:**
- Email: `student@example.com` / Password: `pass`
- Email: `student2@example.com` / Password: `pass`
- Email: `student3@example.com` / Password: `pass`

## 🌐 **Access URLs**
- **Application**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **API Health**: http://localhost:8000/api/health

## 🎮 **What You Can Do**

### **As a Teacher:**
1. Login with `teacher@example.com` / `pass`
2. View existing classes (Biology 101, Mathematics 201)
3. Create new lessons and assignments
4. View student submissions and grades
5. Access analytics and insights
6. Export gradebook as CSV

### **As a Student:**
1. Login with `student@example.com` / `pass`
2. Join classes using invite codes (BIO123, MATH456)
3. Take assignments and get AI feedback
4. View your progress and skill mastery
5. Get personalized recommendations

## 🛠️ **Troubleshooting**

**Backend not starting?**
- Make sure you're in the `backend` directory
- Activate virtual environment: `source .venv/bin/activate`
- Check if port 8000 is free

**Frontend not starting?**
- Make sure you're in the `frontend` directory
- Run `npm install` if needed
- Check if port 3000 is free

**Login not working?**
- Make sure backend is running on port 8000
- Check browser console for errors
- Try refreshing the page

## 🎉 **You're Ready!**

The application is fully functional with:
- ✅ AI-powered grading
- ✅ Teacher insights and analytics
- ✅ Student progress tracking
- ✅ CSV export functionality
- ✅ Demo mode with guided tips

**Happy Learning! 🎓**
