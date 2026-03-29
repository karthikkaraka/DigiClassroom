from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('setup/', views.setup_classroom, name='setup_classroom'),
    path('enroll/', views.enroll_classroom, name='enroll_classroom'),
    path('join/', views.join_classroom, name='join_classroom'),
    path('join/<int:pk>/', views.join_classroom, name='join_classroom_for_classroom'),
    path('search/', views.search_classrooms, name='search_classrooms'),
    path('classroom/<int:pk>/', views.classroom_detail, name='classroom_detail'),
    path('classroom/<int:pk>/regenerate-key/', views.regenerate_join_key, name='regenerate_join_key'),
]
