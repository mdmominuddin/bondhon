from django.urls import path
from . import views
# from .views import ReportView

urlpatterns = [
    # Public and Authentication Views
    # path('', views.public_home, name='home'),
    path('', views.user_login, name='login'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),

    # Member Management
    path('members/', views.member_list, name='member_list'),

    # Deposit and Expense Management
    path('deposit/', views.create_deposit, name='create_deposit'),
    path('expense/', views.create_expense, name='create_expense'),
    # path('deposit-detail/', views.DepositDetails, name='deposit_detail'),
    # path('expense-detail/', views.DetailExpens, name='expense_detail'),

    # Summaries and Reporting
    path('monthly-summary/', views.monthly_summary, name='monthly_summary'),
    path('monthly-summary/<int:year>/<int:month>/', views.monthly_summary, name='monthly_summary_by_date'),
    # path('category-wise-summary/', views.category_wise_summary, name='category_wise_summary'),

    # Report Views
    # path('report/', ReportView.as_view(), name='report'),
    path('view_deposits/<int:member_id>/', views.view_deposits, name='view_deposits'),
    path('date_wise_deposit/', views.date_wise_deposit, name='date_wise_deposit'),
    path('date_wise_expense/', views.date_wise_expense, name='date_wise_expense'),
    path('month_wise_summary/', views.month_wise_summary, name='month_wise_summary'),
    path('monthlyreport/', views.monthlyreport, name='monthly_report'),
    path('dues_list/', views.members_with_dues, name='members_with_dues'),
    
    # path('individual-contributions/<int:member_id>/', ReportView.as_view(), name='individual_contributions'),

    # Contribution Plans (if applicable)
    path('contribution-plans/', views.contribution_plan_list, name='contribution_plan_list'),
    path('contribution-plan/<int:pk>/', views.contribution_plan_detail, name='contribution_plan_detail'),
    path('create-contribution-plan/', views.create_contribution_plan, name='create_contribution_plan'),
]
