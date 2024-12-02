from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F
from django.http import HttpResponseForbidden
from django.urls import reverse
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    ExpenseForm,
    DepositForm,
    DueDepositForm,
    ContributionPlanForm,
)
from .models import (
    Expense,
    Deposit,
    DueDeposit,
    SocietyMember,
    ExpenseHead,
    ContributionPlan,
)
from datetime import datetime


ALLOWED_USERS = ['sgtmomin@gmail.com', 'engg.rakhan@gmail.com']

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Check if the user's email is in the allowed list
            if user.email not in ALLOWED_USERS:
                user.delete()  # Optionally delete the user if not in the allowed list
                # Return custom error page with a redirect to the login page after a short delay
                login_url = reverse('login')  # Get the URL for the login page
                return HttpResponseForbidden(f"""
                    <html>
                    <head>
                        <style>
                            body {{
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                                font-family: Arial, sans-serif;
                                background-color: #f8d7da;
                            }}
                            .error-container {{
                                text-align: center;
                                background-color: #f44336;
                                color: white;
                                padding: 20px;
                                border-radius: 10px;
                                font-size: 2rem;
                                width: 60%;
                            }}
                        </style>
                        <script type="text/javascript">
                            setTimeout(function() {{
                                window.location.href = "{login_url}";  // Redirect to login page
                            }}, 5000);  // Redirect after 5 seconds
                        </script>
                    </head>
                    <body>
                        <div class="error-container">
                            You are not authorized to register. You will be redirected to the login page.
                        </div>
                    </body>
                    </html>
                """)
            
            # Log the user in immediately after successful registration
            login(request, user)
            messages.success(request, "Registration successful. You are now logged in.")
            return redirect("home")  # Redirect to the homepage or the desired page
    else:
        form = UserRegistrationForm()

    return render(request, "registration.html", {"form": form})




def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = UserLoginForm()
    return render(request, "login.html", {"form": form})


@login_required
def user_logout(request):
    logout(request)
    return redirect("login")


# Homepage / Dashboard View
@login_required
def home(request):
    # Total deposits, expenses, and balance
    total_deposits = Deposit.objects.aggregate(Sum("amount"))["amount__sum"] or 0
    total_expenses = Expense.objects.aggregate(Sum("amount"))["amount__sum"] or 0
    balance = total_deposits - total_expenses

    # Pending dues
    contributionplan = ContributionPlan.objects.all()
    total_incontributionplan = contributionplan.aggregate(Sum('amount'))['amount__sum'] or 0
    granttotal_incontributionplan = total_incontributionplan * 54
    due_contribution = granttotal_incontributionplan - total_deposits

    # Category-wise summary
    categories = ExpenseHead.objects.all()
    category_summary = []
    for category in categories:
        category_deposits = Deposit.objects.filter(fund_head=category).aggregate(Sum("amount"))["amount__sum"] or 0
        category_expenses = Expense.objects.filter(expense_head=category).aggregate(Sum("amount"))["amount__sum"] or 0
        category_summary.append({
            "category_name": category.name,
            "total_deposits": category_deposits,
            "total_expenses": category_expenses,
            "balance": category_deposits - category_expenses,
        })

        
    context = {
        "total_incontributionplan": total_incontributionplan,
        "granttotal_incontributionplan": granttotal_incontributionplan,
        "total_deposits": total_deposits,
        "total_expenses": total_expenses,
        "balance": balance,
        "due_contribution": due_contribution,
        "category_summary": category_summary,
        "page_title": "Dashboard",
    }
    return render(request, "dashboard.html", context)


# Member List View
@login_required

def member_list(request):
    members = SocietyMember.objects.all()
    # Create a dictionary where key is the member and value is their corresponding deposits
    member_deposits = {
        member: Deposit.objects.filter(member=member)  
        for member in members
    }

    context = {
        "members": members,
        "member_deposits": member_deposits,
    }
    
    return render(request, "member_list.html", context)



# Deposit and Expense Views
@login_required
def create_deposit(request):
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Deposit successfully added!")
            return redirect("home")
        else:
            messages.error(request, "Error: Please correct the form.")
    else:
        form = DepositForm()
    return render(request, "create_deposit.html", {"form": form})


@login_required
def create_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Expense successfully recorded!")
            return redirect("home")  
        else:
            messages.error(request, "Error: Please correct the form.")
    else:
        form = ExpenseForm()
    return render(request, "create_expense.html", {"form": form})



# Monthly Summary View

@login_required
def monthly_summary(request, year=None, month=None):
    from collections import defaultdict
    from django.db.models import Sum

    # Default to all records if no specific month/year is provided
    expenses = Expense.objects.all()
    deposits = Deposit.objects.all()

    # Group data by month
    monthly_data = defaultdict(list)
    for expense in expenses:
        monthly_data[expense.date.replace(day=1)].append({
            "date": expense.date,
            "description": expense.description,
            "type": "expense",
            "amount": expense.amount,
            "created_by": expense.created_by,
            "expense_head": expense.expense_head,
        })
    for deposit in deposits:
        monthly_data[deposit.date.replace(day=1)].append({
            "date": deposit.date,
            "description": deposit.remark,
            "type": "deposit",
            "amount": deposit.amount,
            "created_by": deposit.member,
        })

    # Compute monthly summaries
    summaries = []
    previous_balance = 0
    for month, items in sorted(monthly_data.items()):
        total_deposits = sum(i["amount"] for i in items if i["type"] == "deposit")
        total_expenses = sum(i["amount"] for i in items if i["type"] == "expense")
        final_balance = previous_balance + total_deposits - total_expenses

        summaries.append({
            "month": month,
            "previous_balance": previous_balance,
            "total_deposits": total_deposits,
            "total_expenses": total_expenses,
            "final_balance": final_balance,
        })
        previous_balance = final_balance
    active_months = Expense.objects.dates("date", "month", order="ASC")
    context = {
        "title": "Monthly Summary",
        "monthly_data": monthly_data,
        "summaries": summaries,
        "previous_month_balance": summaries[0]["previous_balance"] if summaries else 0,
        "total_deposits": sum(s["total_deposits"] for s in summaries),
        "total_expenses": sum(s["total_expenses"] for s in summaries),
        "balance": previous_balance,
        "active_months": active_months, 
    }
    return render(request, "monthly_summary.html", context)



