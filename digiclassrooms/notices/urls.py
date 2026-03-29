from django.urls import path
from . import views

urlpatterns = [
    path('classroom/<int:classroom_pk>/', views.notice_list, name='notices_list'),
    path('classroom/<int:classroom_pk>/create/', views.notice_create, name='notice_create'),
    path('<int:pk>/', views.notice_detail, name='notice_detail'),
    path('<int:pk>/edit/', views.edit_notice, name='edit_notice'),
    path('<int:pk>/delete/', views.delete_notice, name='delete_notice'),
    path('comment/<int:comment_id>/edit/', views.edit_notice_comment, name='edit_notice_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_notice_comment, name='delete_notice_comment'),
]
