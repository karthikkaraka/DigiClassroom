from django.urls import path
from . import views

urlpatterns = [
    path('classroom/<int:classroom_pk>/', views.notice_list, name='notices_list'),
    path('classroom/<int:classroom_pk>/create/', views.notice_create, name='notice_create'),
    path('<int:pk>/', views.notice_detail, name='notice_detail'),
    path('<int:pk>/edit/', views.edit_notice, name='edit_notice'),
    path('<int:pk>/delete/', views.delete_notice, name='delete_notice'),
    path('<int:pk>/toggle-pin/', views.toggle_notice_pin, name='toggle_notice_pin'),
    path('<int:pk>/toggle-lock/', views.toggle_notice_thread_lock, name='toggle_notice_thread_lock'),
    path('comment/<int:comment_id>/edit/', views.edit_notice_comment, name='edit_notice_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_notice_comment, name='delete_notice_comment'),
]
