from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('apply-loan/', views.apply_loan, name='apply_loan'),
    path('user/dashboard/', views.user_dashboard, name="user_dashboard"),
    path('loan/success/', views.loan_success, name="loan_success"),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_application/<int:application_id>/', views.approve_application, name='approve_application'),
    path('reject_application/<int:application_id>/', views.reject_application, name='reject_application'),
    path('investment/', views.investment_page, name='investment_page'),
    path('investment/form/', views.investment_form, name='investment_form'),
    path('register/', views.signup, name="register"),
    path('login/', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
]
