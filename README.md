# DigiClassroom

**DigiClassroom** is a comprehensive, Django-based Learning Management System (LMS) designed to bridge the gap between physical and virtual education. It provides a structured environment where teachers can manage classrooms, deliver content through video lectures, post important notices, and conduct automated assessments.

The platform distinguishes itself with clean role-separation (Teacher/Student), intuitive navigation, and interactive features like threaded comments on lectures and notices.

---

## Key Features

### User Roles and Dashboards
- **Teacher Role**: Dedicated dashboard to manage classrooms, create content, and track student progress.
- **Student Role**: Personalized dashboard showing enrolled courses, pending assignments, and recent updates.
- **Profile Management**: Customized profiles for all users distinguishing between teachers and students.

### Classroom Management
- **Create and Customize**: Teachers can establish new classrooms with titles and descriptions.
- **Easy Enrollment**: Students can browse available classrooms and enroll with a single click.
- **One Teacher Per Classroom**: Security model ensures one teacher manages each classroom with multiple students.

### Interactive Video Lectures
- **YouTube Integration**: Seamlessly embed educational videos from YouTube.
- **Discussion Threads**: Lectures support threaded comments (including nested replies) for Q&A and discussions.
- **Organized Chronological Display**: Lectures are listed by most recent creation date.

### Notices and Announcements
- **Real-time Updates**: Teachers can post important class announcements and updates.
- **Interactive Discussions**: Notices support threaded comments for student questions and clarifications.
- **Author and Timestamp Tracking**: Every notice records the author and creation time.

### Assignments and Assessment
- **Quiz Builder**: Teachers can create assignments and add multiple-choice questions with four options each.
- **Instant Auto-Grading**: Submissions are automatically graded immediately upon completion.
- **Single Submission Per Student**: System prevents multiple submissions for the same assignment per student.
- **Personalized Teacher Feedback**: Teachers can review individual submissions and provide text-based feedback.

---

## Technical Architecture

### Framework and Technology Stack
- **Backend**: Django 6.0.2 with Python
- **Database**: SQLite (default, easily swappable to PostgreSQL or MySQL)
- **Frontend**: HTML5, CSS3, Django Template Language
- **Authentication**: Django's built-in authentication system with custom profile extensions

### Modular Application Structure
The project is organized into six main Django applications:

- **users**: Handles user authentication (signup/login/logout) and profile extensions that distinguish teachers from students.
- **classrooms**: Core logic for classroom creation, listing, and student enrollment management.
- **lectures**: Manages video content storage and associated comment threads.
- **notices**: Handles textual announcements and their interactive comment systems.
- **assignments**: Complex quiz logic including question creation, choice management, student submissions, and auto-grading.
- **results**: Placeholder application designed for future analytics and reporting features.

### Database Relationships
- **One-to-One**: User to Profile (extends Django User model)
- **One-to-One**: Teacher to Classroom (each classroom has exactly one teacher)
- **Many-to-Many**: Students to Classrooms (students can enroll in multiple classrooms)
- **Foreign Keys**: All content (Lectures, Notices, Assignments, Comments) link to specific classrooms
- **Hierarchical Comments**: Comment systems support nested replies through parent-child relationships

### Data Models Overview

#### User and Profile
- `User`: Django's built-in User model
- `Profile`: Custom extension storing teacher/student flag

#### Classroom Hierarchy
- `Classroom`: Container for all classroom content (name, description, teacher, students)
- `Lecture`: Video content (title, YouTube link, creation timestamp)
- `LectureComment`: Threaded discussion on lectures (with parent field for replies)
- `Notice`: Text announcements (title, content, author, timestamp)
- `NoticeComment`: Threaded discussion on notices (with parent field for replies)

#### Assessment System
- `Assignment`: Quiz container (title, creation timestamp, classroom reference)
- `Question`: Individual quiz question (text, assignment reference)
- `Choice`: Multiple choice options (text, correctness flag)
- `Submission`: Student submission record (score, teacher feedback, timestamp)
- `StudentAnswer`: Individual answer record (links submission, question, and selected choice)

---

## Getting Started

To set up and run DigiClassroom locally, refer to [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions.

For email configuration (password resets, notifications), see [EMAIL_SETUP.md](EMAIL_SETUP.md).

---

## Contributing

Contributions are welcome! Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
