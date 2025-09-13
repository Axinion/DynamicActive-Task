# Phase 2 Manual Smoke Test Script

This document provides a comprehensive manual smoke test script to verify all Phase 2 features are working correctly. Follow these steps in order to test the complete teacher and student workflows.

## 🎯 Prerequisites

1. **Backend running**: `uvicorn app.main:app --reload --port 8000`
2. **Frontend running**: `npm run dev` (in frontend directory)
3. **Database seeded**: Run `./make_seed.sh` or `python db/seed.py`
4. **Demo credentials available**:
   - Teacher: `teacher@example.com` / `pass`
   - Student: `student@example.com` / `pass`
   - Demo class invite code: `ABC123`

## 🧪 Test Scenarios

### Scenario 1: Teacher Content Creation

#### Step 1: Teacher Login and Class Access
1. **Navigate to**: `http://localhost:3000`
2. **Login as Teacher**:
   - Email: `teacher@example.com`
   - Password: `pass`
   - Click "Login"
3. **Verify**: Redirected to `/teacher` dashboard
4. **Expected**: See demo class "Demo Class" with invite code `ABC123`

#### Step 2: Access Class Details
1. **Click**: "View" button on the demo class
2. **Verify**: Redirected to `/teacher/classes/1` (class overview)
3. **Expected**: See class name, invite code with copy button, and navigation tabs
4. **Verify Tabs**: Overview | Lessons | Assignments | Gradebook

#### Step 3: Create a New Lesson
1. **Click**: "Lessons" tab
2. **Verify**: See existing demo lessons (if any)
3. **Click**: "New Lesson" button
4. **Fill Lesson Form**:
   - Title: `"Advanced Python Functions"`
   - Content: `"In this lesson, we'll explore advanced Python functions including lambda functions, decorators, and generators. These concepts are essential for writing more efficient and elegant Python code."`
   - Skill Tags: `"python, functions, lambda, decorators, generators, advanced"`
5. **Click**: "Create Lesson"
6. **Verify**: Success toast appears
7. **Verify**: Lesson appears in the lessons list
8. **Click**: On the newly created lesson
9. **Verify**: Lesson detail page shows title, content, and skill tags correctly

#### Step 4: Create an Assignment with MCQ and Short Answer
1. **Click**: "Assignments" tab
2. **Click**: "New Assignment" button
3. **Fill Assignment Form**:
   - Title: `"Python Functions Quiz"`
   - Type: `"quiz"` (should be preselected)
   - Due Date: Leave empty (optional)
4. **Add MCQ Question**:
   - Click "Add Question"
   - Type: `"mcq"`
   - Prompt: `"What is the correct syntax for a lambda function in Python?"`
   - Options: 
     - `"lambda x: x * 2"`
     - `"function(x): x * 2"`
     - `"def lambda(x): x * 2"`
     - `"lambda function(x): x * 2"`
   - Correct Answer: Select `"lambda x: x * 2"`
   - Skill Tags: `"python, lambda, functions"`
5. **Add Short Answer Question**:
   - Click "Add Question"
   - Type: `"short"`
   - Prompt: `"Explain the difference between a regular function and a lambda function in Python. Include examples."`
   - Skill Tags: `"python, functions, lambda, comparison"`
6. **Click**: "Create Assignment"
7. **Verify**: Success toast appears
8. **Verify**: Redirected to assignment detail page
9. **Verify**: Assignment shows both questions correctly
10. **Copy Assignment ID**: Note the URL (e.g., `/teacher/assignments/2`) for later use

#### Step 5: Verify Assignment in List
1. **Click**: "Assignments" tab (or navigate back to class assignments)
2. **Verify**: New assignment appears in the list
3. **Verify**: Shows question count (2 questions)
4. **Verify**: Shows due date (if set) or "No due date"

### Scenario 2: Student Content Access and Submission

#### Step 6: Student Login
1. **Open new browser tab/window**: `http://localhost:3000`
2. **Login as Student**:
   - Email: `student@example.com`
   - Password: `pass`
   - Click "Login"
3. **Verify**: Redirected to `/student` dashboard
4. **Expected**: See enrolled demo class

#### Step 7: Access Class Content
1. **Click**: "View" button on the demo class
2. **Verify**: Redirected to `/student/classes/1` (class overview)
3. **Verify Tabs**: Overview | Lessons | Assignments

#### Step 8: View Lessons
1. **Click**: "Lessons" tab
2. **Verify**: See all available lessons (including the one created by teacher)
3. **Click**: On the lesson created in Step 3
4. **Verify**: Lesson content displays correctly with title, content, and skill tags
5. **Navigate back**: Use browser back button or click "Lessons" tab

#### Step 9: Take Assignment
1. **Click**: "Assignments" tab
2. **Verify**: See the assignment created in Step 4
3. **Verify**: Assignment shows "Start Assignment" button
4. **Click**: "Start Assignment" button
5. **Verify**: Redirected to assignment taking page

