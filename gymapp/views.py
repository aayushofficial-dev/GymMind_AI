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