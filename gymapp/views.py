from django.shortcuts import render, redirect

from gymapp.models import *

from django.contrib import messages

# Create your views here.

def home(request):
    '''
    Simple homepage + contact/enquiry form
    '''
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')

        if name and email and mobile and message:
            Enquiry.objects.create(
                name=name,
                email=email,
                mobile=mobile,
                message=message
            )
            messages.success(request, 'Your enquiry has been submitted successfully.')
            return redirect('home') # redirect to the home page after successfull submission
        else:
            message.error(request, 'Please fill in all the fields before submitting the form')

    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

from django.contrib.auth import authenticate, login, logout

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and getattr(user, 'role', None) == 'ADMIN': # check if the user is an admin/staff
            login(request, user) # log the user in using Django's built-in login function
            messages.success(request, 'Logged in successfully!.')
            return redirect('admin_dashboard') # Redirect to the admin dashboard

        else:
            messages.error(request, 'Invalid credentials or not an admin')
    return render(request, 'admin_login.html')

def admin_required(view_func):
    '''
    Decorator to ensure that the user is an admin before accessing certain views.
    '''
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'ADMIN':
            messages.error(request, 'You must be logged in as an admin to access this page.')
            return redirect('admin_login') # Redirect to the admin login page
        return view_func(request, *args, **kwargs)
    return wrapper

@admin_required
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')

def logout_view(request):
    logout(request)  # log the user out using Django's built-in logout function
    messages.success(request, 'Logged out successfully!')
    return redirect('home') # Redirect to the home page after logout

