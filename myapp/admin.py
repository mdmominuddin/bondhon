from django.contrib import admin
from .models import (
    SocietyMember,
    MonthlyFinancialSummary,
    ExpenseHead,
    Expense,
    Deposit,
    DueDeposit,
    BuildingProject,
    Notification,
    Category,
    ExpenseCategory,
    ContributionPlan,
)

# Register the SocietyMember model with some customization
@admin.register(SocietyMember)
class SocietyMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'society_designation', 'phone_number', 'shares', 'joining_date')
    search_fields = ('name', 'phone_number')
    list_filter = ('society_designation',)
    ordering = ('name',)

# Register the MonthlyFinancialSummary model with some customization
@admin.register(MonthlyFinancialSummary)
class MonthlyFinancialSummaryAdmin(admin.ModelAdmin):
    list_display = ('month', 'total_deposits', 'total_expenses', 'balance')
    search_fields = ('month',)
    list_filter = ('month',)
    ordering = ('month',)

# Register the ExpenseHead model
@admin.register(ExpenseHead)
class ExpenseHeadAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Register the Expense model with some customization
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'expense_head', 'amount', 'created_by', 'remark')
    search_fields = ('description', 'created_by__username', 'expense_head__name')
    list_filter = ('date', 'expense_head')
    ordering = ('-date',)

# Register the Deposit model with some customization
@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('date', 'member', 'amount', 'fund_head', 'remark')
    search_fields = ('member__name', 'fund_head__name')
    list_filter = ('date', 'member', 'fund_head')
    ordering = ('-date',)

# Register the DueDeposit model with some customization
@admin.register(DueDeposit)
class DueDepositAdmin(admin.ModelAdmin):
    list_display = ('member', 'date', 'amount', 'status')
    search_fields = ('member__name',)
    list_filter = ('status', 'date')
    ordering = ('-date',)

# Register the BuildingProject model
@admin.register(BuildingProject)
class BuildingProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'budget')
    search_fields = ('name',)
    list_filter = ('start_date',)
    ordering = ('-start_date',)

# Register the Notification model
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('member', 'message', 'created_at')
    search_fields = ('member__name', 'message')
    ordering = ('-created_at',)

# Register the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Register the ExpenseCategory model
@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

# Register the ContributionPlan model
@admin.register(ContributionPlan)
class ContributionPlanAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'start_date', 'end_date')
    search_fields = ('description',)
    ordering = ('start_date',)

