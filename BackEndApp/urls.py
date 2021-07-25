from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('followUpFiles/', views.followUpFiles, name='followUpFiles'),
    path('register/', views.register, name='register'),
    path('registerDoctor/', views.registerDoctor, name='registerDoctor'),
    path('registerHospital/', views.registerHospital, name='registerHospital'),
    
    
    path('addPatient/', views.addPatient, name='addPatient'),
    path('addDoctor/', views.addDoctor, name='addDoctor'),
    path('addLaboratory/', views.addLaboratory, name='addLaboratory'),
    path('addHospital/', views.addHospital, name='addHospital'),

    path('chatOpened/' , views.loadMessages, name = 'chatOpened'),
    
    
    path('registerLab/', views.registerLab, name='registerLab'),
    path('feed/', views.feed, name='feed'),
    path('logout/', views.logoutUser, name='logout'),
    path('addPrescription/', views.addPrescription, name='addPrescription'),
    path('addLabReport/', views.addLabReport, name='addLabReport'),

    path('loadSenders/', views.loadSenders, name='loadSenders'),
    path('loadMessages/', views.loadMessages, name='loadMessages'),
    path('sendMessage/', views.sendMessage, name='sendMessage'),
    
    path('addFollowUp/', views.addFollowUp, name='addFollowUp'),
    path('about/', views.about, name='about'),
    path('getPrescriptionFiles/', views.getPrescriptionFiles,
         name='getPrescriptionFiles'),
    path('getReportFiles/', views.getReportFiles, name='getReportFiles'),
    path('changePassword/', views.changePassword, name='changePassword'),
    path('viewTrustedContact/', views.viewTrustedContact,
         name='viewTrustedContact'),
    path('viewConnections/', views.viewConnections, name='viewConnections'),
    path('profile/', views.profile, name='profile'),
    path('summary/', views.summary, name='summary'),
    path('timeline/', views.timeline, name='timeline'),
    path('viewAllRecords/', views.viewAllRecords, name='viewAllRecords'),
    path('analysisByCity/' , views.analysisByCity, name='analysisByCity'),
    path('analysisByDisease/' , views.analysisByDisease, name='analysisByDisease'),
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
