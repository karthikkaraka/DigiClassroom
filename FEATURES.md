# DigiClassroom - Features Guide

## Recently Added Features

### 1. Classroom Join Keys

**Description**: Teachers can generate unique 8-character keys for each classroom, allowing students to join via code instead of browsing.

**Teacher Functionality**:
- Join key is auto-generated when classroom is created
- Teachers can regenerate keys at any time (invalidates old key)
- View join key in classroom settings
- Share key with students easily

**Student Functionality**:
- Join classroom via "Join with Code" option
- Enter the 8-character classroom key
- Student is instantly added to the classroom

**Implementation Details**:
```python
# Classroom model
join_key = CharField(max_length=8, unique=True)
regenerate_join_key()  # Method to generate new key
```

---

### 2. Edit and Delete Comments

**Description**: Users can edit their own comments on lectures and notices, and teachers can moderate/delete inappropriate comments.

**Comment Editing**:
- Click "Edit" on your own comment
- Modify the content
- Comment marked with "edited" indicator
- Updated timestamp shown

**Comment Deletion**:
- Authors can delete their own comments
- Teachers can delete any comment in their classroom
- Nested replies handled appropriately

**Implementation Details**:
```python
# LectureComment and NoticeComment models
updated_at = DateTimeField(auto_now=True)
is_edited = BooleanField(default=False)
```

---

### 3. Edit and Delete Content

**Description**: Teachers can edit and delete lectures, notices, and quizzes they created.

**Lecture Management**:
- Teachers can edit lecture title and YouTube link
- Delete entire lecture (with confirmation)
- Updated timestamp shown to students

**Notice Management**:
- Teachers can edit notice title and content
- Delete notice with confirmation
- Students see "edited" indicator if modified

**Quiz/Assignment Management**:
- Teachers can edit assignment title and due date
- Edit individual questions and answer choices
- Delete assignments (with confirmation for cascading deletes)
- Updated timestamp visible

---

### 4. Search Functionality for Classes

**Description**: Students browse/search available classrooms instead of seeing all at once on home page.

**New Search Features**:
- Search bar on "Browse Classes" page
- Filter by classroom name, description, teacher
- Sort by recently created, alphabetically
- Shows classroom details (description, teacher name)
- One-click enrollment

**Implementation**:
- New Django view with Q objects for search
- Pagination for large result sets
- Optional: Search cache for performance

---

### 5. View Past Quiz Attempts

**Description**: Students can view history of all submission attempts for an assignment.

**Features**:
- "Submission History" tab on assignment detail
- List all attempts with scores and dates
- Click to view detailed submission
- Compare answers across attempts
- See teacher feedback for each submission

**Teacher View**:
- "All Submissions" page showing all students' attempts
- Filter by student
- Download submission data

---

### 6. Assignment Due Dates

**Added to Previous Feature**: Assignments now support due dates with visual indicators.

**Features**:
- Set due date when creating assignment
- Edit due date anytime
- Visual indicators: On-time, Late, Not Submitted
- Count down timer (optional)
- Automatic flagging of late submissions

---

## Suggested Extra Features (Not Too Complicated)

### A. Assignment Grades and Statistics

**Description**: Teachers get quick grade overview, students see their performance.

**Features**:
- Grade book view for teachers (class average, histogram)
- Student performance dashboard (scores across assignments)
- Automatic GPA calculation based on grades
- Class performance analytics

**Implementation**: Query aggregations on Submission model

---

### B. Lecture Completion Tracking

**Description**: Track which lectures students have watched/completed.

**Features**:
- "Mark as Watched" button on lecture
- Teachers see completion percentage per lecture
- Students see their watched lectures list
- Get notifications for unwatched lectures

**Models**:
```python
class LectureProgress(models.Model):
    student = ForeignKey(User)
    lecture = ForeignKey(Lecture)
    is_completed = BooleanField()
    watched_at = DateTimeField()
```

---

### C. Favorite/Bookmark Classes and Lectures

**Description**: Quick access to frequently used resources.

**Features**:
- Star icon to favorite classrooms
- Favorite classrooms appear at top of dashboard
- Bookmark lectures for easy re-access
- Organize learning materials

**Models**:
```python
class Favorite(models.Model):
    user = ForeignKey(User)
    classroom = ForeignKey(Classroom)
    bookmarked_at = DateTimeField(auto_now_add=True)
```

---

### D. Simple Announcements/Notifications

**Description**: Real-time notifications for important updates.

**Features**:
- Notification badge in navbar
- Mark as read/unread
- Filter: Class updates, assignments due, submissions graded
- Email digest option (daily/weekly)

**Models**:
```python
class Notification(models.Model):
    user = ForeignKey(User)
    classroom = ForeignKey(Classroom, null=True)
    message = TextField()
    is_read = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
```

---

### E. Attendance/Participation Tracking

**Description**: Simple engagement metrics for student motivation.

**Features**:
- Count submissions, comments, lecture views
- Participation score per student
- "Streak" for consecutive participation
- Teachers see participation report

**Implementation**: Query-based, no new models needed

---

### F. Assignment Re-attempts

**Description**: Allow multiple attempts with best score tracking.

**Features**:
- Set max attempts per assignment
- Keep track of all attempts
- Show best score and all scores
- Display improvement over attempts

**Models**:
```python
# Modify Assignment
max_attempts = IntegerField(default=1)

# In Submission
attempt_number = IntegerField(default=1)
```

---

### G. Drag-and-Drop Quiz Ordering

**Description**: Question ordering/shuffling for better assessment.

**Features**:
- Teacher shuffles questions for each student
- Randomize answer choices order
- Prevent cheating by varying question order
- Set difficulty per question

---

### H. Student Progress Dashboard

**Description**: Personal learning analytics for students.

**Features**:
- Assignment completion status
- Quiz performance trends (chart)
- Class participation summary
- Time spent on assignments
- Topics mastered vs. to-review

---

### I. Auto-Save Quiz Responses

**Description**: Prevent data loss during quiz attempts.

**Features**:
- Auto-save responses every 30 seconds
- Visual indicator: "Saving...", "Saved"
- Resume from last saved attempt if interrupted
- Recovery message if browser crashed

---

### J. Bulk Upload for Assignments

**Description**: Teachers upload CSV of student answers for grade import.

**Features**:
- CSV template for grades
- Bulk upload grades
- Automatic grading logic
- Batch feedback messaging

---

## Implementation Priority

### High Priority (Core Functionality):
1. Classroom Join Keys
2. Edit/Delete Comments
3. Edit/Delete Content
4. Search Classes
5. View Past Quiz Attempts

### Medium Priority (Nice to Have):
- Assignment Grades/Statistics (A)
- Attendance Tracking (E)
- Student Progress Dashboard (H)
- Announcements/Notifications (D)

### Low Priority (Future Enhancements):
- Lecture Completion Tracking (B)
- Favorites (C)
- Multiple Attempts (F)
- Question Shuffling (G)
- Auto-save (I)
- Bulk Upload (J)

---

## Database Migration Notes

Run migrations after model updates:

```bash
python manage.py makemigrations
python manage.py migrate
```

Existing classrooms will have empty join_keys - run management command to generate:

```bash
python manage.py generate_join_keys
```

---

## Next Steps

1. Create management command for generating join keys
2. Update views to handle join key logic
3. Add forms for edit/delete functionality
4. Create search views and templates
5. Add submission history views
6. Update templates with new UI
7. Create management commands for utilities