# Fund Details View
@login_required
def fund_details(request):
    contributions = Deposit.objects.select_related("member").order_by("-date")
    total_fund = contributions.aggregate(Sum("amount"))["amount__sum"] or 0
    contributions_by_member = (
        Deposit.objects.values("member__name")
        .annotate(total_contributions=Sum("amount"))
        .order_by("-total_contributions")
    )
    return render(request, "fund_details.html", {
        "contributions": contributions,
        "total_fund": total_fund,
        "contributions_by_member": contributions_by_member,
    })

def contribution_plan_list(request):
    plans = ContributionPlan.objects.all()
    return render(request, 'contribution_plan_list.html', {'plans': plans})

def contribution_plan_detail(request, pk):
    plan = get_object_or_404(ContributionPlan, pk=pk)
    return render(request, 'contribution_plan_detail.html', {'plan': plan})

def create_contribution_plan(request):
    if request.method == 'POST':
        form = ContributionPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contribution plan created successfully!')
            return redirect('contribution_plan_list')
    else:
        form = ContributionPlanForm()
    return render(request, 'create_contribution_plan.html', {'form': form})





from django.db.models import Sum

def view_deposits(request, member_id):
    member = SocietyMember.objects.get(id=member_id)
    deposits = Deposit.objects.filter(member=member)
    contribution_plan = ContributionPlan.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_contribution_for_member = contribution_plan * member.shares if contribution_plan else 0
    total_deposit = deposits.aggregate(Sum('amount'))['amount__sum'] or 0
    dues = total_contribution_for_member - total_deposit
    advance = total_deposit - total_contribution_for_member if total_deposit > total_contribution_for_member else 0
    
    dueslist = []
    
    context = {
        'member': member,
        'deposits': deposits,
        'total_deposit': total_deposit,
        'total_contribution_for_member': total_contribution_for_member,
        'dues': dues,
        'advance': advance,
    }
    
    return render(request, 'view_deposits.html', context)


def date_wise_deposit(request):
    # Fetch all deposits
    date_wise_deposit = Deposit.objects.all().order_by('date')
    
    
    total_deposit = date_wise_deposit.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'date_wise_deposit': date_wise_deposit,
        'total_deposit': total_deposit
    }
    return render(request, 'date_wise_deposit.html', context)


def date_wise_expense(request):
    date_wise_expense = Expense.objects.all().order_by('date')

    total_expense = date_wise_expense.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        "date_wise_expense": date_wise_expense,
        'total_expense': total_expense,
    }
    return render(request, "date_wise_expense.html", context)

def month_wise_summary(request):
    # Get all deposits and expenses with month grouping
    deposits_by_month = Deposit.objects.values('date__year', 'date__month').annotate(total_deposits=Sum('amount')).order_by('date__year', 'date__month')
    expenses_by_month = Expense.objects.values('date__year', 'date__month').annotate(total_expenses=Sum('amount')).order_by('date__year', 'date__month')

    # Combine deposits and expenses into one list
    month_summary = []
    months = set()  # To keep track of unique months
    for deposit in deposits_by_month:
        months.add((deposit['date__year'], deposit['date__month']))
    for expense in expenses_by_month:
        months.add((expense['date__year'], expense['date__month']))

    # Prepare summary data for each month
    for month in months:
        year, month_number = month
        deposit = next((d for d in deposits_by_month if d['date__year'] == year and d['date__month'] == month_number), None)
        expense = next((e for e in expenses_by_month if e['date__year'] == year and e['date__month'] == month_number), None)

        month_summary.append({
            'month_name': f'{month_number}/{year}',
            'deposits': deposit['total_deposits'] if deposit else 0,
            'expenses': expense['total_expenses'] if expense else 0,
            'balance': (deposit['total_deposits'] if deposit else 0) - (expense['total_expenses'] if expense else 0),
        })

    
    total_deposits = sum(item['deposits'] for item in month_summary)
    total_expenses = sum(item['expenses'] for item in month_summary)
    total_balance = total_deposits - total_expenses

    
    context = {
        'month_summary': month_summary,
        'total_deposits': total_deposits,
        'total_expenses': total_expenses,
        'total_balance': total_balance,
    }
    return render(request, "month_wise_summary.html", context)

def monthlyreport(request):
    pass

from django.shortcuts import render
from .models import SocietyMember, Deposit, ContributionPlan
from django.db.models import Sum

def members_with_dues(request):
    members_with_dues = SocietyMember.objects.all()
    dues_list = []
    contribution_plan = ContributionPlan.objects.aggregate(Sum('amount'))['amount__sum'] or 0

    
    for member in members_with_dues:
        deposits = Deposit.objects.filter(member=member)
        total_contribution_for_member = contribution_plan * member.shares if contribution_plan else 0
        total_deposit = deposits.aggregate(Sum('amount'))['amount__sum'] or 0
        dues = total_contribution_for_member - total_deposit
        
        
        if dues > 0:
            dues_list.append({
                'member': member,
                'dues': dues,
                'total_deposit': total_deposit,
                'total_contribution_for_member': total_contribution_for_member,
            })

    context = {
        'dues_list': dues_list,  
    }
    
    return render(request, 'members_with_dues.html', context)
