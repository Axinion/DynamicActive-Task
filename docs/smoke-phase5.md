# 🧪 K12 LMS Phase 5 Smoke Test Guide

This document provides a comprehensive step-by-step manual end-to-end (E2E) testing script for the K12 LMS Phase 5 features, including demo mode, CSV export, logging, and server hardening.

## 🎯 **Test Overview**

**Purpose**: Verify all Phase 5 features work correctly in an integrated environment
**Duration**: ~30-45 minutes
**Prerequisites**: 
- Backend server running on `http://localhost:8000`
- Frontend server running on `http://localhost:3000`
- Database seeded with demo data

## 📋 **Pre-Test Setup**

### 1. **Start Services**
```bash
# Terminal 1: Start Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev

# Terminal 3: Seed Database (if needed)
cd backend
python -m db.seed
```

### 2. **Verify Services**
- ✅ Backend: `http://localhost:8000/api/health` returns `{"status": "ok"}`
- ✅ Frontend: `http://localhost:3000` loads without errors
- ✅ Version: `http://localhost:8000/api/version` returns version info

## 🧪 **Smoke Test Script**

### **Phase 1: Authentication & Demo Mode**

#### **Step 1.1: Teacher Login**
1. Navigate to `http://localhost:3000`
2. Click "Sign In" or navigate to `/login`
3. Enter teacher credentials:
   - **Email**: `teacher@example.com`
   - **Password**: `pass`
4. Click "Sign In"
5. **Expected**: Redirected to teacher dashboard
6. **Verify**: Header shows "Demo Mode: OFF" toggle

#### **Step 1.2: Enable Demo Mode**
1. Click "Demo Mode: OFF" toggle in header
2. **Expected**: Toggle changes to "Demo Mode: ON"
3. **Verify**: Page reloads and demo mode is active
4. **Verify**: Floating demo tip appears (if on relevant screen)

#### **Step 1.3: Create Class**
1. Click "Create Class" button
2. **Expected**: Demo tip appears: "Create Your First Class"
3. Fill in class details:
   - **Name**: "Test Class for Smoke Test"
   - **Description**: "Testing Phase 5 features"
4. Click "Create Class"
5. **Expected**: Class created successfully
6. **Verify**: Invite code is displayed (e.g., "ABC123")
7. **Copy invite code** for later use

### **Phase 2: Student Registration & Quiz Taking**

#### **Step 2.1: Student Login**
1. Open new browser tab/incognito window
2. Navigate to `http://localhost:3000`
3. Click "Sign In"
4. Enter student credentials:
   - **Email**: `student@example.com`
   - **Password**: `pass`
5. Click "Sign In"
6. **Expected**: Redirected to student dashboard
7. **Verify**: Demo mode toggle is visible

#### **Step 2.2: Join Class**
1. Click "Join Class" or navigate to join class page
2. Enter the invite code from Step 1.3
3. Click "Join Class"
4. **Expected**: Successfully joined class
5. **Verify**: Class appears in student's class list

#### **Step 2.3: Take Quiz**
1. Navigate to the joined class
2. Click on an assignment/quiz
3. **Expected**: Demo tip appears: "Take a Quiz"
4. Answer questions:
   - **MCQ**: Select an answer
   - **Short Answer**: Type a response
5. Click "Submit Assignment"
6. **Expected**: Redirected to results page
7. **Verify**: MCQ result shows immediately
8. **Verify**: AI feedback is displayed for short answers
9. **Verify**: "See your progress" link is present

### **Phase 3: Teacher Management & Insights**

#### **Step 3.1: Create Lesson + Quiz**
1. Switch back to teacher tab
2. Navigate to the created class
3. Click "Create Lesson"
4. **Expected**: Demo tip appears: "Build an Assignment"
5. Fill in lesson details:
   - **Title**: "Smoke Test Lesson"
   - **Content**: "This is a test lesson for smoke testing"
   - **Skill Tags**: "testing, smoke_test"
6. Click "Create Lesson"
7. Click "Create Assignment"
8. Create a quiz with:
   - **Title**: "Smoke Test Quiz"
   - **1 MCQ Question**: "What is 2+2?" with options ["3", "4", "5", "6"]
   - **1 Short Answer**: "Explain the concept of testing"
