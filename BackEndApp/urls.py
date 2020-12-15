from django.urls import path
from . import views

urlpatterns = [
    path('partner/<str:name>', views.name),
    path('login/', views.login),
    path('register/', views.register),
    path('', views.home),
]
