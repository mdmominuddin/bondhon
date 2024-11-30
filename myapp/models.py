from django.db import models
from datetime import date
from django.contrib.auth.models import User


class SocietyMember(models.Model):
    MEMBER_DESIGNATION_CHOICES = [
        ("General Member", "General Member"),
        ("Treasurer", "Treasurer"),
        ("Secretary", "Secretary"),
        ("President", "President"),
    ]
    name = models.CharField(max_length=255)
    society_designation = models.CharField(
        max_length=50, choices=MEMBER_DESIGNATION_CHOICES, default="General Member"
    )
    
    phone_number = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    shares = models.PositiveIntegerField(default=1)
    joining_date = models.DateField(default=date.today)

    def __str__(self):
        return self.name
    
    def calculate_due(self, contribution_plan):
        """Calculate the due based on shares and contribution plan"""
        return contribution_plan.amount * self.shares


class MonthlyFinancialSummary(models.Model):
    month = models.DateField(default=date.today, unique=True)
    total_deposits = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_balance(self):
        self.balance = self.total_deposits - self.total_expenses

    def save(self, *args, **kwargs):
        self.calculate_balance()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.month.strftime("%B %Y"))


class ExpenseHead(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Expense(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=255)
    expense_head = models.ForeignKey(ExpenseHead, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(SocietyMember, on_delete=models.CASCADE)
    remark = models.CharField(max_length=200, default="Nil")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the corresponding MonthlyFinancialSummary
        summary, created = MonthlyFinancialSummary.objects.get_or_create(
            month=self.date.replace(day=1)
        )
        summary.total_expenses += self.amount
        summary.save()

    def __str__(self):
        return f"{self.expense_head.name} - {self.date.strftime('%d-%m-%Y')}"


class Deposit(models.Model):
    date = models.DateField()
    member = models.ForeignKey(SocietyMember, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fund_head = models.ForeignKey(ExpenseHead, on_delete=models.CASCADE)
    remark = models.CharField(max_length=200, default="Nil")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the corresponding MonthlyFinancialSummary
        summary, created = MonthlyFinancialSummary.objects.get_or_create(
            month=self.date.replace(day=1)
        )
        summary.total_deposits += self.amount
        summary.save()

    def __str__(self):
        return f"{self.member.name} - {self.date.strftime('%d-%m-%Y')}"


class DueDeposit(models.Model):
    member = models.ForeignKey(SocietyMember, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10,
        choices=[("Pending", "Pending"), ("Paid", "Paid")],
        default="Pending",
    )

    @classmethod
    def get_total_due_amount(cls):
        return cls.objects.filter(status="Pending").aggregate(
            models.Sum("amount")
        )["amount__sum"] or 0

    def __str__(self):
        return f"{self.member.name} - {self.date.strftime('%d-%m-%Y')}"


class BuildingProject(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    member = models.ForeignKey(SocietyMember, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.member.name}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ContributionPlan(models.Model):
    description = models.CharField(max_length=100)
    amount = models.PositiveBigIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.description
