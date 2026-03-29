from django.urls import path
from . import views

urlpatterns = [
    path('classroom/<int:classroom_pk>/', views.lecture_list, name='lectures_list'),
    path('classroom/<int:classroom_pk>/create/', views.lecture_create, name='lecture_create'),
    path('<int:pk>/', views.lecture_detail, name='lecture_detail'),
    path('<int:pk>/edit/', views.edit_lecture, name='edit_lecture'),
    path('<int:pk>/delete/', views.delete_lecture, name='delete_lecture'),
    path('<int:pk>/toggle-lock/', views.toggle_lecture_thread_lock, name='toggle_lecture_thread_lock'),
    path('comment/<int:comment_id>/edit/', views.edit_lecture_comment, name='edit_lecture_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_lecture_comment, name='delete_lecture_comment'),
]
