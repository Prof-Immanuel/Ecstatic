from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import LoanApplication, Testimonial
from datetime import timedelta
from decimal import Decimal
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse


# Create your views here.
def index(request):
    testimonials = Testimonial.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'testimonials': testimonials})



@login_required(login_url='login')
def apply_loan(request):
    if request.method == 'POST':
        # Get the form data
        amount = request.POST.get('amount')
        loan_reason = request.POST.get('loan_reason')
        collateral = request.POST.get('collateral')
        location = request.POST.get('location')  # New field
        repayment_duration = request.POST.get('repayment_duration')  # New field
        nrc_front = request.FILES.get('nrc_front')
        nrc_back = request.FILES.get('nrc_back')
        photo = request.FILES.get('photo')
        bank_statement = request.FILES.get('bank_statement')
        pay_slip = request.FILES.get('pay_slip')

        # Validate required fields
        if not (nrc_front and nrc_back and photo):
            messages.error(request, "Please upload all required files.",  extra_tags="apply_loan")
            return redirect('apply_loan')

        try:
            # Save the loan application
            loan_application = LoanApplication.objects.create(
                user=request.user,
                amount=amount,
                loan_reason=loan_reason,
                collateral=collateral,
                location=location, 
                repayment_duration=repayment_duration,  
            )
            loan_application.save()

            # Send email to the company's email address
            company_email = "ecstaticfinance@gmail.com"  # Replace with the company's email address
            subject = "New Loan Application Submission"
            message = f"""
            A new loan application has been submitted.

            Applicant: {request.user.first_name} {request.user.last_name}
            Amount Requested: {amount}
            Loan Reason: {loan_reason}
            Collateral: {collateral}
            Location: {location}
            Repayment Duration: {repayment_duration}

            Please review the attached files for more details.
            """

            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [company_email],
            )

            # Attach files
            if nrc_front:
                nrc_front.seek(0)
                email.attach(nrc_front.name, nrc_front.read(), nrc_front.content_type)
            if nrc_back:
                nrc_back.seek(0)
                email.attach(nrc_back.name, nrc_back.read(), nrc_back.content_type)
            if photo:
                photo.seek(0)
                email.attach(photo.name, photo.read(), photo.content_type)
            if bank_statement:
                bank_statement.seek(0)
                email.attach(bank_statement.name, bank_statement.read(), bank_statement.content_type)
            if pay_slip:
                pay_slip.seek(0)
                email.attach(pay_slip.name, pay_slip.read(), pay_slip.content_type)

            # Send the email
            email.send(fail_silently=False)

            return redirect('loan_success')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}. Please try again",  extra_tags="apply_loan")
            return redirect('apply_loan')

    return render(request, 'loan_application.html')






from datetime import timedelta
from decimal import Decimal

@login_required(login_url='login')
def user_dashboard(request):
    user = request.user
    
    if user.is_superuser:
        return redirect('admin_dashboard')

    # Fetch approved loans for the user
    loans = LoanApplication.objects.filter(user=user, approved=True)

    loan_details = []
    for loan in loans:
        # Map repayment duration to interest rates
        repayment_rates = {
            "1week": Decimal("1.15"),  # 15% interest
            "2week": Decimal("1.20"),  # 20% interest
            "3week": Decimal("1.30"),  # 30% interest
            "4week": Decimal("1.40"),  # 40% interest
        }

        # Get the repayment duration and calculate total repayment
        repayment_rate = repayment_rates.get(loan.repayment_duration, Decimal("1.40"))
        total_repayment = loan.amount * repayment_rate

        # Assuming the loan is due in 30 days from the created date
        due_date = loan.created_at + timedelta(days=30)

        loan_details.append({
            'amount': loan.amount,
            'created_at': loan.created_at,
            'due_date': due_date,
            'repayment_duration': loan.repayment_duration,
            'total_repayment': total_repayment,
        })

    profile_data = {
        'name': f"{user.first_name} {user.last_name}",
        'phone': user.username,
    }

    # Handle testimonial form submission
    if request.method == "POST":
        content = request.POST.get("testimonial")
        if content:
            Testimonial.objects.create(user=user, content=content)
            messages.success(request, "Thank you! Your testimonial has been submitted for review.",  extra_tags="user_dashboard")
        else:
            messages.error(request, "Please write a testimonial before submitting.")
        return redirect("user_dashboard")

    context = {
        'loan_details': loan_details,
        'profile_data': profile_data,
    }

    return render(request, 'user_dashboard.html', context)


