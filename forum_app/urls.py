from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.list_questions, name='home'),
    path("questions/", views.list_questions, name="list_questions"),
    path('questions/post/', views.post_question, name='post_question'),
    path('questions/<int:question_id>/', views.question_detail, name='question_detail'),
    path('answers/<int:answer_id>/like/', views.like_answer, name='like_answer'),
    path('notifications/', views.get_notifications, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.read_notification_redirect, name='read_notification_redirect'),

]