#### Step 10: Submit Assignment
1. **Answer MCQ Question**:
   - Select the correct answer: `"lambda x: x * 2"`
2. **Answer Short Answer Question**:
   - Enter: `"A regular function is defined using the 'def' keyword and can contain multiple statements. A lambda function is an anonymous function defined using the 'lambda' keyword and can only contain a single expression. Example: def regular(x): return x * 2 vs lambda x: x * 2"`
3. **Click**: "Submit Assignment"
4. **Verify**: Success toast appears
5. **Verify**: Redirected to result page

#### Step 11: Verify Submission Results
1. **Verify MCQ Result**:
   - Should show "Correct" or "Incorrect" for MCQ question
   - Should show the selected answer
   - Should show score (100% for correct, 0% for incorrect)
2. **Verify Short Answer Result**:
   - Should show "Awaiting Grading" status
   - Should show the submitted answer
   - Should show no score (null/empty)
3. **Verify Overall Score**:
   - Should show overall AI score based on MCQ only
   - Should show breakdown of individual question scores
4. **Click**: "Back to Assignments" link
5. **Verify**: Returned to assignments list

### Scenario 3: Teacher Gradebook Verification

#### Step 12: Teacher Gradebook Check
1. **Return to Teacher Tab**: Switch back to teacher browser tab
2. **Navigate to Gradebook**: Click "Gradebook" tab in class view
3. **Verify**: See student submission in the gradebook table
4. **Verify Columns**:
   - Student: "Demo Student" (or student name)
   - Assignment: "Python Functions Quiz"
   - Submitted At: Recent timestamp
   - AI Score: Should show score (e.g., 100% if MCQ was correct)
   - Teacher Score: Should show "—" (not yet graded)
5. **Click**: On the submission row
6. **Verify**: Side panel opens showing student responses
7. **Verify MCQ Response**: Shows selected answer and correct/incorrect status
8. **Verify Short Answer Response**: Shows submitted text with "Awaiting Grading" status

## ✅ Expected Results Summary

### Teacher Experience
- ✅ Can create lessons with title, content, and skill tags
- ✅ Can create assignments with MCQ and short-answer questions
- ✅ Can view all created content in organized lists
- ✅ Can access gradebook with student submissions
- ✅ Can see AI scores for MCQ questions
- ✅ Can view detailed student responses

### Student Experience
- ✅ Can view all available lessons
- ✅ Can read lesson content with proper formatting
- ✅ Can take assignments with interactive forms
- ✅ Receives immediate feedback on MCQ questions
- ✅ Sees "Awaiting Grading" status for short answers
- ✅ Can view submission results with score breakdown

### System Behavior
- ✅ MCQ questions auto-graded immediately (100% or 0%)
- ✅ Short answer questions stored with null scores
- ✅ Overall AI score calculated from MCQ questions only
- ✅ Gradebook shows submissions with proper scoring
- ✅ All navigation and routing works correctly
- ✅ Toast notifications appear for success/error states

## 🐛 Troubleshooting

### Common Issues

#### **Assignment Not Appearing**
- **Check**: Teacher created assignment successfully
- **Check**: Student is enrolled in the class
- **Check**: Assignment is published (no draft status)

#### **MCQ Not Auto-Grading**
- **Check**: Answer key is set correctly in assignment creation
- **Check**: Student selected an answer before submitting
- **Check**: Backend logs for any errors during submission

#### **Short Answer Not Showing "Awaiting Grading"**
- **Check**: Question type is set to "short" not "mcq"
- **Check**: Student submitted text in the textarea
- **Check**: Submission was successful (success toast appeared)

#### **Gradebook Empty**
- **Check**: Student has submitted the assignment
- **Check**: Teacher is viewing the correct class
- **Check**: Assignment was created in the same class

#### **Navigation Issues**
- **Check**: User is logged in with correct role
- **Check**: Class ID in URL matches the class being accessed
- **Check**: User has proper permissions (teacher owns class, student is enrolled)

## 📝 Test Data Reference

### Demo Credentials
- **Teacher**: `teacher@example.com` / `pass`
- **Student**: `student@example.com` / `pass`
- **Demo Class Invite Code**: `ABC123`

### Sample Content (Created by Seeding)
- **Lessons**: "Introduction to Python", "Data Structures in Python"
- **Assignment**: "Python Basics Quiz" with MCQ and short-answer questions

### Test Assignment (Created During Smoke Test)
- **Title**: "Python Functions Quiz"
- **MCQ**: Lambda function syntax question
- **Short Answer**: Regular vs lambda function comparison

---

**🎉 Success Criteria**: All steps complete without errors, all expected results verified, and both teacher and student workflows function correctly end-to-end.
