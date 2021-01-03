from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('register/', views.register, name='register'),
    path('feed/', views.feed, name='feed'),
    path('logout/', views.logoutUser, name='logout'),
    path('prescription/', views.prescription, name='prescription'),
    path('', views.home, name='base'),
]
