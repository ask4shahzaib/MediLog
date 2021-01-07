from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('register/', views.register, name='register'),
    path('feed/', views.feed, name='feed'),
    path('logout/', views.logoutUser, name='logout'),
    path('prescription/', views.prescription, name='prescription'),
    path('profile/', views.profile, name='profile'),
    path('summary/', views.summary, name='summary'),
    path('reset_password/',
         auth_views.PasswordResetView.as_view(
             template_name="BackEndApp/password_reset.html"),
         name="reset_password"),

    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="BackEndApp/password_reset_sent.html"),
         name="password_reset_done"),

    path('reset/<uidb64>/<token>',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="BackEndApp/password_reset_form.html"),
         name="password_reset_confirm"),

    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="BackEndApp/password_reset_done.html"),
         name="password_reset_complete"),

    path('', views.home, name='base'),
]