@login_required(login_url='login')
def loan_success(request):
    return render(request, 'loan_success.html')



@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')  # Redirect non-admin users to home
    
    # Get all loan applications
    loan_applications = LoanApplication.objects.all().order_by('-created_at')

    # Get the total number of users
    total_users = User.objects.count()

    # Count the total loan applications, approved, and pending applications
    total_loans = loan_applications.count()
    approved_loans = loan_applications.filter(approved=True).count()
    pending_loans = loan_applications.filter(approved=False).count()

    return render(request, 'admin_dashboard.html', {
        'loan_applications': loan_applications,
        'total_users': total_users,
        'total_loans': total_loans,
        'approved_loans': approved_loans,
        'pending_loans': pending_loans,
    })


@login_required(login_url='login')
def approve_application(request, application_id):
    if not request.user.is_superuser:
        return redirect('home')

    # Approve the application
    application = get_object_or_404(LoanApplication, id=application_id)
    application.approved = True  
    application.save()

    return redirect('admin_dashboard')


@login_required(login_url='login')
def reject_application(request, application_id):
    if not request.user.is_superuser:
        return redirect('home')  # Redirect non-admin users to home

    try:
        # Get the loan application to be rejected
        application = LoanApplication.objects.get(id=application_id)
        
        application.delete()

        messages.success(request, "The loan application has been rejected and deleted.")
    except LoanApplication.DoesNotExist:
        messages.error(request, "Loan application not found.",  extra_tags="reject_application")

    return redirect('admin_dashboard') 


def signup(request):
    if request.method == 'POST':  # Corrected to lowercase
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')  # Using username field to store phone number
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')  # Correct key for confirm password

       
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

       
        if User.objects.filter(username=phone_number).exists():
            messages.error(request, 'Phone number already registered!')
            return redirect('register')

     
        user = User.objects.create_user(
            username=phone_number,
            first_name=full_name.split()[0],
            last_name=" ".join(full_name.split()[1:]),
            password=password
        )
        user.save()

        
        login(request, user)

        messages.success(request, 'Registration successful! Please log in.',  extra_tags="register")
        return redirect('home') 

    return render(request, 'registration.html')



def investment_page(request):
    return render(request, 'investment_page.html')

 
@login_required
def investment_form(request):
    # Retrieve the selected amount from the query parameter
    amount = request.GET.get('amount', None)
    if not amount:
        return HttpResponse("Invalid plan. Please select a valid investment plan.", status=400)

    # Get user information
    user = request.user
    username = f"{user.first_name} {user.last_name}"
    phone = user.username  
    if request.method == 'POST':
        # Retrieve data from the submitted form
        selected_amount = request.POST.get('amount')
        investment_month = request.POST.get('month')

        # Construct the email message
        email_subject = "New Investment Request"
        email_message = (
            f"User Details:\n"
            f"Username: {username}\n"
            f"Phone: {phone}\n"
            f"\nInvestment Details:\n"
            f"Selected Investment Plan: K{selected_amount}\n"
            f"Investment Duration: {investment_month}\n\n"
            f"Expected Returns: Based on your table for {investment_month}."
        )

        # Send email
        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],  
        )

        return render(request, 'investment_success.html', {"username": username})

    return render(request, 'investment_form.html', {
        'amount': amount,
        'username': username,
        'phone': phone
    })

            
        
def user_login(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')  
        password = request.POST.get('password')

       
        user = authenticate(request, username=phone_number, password=password)

        if user is not None:
            login(request, user)  
            messages.success(request, 'Login successful!')
            return redirect('home')  
        else:
            messages.error(request, 'Invalid phone number or password!',  extra_tags="login")
            return redirect('login')  

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('home')

