from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from classrooms.models import Classroom
from lectures.models import Lecture, LectureComment
from notices.models import Notice, NoticeComment
from assignments.models import Assignment, Question, Choice, Submission, StudentAnswer
from users.models import Profile


class Command(BaseCommand):
    help = 'Creates dummy data for testing the DigiClassroom application'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Creating dummy data...'))
        
        # Create users
        self.stdout.write('Creating users...')
        
        # Create multiple teachers
        teachers = []
        teacher_data = [
            ('teacher1', 'John', 'Smith', 'john@example.com'),
            ('teacher2', 'Sarah', 'Johnson', 'sarah@example.com'),
            ('teacher3', 'Michael', 'Brown', 'michael@example.com'),
            ('teacher4', 'Emily', 'Davis', 'emily@example.com'),
            ('teacher5', 'Robert', 'Miller', 'robert@example.com'),
            ('teacher6', 'Jennifer', 'Wilson', 'jennifer@example.com'),
        ]
        
        for username, first, last, email in teacher_data:
            teacher, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last
                }
            )
            if created:
                teacher.set_password('password123')
                teacher.save()
                profile, _ = Profile.objects.get_or_create(user=teacher)
                profile.is_teacher = True
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'Created teacher: {teacher.username}'))
            else:
                self.stdout.write(f'  Teacher {teacher.username} already exists')
            teachers.append(teacher)
        
        # Create students
        students = []
        student_data = [
            ('student1', 'Alice', 'Johnson', 'alice@example.com'),
            ('student2', 'Bob', 'Williams', 'bob@example.com'),
            ('student3', 'Charlie', 'Brown', 'charlie@example.com'),
        ]
        
        for username, first, last, email in student_data:
            student, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first,
                    'last_name': last
                }
            )
            if created:
                student.set_password('password123')
                student.save()
                profile, _ = Profile.objects.get_or_create(user=student)
                profile.is_teacher = False
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'Created student: {student.username}'))
            else:
                self.stdout.write(f'  Student {student.username} already exists')
            students.append(student)
        
        # Create classrooms
        self.stdout.write('\nCreating classrooms...')
        
        classroom_data = [
            ('CS101 - Introduction to Computer Science', 'Learn the fundamentals of programming and computer science'),
            ('MATH201 - Linear Algebra', 'Explore vectors, matrices, and linear transformations'),
            ('PHYS301 - Classical Mechanics', 'Study motion, forces, and energy in classical physics'),
            ('DATA401 - Data Structures and Algorithms', 'Master essential data structures and algorithm design patterns'),
            ('WEB501 - Full Stack Web Development', 'Build modern web applications using frontend and backend technologies'),
            ('DB601 - Database Design and SQL', 'Design efficient databases and master SQL queries'),
        ]
        
        classrooms = []
        for idx, (name, desc) in enumerate(classroom_data):
            teacher = teachers[idx % len(teachers)]
            classroom, created = Classroom.objects.get_or_create(
                name=name,
                defaults={
                    'teacher': teacher,
                    'description': desc
                }
            )
            if created:
                # Add students to classroom
                classroom.students.add(*students)
                self.stdout.write(self.style.SUCCESS(f'Created classroom: {classroom.name}'))
            else:
                self.stdout.write(f'  Classroom {classroom.name} already exists')
            classrooms.append(classroom)
        
        # Subject-specific content mapping
        subject_content = {
            'CS101 - Introduction to Computer Science': {
                'lectures': [
                    ('What is Computer Science?', 'https://www.youtube.com/watch?v=kqtD5dpn9C8'),
                    ('History of Computing', 'https://www.youtube.com/watch?v=Z1Yd7upQsXY'),
                    ('Introduction to Algorithms', 'https://www.youtube.com/watch?v=PqFKRqpHrjw'),
                    ('Binary and Number Systems', 'https://www.youtube.com/watch?v=NSbOtYzIQI0'),
                    ('Boolean Logic Basics', 'https://www.youtube.com/watch?v=JeznW_7DlB0'),
                ],
                'notices': [
                    ('Welcome to CS101!', 'Welcome to Introduction to Computer Science! This course covers fundamental concepts in computer science.'),
                    ('Assignment 1 Released', 'Assignment 1 on Boolean Logic is now available. Due by next Friday.'),
                    ('Midterm Exam Schedule', 'The midterm exam will be held next month. Start preparing now!'),
                ],
                'assignments': [
                    {
                        'title': 'Boolean Logic Quiz',
                        'questions': [
                            {'text': 'What is the output of (True AND False)?', 'choices': [('True', False), ('False', True), ('None', False), ('Error', False)]},
                            {'text': 'Which gate produces output 1 when all inputs are 1?', 'choices': [('OR', False), ('AND', True), ('NOT', False), ('XOR', False)]},
                            {'text': 'What does OR gate do?', 'choices': [('Output 1 if any input is 1', True), ('Output 1 only if all are 1', False), ('Inverts input', False), ('Compares inputs', False)]},
                        ]
                    },
                    {
                        'title': 'Number Systems Assessment',
                        'questions': [
                            {'text': 'What is 1010 in decimal?', 'choices': [('8', False), ('10', True), ('12', False), ('16', False)]},
                            {'text': 'What is 255 in hexadecimal?', 'choices': [('FF', True), ('FE', False), ('FFF', False), ('100', False)]},
                        ]
                    },
                ]
            },
            'MATH201 - Linear Algebra': {
                'lectures': [
                    ('Introduction to Vectors', 'https://www.youtube.com/watch?v=fNk_zzaMoSY'),
                    ('Matrix Operations', 'https://www.youtube.com/watch?v=IZcyz27-a8w'),
                    ('Determinants and Inverses', 'https://www.youtube.com/watch?v=Ip3X9LOh_90'),
                    ('Eigenvalues and Eigenvectors', 'https://www.youtube.com/watch?v=PFDu9oVAE-g'),
                    ('Linear Transformations', 'https://www.youtube.com/watch?v=kYB8IZa7TL8'),
                ],
                'notices': [
                    ('Welcome to Linear Algebra!', 'Linear Algebra is the foundation for advanced mathematics and computer science. Let\'s explore vectors and matrices together.'),
                    ('Problem Set 1 Due', 'Problem Set 1 covering vectors and basic matrix operations is due this Friday.'),
                    ('Office Hours Extended', 'Due to high demand, office hours have been extended to Tuesday and Thursday evenings.'),
                ],
                'assignments': [
                    {
                        'title': 'Vector Operations Quiz',
                        'questions': [
                            {'text': 'What is the dot product of (1,2) and (3,4)?', 'choices': [('7', False), ('11', True), ('9', False), ('12', False)]},
                            {'text': 'What is the magnitude of vector (3,4)?', 'choices': [('5', True), ('7', False), ('sqrt(7)', False), ('25', False)]},
                            {'text': 'Are vectors (1,2) and (2,4) orthogonal?', 'choices': [('Yes', False), ('No', True), ('Cannot determine', False), ('Undefined', False)]},
                        ]
                    },
                    {
                        'title': 'Matrix Multiplication Test',
                        'questions': [
                            {'text': 'What is the result of multiplying a 2x3 matrix with a 3x2 matrix?', 'choices': [('2x2', True), ('3x3', False), ('2x3', False), ('Cannot multiply', False)]},
                        ]
                    },
                ]
            },
            'PHYS301 - Classical Mechanics': {
                'lectures': [
                    ('Kinematics and Motion', 'https://www.youtube.com/watch?v=Y0nnzS_5IVc'),
                    ('Newton\'s Laws of Motion', 'https://www.youtube.com/watch?v=VzZdvVsYnB4'),
                    ('Energy and Work', 'https://www.youtube.com/watch?v=w-P-K9JBbq0'),
                    ('Momentum and Collisions', 'https://www.youtube.com/watch?v=cJsqBXfVh5s'),
                    ('Rotational Motion', 'https://www.youtube.com/watch?v=sN6tMVqo7Ow'),
                ],
                'notices': [
                    ('Welcome to Classical Mechanics!', 'This course explores the motion of objects and forces. Get ready for some interesting experiments!'),
                    ('Lab Report 1 Guidelines', 'Lab Report 1 submission guidelines are now available. Please follow the format provided.'),
                    ('Exam Prep Session', 'Join me for an exam preparation session on Friday at 4 PM in the physics lab.'),
                ],
                'assignments': [
                    {
                        'title': 'Newton\'s Laws Quiz',
                        'questions': [
                            {'text': 'What does Newton\'s First Law state?', 'choices': [('F = ma', False), ('Objects continue in motion unless acted upon', True), ('Action equals reaction', False), ('Energy is conserved', False)]},
                            {'text': 'If F = ma, and a = 0, what can we conclude?', 'choices': [('F is zero or object is at rest', True), ('Object is moving', False), ('No force exists', False), ('Mass is zero', False)]},
                            {'text': 'For every action there is an equal and opposite reaction. Which law?', 'choices': [('First', False), ('Second', False), ('Third', True), ('Fourth', False)]},
                        ]
                    },
                    {
                        'title': 'Motion and Forces Problem Set',
                        'questions': [
                            {'text': 'An object accelerates at 5 m/s^2 with a force of 50 N. What is its mass?', 'choices': [('5 kg', False), ('10 kg', True), ('25 kg', False), ('250 kg', False)]},
                            {'text': 'What is the SI unit of work?', 'choices': [('Newton', False), ('Joule', True), ('Watt', False), ('Pascal', False)]},
                        ]
                    },
                ]
            },
            'DATA401 - Data Structures and Algorithms': {
                'lectures': [
                    ('Arrays and Linked Lists', 'https://www.youtube.com/watch?v=WwIkUjZOTco'),
                    ('Stacks and Queues', 'https://www.youtube.com/watch?v=wjI1WNcIntg'),
                    ('Trees and Binary Search Trees', 'https://www.youtube.com/watch?v=xLVCHKAUhGU'),
                    ('Graphs and Graph Traversal', 'https://www.youtube.com/watch?v=tWVWeAqZ0WU'),
                    ('Sorting and Searching Algorithms', 'https://www.youtube.com/watch?v=iqlTj3SQpM8'),
                ],
                'notices': [
                    ('Welcome to Data Structures!', 'This course will teach you the building blocks of efficient algorithms. Master these concepts!'),
                    ('Coding Challenge 1 Released', 'Implement a stack using arrays. Submit your solution on the assignment portal.'),
                    ('Big O Notation Review', 'Please review Big O notation from online resources before next class.'),
                ],
                'assignments': [
                    {
                        'title': 'Data Structures Fundamentals',
                        'questions': [
                            {'text': 'What is the time complexity of accessing an element in an array?', 'choices': [('O(n)', False), ('O(1)', True), ('O(log n)', False), ('O(n²)', False)]},
                            {'text': 'Which data structure follows LIFO principle?', 'choices': [('Queue', False), ('Stack', True), ('Array', False), ('Link', False)]},
                            {'text': 'What is the worst case for binary search?', 'choices': [('O(1)', False), ('O(n)', False), ('O(log n)', True), ('O(n²)', False)]},
                        ]
                    },
                    {
                        'title': 'Algorithm Analysis Quiz',
                        'questions': [
                            {'text': 'Bubble sort has a best-case complexity of:', 'choices': [('O(n)', True), ('O(n²)', False), ('O(log n)', False), ('O(n log n)', False)]},
                            {'text': 'Which is NOT a sorting algorithm?', 'choices': [('Merge Sort', False), ('Quick Sort', False), ('Binary Search', True), ('Heap Sort', False)]},
                        ]
                    },
                ]
            },
            'WEB501 - Full Stack Web Development': {
                'lectures': [
                    ('HTML Fundamentals', 'https://www.youtube.com/watch?v=qz0aGYrrlMU'),
                    ('CSS Styling and Layouts', 'https://www.youtube.com/watch?v=OXGznpKZ_sA'),
                    ('JavaScript Basics', 'https://www.youtube.com/watch?v=W6NZfCO5tTE'),
                    ('Backend Development with Django', 'https://www.youtube.com/watch?v=jBzwzrDvZ18'),
                    ('Databases and SQL', 'https://www.youtube.com/watch?v=FQqNeGAI5UE'),
                ],
                'notices': [
                    ('Welcome to Full Stack Development!', 'Learn to build complete web applications. This is an intensive and practical course.'),
                    ('Project 1: Personal Portfolio', 'Create a personal portfolio website using HTML, CSS, and JavaScript. Due in 2 weeks.'),
                    ('JavaScript Frameworks Discussion', 'We will start learning React next week. Prepare by reviewing ES6 concepts.'),
                ],
                'assignments': [
                    {
                        'title': 'HTML and CSS Basics',
                        'questions': [
                            {'text': 'What does HTML stand for?', 'choices': [('Hyper Text Markup Language', True), ('High Tech Modern Language', False), ('Home Tool Markup Language', False), ('Hyperlinks and Text Markup', False)]},
                            {'text': 'Which CSS property changes text color?', 'choices': [('color', True), ('text-color', False), ('font-color', False), ('text-style', False)]},
                            {'text': 'What is the purpose of class selectors in CSS?', 'choices': [('Style multiple elements', True), ('Create new elements', False), ('Define page layout', False), ('Set fonts', False)]},
                        ]
                    },
                    {
                        'title': 'JavaScript and Backend Quiz',
                        'questions': [
                            {'text': 'What is the correct way to declare a variable in JavaScript?', 'choices': [('var x = 5;', True), ('x = 5;', False), ('int x = 5;', False), ('declare x = 5;', False)]},
                            {'text': 'Which framework is for frontend development?', 'choices': [('React', True), ('Django', False), ('Flask', False), ('Spring', False)]},
                        ]
                    },
                ]
            },
            'DB601 - Database Design and SQL': {
                'lectures': [
                    ('Database Basics and Design', 'https://www.youtube.com/watch?v=4cWkVbC2bNE'),
                    ('Relational Database Model', 'https://www.youtube.com/watch?v=jQ0C-yKXtGQ'),
                    ('SELECT Statements and Queries', 'https://www.youtube.com/watch?v=0-ZhV0Ev1Vg'),
                    ('JOINs and Subqueries', 'https://www.youtube.com/watch?v=F_I0EJfK_20'),
                    ('Normalization and Optimization', 'https://www.youtube.com/watch?v=n0CJYv07Uxs'),
                ],
                'notices': [
                    ('Welcome to Database Design!', 'SQL is a critical skill for data management. Let\'s master database design and queries.'),
                    ('SQL Practice Environment Ready', 'The SQL practice environment is now available. Start with the basic queries tutorial.'),
                    ('Normalization Assignment', 'Normalize a given database schema and submit your design document by next Wednesday.'),
                ],
                'assignments': [
                    {
                        'title': 'SQL Basics Quiz',
                        'questions': [
                            {'text': 'Which SQL statement is used to retrieve data?', 'choices': [('SELECT', True), ('GET', False), ('FETCH', False), ('RETRIEVE', False)]},
                            {'text': 'What does PRIMARY KEY ensure?', 'choices': [('Uniqueness and non-null', True), ('Data encryption', False), ('Faster queries', False), ('Automatic backup', False)]},
                            {'text': 'Which JOIN returns all rows from the left table?', 'choices': [('INNER JOIN', False), ('LEFT JOIN', True), ('RIGHT JOIN', False), ('FULL JOIN', False)]},
                        ]
                    },
                    {
                        'title': 'Database Design and Normalization',
                        'questions': [
                            {'text': 'What is the main goal of normalization?', 'choices': [('Reduce redundancy', True), ('Increase performance', False), ('Create more tables', False), ('Add constraints', False)]},
                            {'text': 'How many tables would you create for a one-to-many relationship?', 'choices': [('1', False), ('2', True), ('3', False), ('Depends on data', False)]},
                        ]
                    },
                ]
            }
        }
        
        # Create lectures
        self.stdout.write('\nCreating lectures...')
        
        for classroom in classrooms:
            lectures = subject_content[classroom.name]['lectures']
            for title, url in lectures:
                lecture, created = Lecture.objects.get_or_create(
                    classroom=classroom,
                    title=title,
                    defaults={
                        'youtube_link': url
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created lecture: {title}'))
                    
                    # Add some comments to lectures
                    if students:
                        LectureComment.objects.get_or_create(
                            lecture=lecture,
                            author=students[0],
                            defaults={'content': 'Great lecture! Very informative.'}
                        )
        
        # Create notices
        self.stdout.write('\nCreating notices...')
        
        for classroom in classrooms:
            notices = subject_content[classroom.name]['notices']
            for title, content in notices:
                notice, created = Notice.objects.get_or_create(
                    classroom=classroom,
                    title=title,
                    defaults={
                        'content': content,
                        'author': classroom.teacher
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created notice: {title}'))
        
        # Create assignments
        self.stdout.write('\nCreating assignments...')
        
        for classroom in classrooms:
            assignments = subject_content[classroom.name]['assignments']
            for assign_info in assignments:
                assignment, created = Assignment.objects.get_or_create(
                    classroom=classroom,
                    title=assign_info['title'],
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Created assignment: {assign_info["title"]}'))
                    
                    # Create questions and choices
                    for q_data in assign_info['questions']:
                        question = Question.objects.create(
                            assignment=assignment,
                            text=q_data['text']
                        )
                        
                        for choice_text, is_correct in q_data['choices']:
                            Choice.objects.create(
                                question=question,
                                text=choice_text,
                                is_correct=is_correct
                            )
                    
                    # Create a sample submission from first student
                    if students:
                        submission = Submission.objects.create(
                            assignment=assignment,
                            student=students[0],
                            score=0
                        )
                        
                        score = 0
                        for question in assignment.questions.all():
                            # Randomly pick an answer (first choice for demo)
                            choice = question.choices.first()
                            if choice:
                                StudentAnswer.objects.create(
                                    submission=submission,
                                    question=question,
                                    choice=choice
                                )
                                if choice.is_correct:
                                    score += 1
                        
                        submission.score = score
                        submission.teacher_feedback = "Good effort! Keep practicing."
                        submission.save()
                        
                        self.stdout.write(f'    Created sample submission for {students[0].username}')
        
        self.stdout.write(self.style.SUCCESS('\nDummy data creation complete!'))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('  Teacher: username=teacher1, password=password123')
        self.stdout.write('  Student: username=student1, password=password123')
        self.stdout.write('  Student: username=student2, password=password123')
        self.stdout.write('  Student: username=student3, password=password123')
        self.stdout.write(self.style.SUCCESS('\nClassrooms created:'))
        self.stdout.write('  - CS101 - Introduction to Computer Science')
        self.stdout.write('  - MATH201 - Linear Algebra')
        self.stdout.write('  - PHYS301 - Classical Mechanics')
        self.stdout.write('  - DATA401 - Data Structures and Algorithms')
        self.stdout.write('  - WEB501 - Full Stack Web Development')
        self.stdout.write('  - DB601 - Database Design and SQL')
