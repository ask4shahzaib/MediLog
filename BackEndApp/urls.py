from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('register/', views.register, name='register'),
    path('feed/', views.feed, name='feed'),
    path('logout/', views.logoutUser, name='logout'),
    path('', views.home, name='base'),
]