9. Click "Create Assignment"
10. **Expected**: Assignment created successfully

#### **Step 3.2: View Gradebook**
1. Navigate to "Gradebook" tab
2. **Expected**: Student submission appears
3. **Verify**: "Export CSV" button is present
4. **Verify**: "View Insights" link is present
5. Click on a submission row
6. **Expected**: Side panel opens with submission details
7. **Verify**: Override functionality is available

#### **Step 3.3: Override Response**
1. In the submission detail panel
2. Click "Override" on a response
3. **Expected**: Override drawer opens
4. Change the score (e.g., from 85 to 90)
5. Add teacher feedback: "Good work, but could be more detailed"
6. Click "Save Override"
7. **Expected**: Override saved successfully
8. **Verify**: New score appears in gradebook
9. **Verify**: Toast notification shows success

### **Phase 4: Analytics & Insights**

#### **Step 4.1: View Insights**
1. Click "View Insights" link in gradebook header
2. **Expected**: Redirected to Insights tab
3. **Expected**: Demo tip appears: "View Insights"
4. **Verify**: "Top 3 misconceptions" section is present
5. **Verify**: Period switcher (Week/Month) is functional
6. **Verify**: Mini-lesson suggestions are displayed
7. **Verify**: Example student answers are shown
8. **Verify**: "Why am I seeing this?" tooltips are present

#### **Step 4.2: Test Insights Features**
1. Switch between "Week" and "Month" periods
2. **Expected**: Data updates based on selected period
3. Click on a mini-lesson suggestion
4. **Expected**: Lesson opens in new tab/window
5. **Verify**: Misconception clusters show proper labels and counts
6. **Verify**: Student answer examples are truncated with "Show more"

### **Phase 5: Student Progress & Recommendations**

#### **Step 5.1: Student Dashboard Progress**
1. Switch back to student tab
2. Navigate to student dashboard
3. **Expected**: Demo tip appears: "Track Progress"
4. **Verify**: Skill progress chart is displayed
5. **Verify**: Progress badges (STRONG, GROWING, NEEDS PRACTICE) are shown
6. **Verify**: "Practice next" CTA button is present
7. Click "Practice next"
8. **Expected**: Redirected to recommended lessons

#### **Step 5.2: Class Overview Progress**
1. Navigate to the joined class
2. **Verify**: Progress card is displayed with `id="progress"`
3. **Verify**: Skill progress chart shows mastery levels
4. **Verify**: Individual skill badges are displayed
5. **Verify**: "Why am I seeing this?" tooltip is present

### **Phase 6: CSV Export & File Download**

#### **Step 6.1: Export Gradebook CSV**
1. Switch back to teacher tab
2. Navigate to Gradebook
3. Click "Export CSV" button
4. **Expected**: File download starts automatically
5. **Verify**: Downloaded file is named `gradebook_class_{class_id}.csv`
6. **Verify**: File contains expected columns:
   - Submission ID, Student ID, Student Name, Student Email
   - Assignment ID, Assignment Title, Submitted At
   - AI Score, Teacher Score, Final Score, AI Explanation
7. Open the CSV file
8. **Verify**: Data matches what's shown in the gradebook
9. **Verify**: Override scores are reflected in the export

### **Phase 7: Demo Mode Features**

#### **Step 7.1: Demo Tips Navigation**
1. Ensure demo mode is enabled
2. Navigate through different screens:
   - Teacher dashboard → Create class tip
   - Assignments page → Build assignment tip
   - Student assignment → Take quiz tip
   - Insights page → View insights tip
   - Student dashboard → Track progress tip
3. **Verify**: Appropriate tips appear on each screen
4. **Verify**: Tips can be dismissed or navigated through
5. **Verify**: Dismissed tips don't reappear

#### **Step 7.2: Demo Mode Toggle**
1. Click "Demo Mode: ON" toggle
2. **Expected**: Toggle changes to "Demo Mode: OFF"
3. **Verify**: Page reloads and demo tips disappear
4. Toggle back to "Demo Mode: ON"
5. **Verify**: Demo tips reappear on relevant screens

