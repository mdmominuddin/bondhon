from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    Expense,
    Deposit,
    DueDeposit,
    BuildingProject,
    Notification,
    SocietyMember,
    ContributionPlan,
)

# User Registration Form
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254, help_text="Required. Enter a valid email address."
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }


# User Login Form
class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ["username", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(attrs={"class": "form-control"}),
        }


# Expense Form
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["date", "description", "expense_head", "amount", "created_by", "remark"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "expense_head": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "remark": forms.TextInput(attrs={"class": "form-control"}),
        }

    # Override the created_by field to use a dropdown
    created_by = forms.ModelChoiceField(
        queryset=SocietyMember.objects.all(),
        widget=forms.Select(attrs={"class": "form-control"}),
        empty_label="Select Member",
        label="Created By"
    )


# Deposit Form
class DepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ["date", "member", "amount", "fund_head", "remark"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "member": forms.Select(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "fund_head": forms.Select(attrs={"class": "form-control"}),
            "remark": forms.TextInput(attrs={"class": "form-control"}),
        }


# Due Deposit Form
class DueDepositForm(forms.ModelForm):
    class Meta:
        model = DueDeposit
        fields = ["member", "date", "amount", "status"]
        widgets = {
            "member": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }


# Building Project Form
class BuildingProjectForm(forms.ModelForm):
    class Meta:
        model = BuildingProject
        fields = ["name", "start_date", "end_date", "budget", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "budget": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
        }


# Notification Form
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["member", "message"]
        widgets = {
            "member": forms.Select(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control"}),
        }


# Contribution Plan Form
class ContributionPlanForm(forms.ModelForm):
    class Meta:
        model = ContributionPlan
        fields = ["description", "amount"]
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control"}),
            
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
        }