### **Phase 8: Error Handling & Edge Cases**

#### **Step 8.1: Network Error Handling**
1. Stop the backend server
2. Try to perform an action (e.g., create class)
3. **Expected**: Error toast appears with appropriate message
4. **Verify**: UI remains functional
5. Restart backend server
6. **Verify**: Actions work normally again

#### **Step 8.2: Authentication Edge Cases**
1. Let session expire (wait or clear localStorage)
2. Try to access protected page
3. **Expected**: Redirected to login page
4. **Verify**: Session expired toast appears
5. Log in again
6. **Verify**: Redirected to appropriate page

#### **Step 8.3: Rate Limiting**
1. Rapidly click login button multiple times
2. **Expected**: Rate limiting kicks in after 5 attempts
3. **Verify**: HTTP 429 error with appropriate message
4. Wait 1 minute
5. **Verify**: Login works normally again

## ✅ **Test Completion Checklist**

### **Core Features**
- [ ] Teacher login and dashboard access
- [ ] Student login and dashboard access
- [ ] Class creation and invite code generation
- [ ] Student class joining with invite code
- [ ] Lesson and assignment creation
- [ ] Quiz taking with MCQ and short answers
- [ ] AI grading and feedback display
- [ ] Teacher score overrides
- [ ] Gradebook view and management

### **Analytics Features**
- [ ] Insights tab with misconception clustering
- [ ] Period switching (Week/Month)
- [ ] Mini-lesson suggestions
- [ ] Student progress tracking
- [ ] Skill mastery badges and charts
- [ ] Progress recommendations

### **Export Features**
- [ ] CSV export functionality
- [ ] File download with correct naming
- [ ] CSV data accuracy and completeness
- [ ] Override scores reflected in export

### **Demo Mode Features**
- [ ] Demo mode toggle functionality
- [ ] Floating tips on appropriate screens
- [ ] Tip navigation and dismissal
- [ ] Demo state persistence

### **Technical Features**
- [ ] Health endpoint functionality
- [ ] Version endpoint information
- [ ] Request logging and unique IDs
- [ ] Error handling and user feedback
- [ ] Rate limiting on sensitive endpoints
- [ ] CORS configuration
- [ ] Configuration validation

## 🐛 **Common Issues & Troubleshooting**

### **Backend Issues**
- **Port 8000 in use**: Change port in uvicorn command
- **Database errors**: Run `python -m db.seed` to reset data
- **Import errors**: Ensure all dependencies are installed

### **Frontend Issues**
- **Port 3000 in use**: Change port in npm run dev
- **Build errors**: Clear node_modules and reinstall
- **API connection**: Verify backend is running and accessible

### **Demo Mode Issues**
- **Tips not showing**: Check localStorage for demo-mode setting
- **Toggle not working**: Clear browser cache and reload
- **Tips on wrong screens**: Verify screen detection logic

### **Export Issues**
- **CSV not downloading**: Check browser download settings
- **Empty CSV**: Verify gradebook has data
- **Wrong data**: Check class_id parameter

## 📊 **Performance Expectations**

- **Page load times**: < 2 seconds
- **API response times**: < 1 second
- **Export generation**: < 5 seconds
- **Demo tip display**: < 500ms
- **Rate limiting**: 5 requests/minute for login

## 🎯 **Success Criteria**

The smoke test is considered **PASSED** if:
1. All core features work without errors
2. Demo mode functions correctly
3. CSV export generates accurate data
4. Analytics features display properly
5. Error handling works as expected
6. Performance meets expectations
7. No critical bugs or crashes occur

## 📝 **Test Results Template**

```
Smoke Test Results - [Date]
================================

Environment:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Database: SQLite (seeded)

Test Duration: [X] minutes
Tester: [Name]

Results:
✅ PASSED: [List passed features]
❌ FAILED: [List failed features]
⚠️  WARNINGS: [List warnings/issues]

Overall Status: PASSED/FAILED

Notes:
[Any additional observations or issues]
```

---

**🎉 Congratulations!** If all tests pass, the K12 LMS Phase 5 implementation is ready for production deployment!
