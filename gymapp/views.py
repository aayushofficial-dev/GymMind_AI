from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import *


def home(request):
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
            return redirect('home')
        else:
            messages.error(request, 'Please fill in all the fields before submitting the form.')

    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and getattr(user, 'role', None) == 'ADMIN':
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin.')

    return render(request, 'admin_login.html')


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'ADMIN':
            messages.error(request, 'You must be logged in as an admin to access this page.')
            return redirect('admin_login')

        return view_func(request, *args, **kwargs)

    return wrapper


@admin_required
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


@admin_required
def admin_plans_list(request):
    plans = MembershipPlan.objects.all().order_by('duration_months')
    return render(request, 'admin_plans_list.html', {'plans': plans})


@admin_required
def admin_plan_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        duration_months = request.POST.get('duration_months')
        fee = request.POST.get('fee')
        description = request.POST.get('description')

        if name and duration_months and fee:
            MembershipPlan.objects.create(
                name=name,
                duration_months=duration_months,
                fee=fee,
                description=description
            )

            messages.success(request, 'Membership Plan added successfully!')
            return redirect('admin_plans_list')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'admin_plan_form.html', {'mode': 'add'})


@admin_required
def admin_plan_edit(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        duration_months = request.POST.get('duration_months')
        fee = request.POST.get('fee')
        description = request.POST.get('description')

        if name and duration_months and fee:
            plan.name = name
            plan.duration_months = duration_months
            plan.fee = fee
            plan.description = description
            plan.save()

            messages.success(request, 'Membership plan updated successfully!')
            return redirect('admin_plans_list')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(
        request,
        'admin_plan_form.html',
        {
            'plan': plan,
            'mode': 'edit'
        }
    )


@admin_required
def admin_plan_delete(request, plan_id):
    plan = get_object_or_404(MembershipPlan, id=plan_id)

    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Membership plan deleted successfully!')
        return redirect('admin_plans_list')

    return redirect('admin_plans_list')


@admin_required
def admin_trainers_list(request):
    trainers = Trainer.objects.all().order_by('name')
    return render(request, 'admin_trainers_list.html', {'trainers': trainers})


@admin_required
def admin_trainer_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        specialization = request.POST.get('specialization')
        shift_timing = request.POST.get('shift_timing')

        if name and mobile and specialization and shift_timing:
            Trainer.objects.create(
                name=name,
                mobile=mobile,
                specialization=specialization,
                shift_timing=shift_timing
            )

            messages.success(request, 'Trainer added successfully!')
            return redirect('admin_trainers_list')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(request, 'admin_trainer_form.html', {'mode': 'add'})


@admin_required
def admin_trainer_edit(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        specialization = request.POST.get('specialization')
        shift_timing = request.POST.get('shift_timing')

        if name and mobile and specialization and shift_timing:
            trainer.name = name
            trainer.mobile = mobile
            trainer.specialization = specialization
            trainer.shift_timing = shift_timing
            trainer.save()

            messages.success(request, 'Trainer updated successfully!')
            return redirect('admin_trainers_list')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(
        request,
        'admin_trainer_form.html',
        {
            'trainer': trainer,
            'mode': 'edit'
        }
    )


@admin_required
def admin_trainer_delete(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)

    if request.method == 'POST':
        trainer.delete()
        messages.success(request, 'Trainer deleted successfully!')
        return redirect('admin_trainers_list')

    return redirect('admin_trainers_list')


@admin_required
def admin_members_list(request):
    search = request.GET.get('search', '')

    members = MemberProfile.objects.all().select_related('user', 'plan')

    if search:
        members = members.filter(full_name__icontains=search)

    return render(
        request,
        'admin_members_list.html',
        {
            'members': members,
            'search': search
        }
    )


@admin_required
def admin_member_add(request):
    plans = MembershipPlan.objects.all().order_by('duration_months')
    trainers = Trainer.objects.all().order_by('name')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        join_date = request.POST.get('join_date') or timezone.now().date()
        plan_id = request.POST.get('plan_id')
        trainer_id = request.POST.get('trainer_id')

        if User.objects.filter(username=username).exists():
            messages.error(
                request,
                'Username already exists. Please choose a different username.'
            )
            return redirect('admin_member_add')

        if not username or not password or not full_name or not mobile or not age or not gender or not address:
            messages.error(request, 'Please fill in all the required fields.')
            return redirect('admin_member_add')

        user = User.objects.create_user(
            username=username,
            password=password,
            role='MEMBER'
        )

        plan = MembershipPlan.objects.get(id=plan_id) if plan_id else None
        trainer = Trainer.objects.get(id=trainer_id) if trainer_id else None

        MemberProfile.objects.create(
            user=user,
            full_name=full_name,
            mobile=mobile,
            age=age,
            gender=gender,
            address=address,
            join_date=join_date,
            plan=plan,
            trainer=trainer
        )

        messages.success(request, 'Member added successfully!')
        return redirect('admin_members_list')

    return render(
        request,
        'admin_member_form.html',
        {
            'plans': plans,
            'trainers': trainers,
            'mode': 'add'
        }
    )


@admin_required
def admin_member_edit(request, member_id):
    member = get_object_or_404(MemberProfile, id=member_id)

    plans = MembershipPlan.objects.all().order_by('duration_months')
    trainers = Trainer.objects.all().order_by('name')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        mobile = request.POST.get('mobile')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        join_date = request.POST.get('join_date') or member.join_date

        plan_id = request.POST.get('plan_id')
        trainer_id = request.POST.get('trainer_id')

        plan = MembershipPlan.objects.get(id=plan_id) if plan_id else None
        trainer = Trainer.objects.get(id=trainer_id) if trainer_id else None

        if full_name and mobile and age and gender and address and join_date:
            member.full_name = full_name
            member.mobile = mobile
            member.age = age
            member.gender = gender
            member.address = address
            member.join_date = join_date
            member.plan = plan
            member.trainer = trainer
            member.save()

            messages.success(request, 'Member updated successfully!')
            return redirect('admin_members_list')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(
        request,
        'admin_member_form.html',
        {
            'member': member,
            'plans': plans,
            'trainers': trainers,
            'mode': 'edit'
        }
    )


@admin_required
def admin_member_delete(request, member_id):
    member = get_object_or_404(MemberProfile, id=member_id)

    if request.method == 'POST':
        user = member.user
        user.delete()

        messages.success(request, 'Member deleted successfully!')
        return redirect('admin_members_list')

    return redirect('admin_members_list')


@admin_required
def admin_attendance_list(request):
    today = timezone.now().date()

    selected_date = request.GET.get('date', str(today))
    selected_member_id = request.GET.get('member_id', '')

    attendances = Attendance.objects.all().select_related('member').filter(
        date=selected_date
    )

    if selected_member_id:
        attendances = attendances.filter(member_id=selected_member_id)

    members = MemberProfile.objects.all().order_by('full_name')

    return render(
        request,
        'admin_attendance_list.html',
        {
            'attendances': attendances,
            'members': members,
            'today': today,
            'selected_member_id': selected_member_id,
            'selected_date': selected_date
        }
    )


@admin_required
def admin_attendance_add(request):
    members = MemberProfile.objects.all().order_by('full_name')

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        date = request.POST.get('date') or timezone.now().date()
        time_in = request.POST.get('time_in')

        if not member_id:
            messages.error(request, 'Please select a member.')
            return redirect('admin_attendance_add')

        if not time_in:
            messages.error(request, 'Please enter the time in.')
            return redirect('admin_attendance_add')

        member = get_object_or_404(MemberProfile, id=member_id)

        attendance, created = Attendance.objects.get_or_create(
            member=member,
            date=date,
            defaults={
                'time_in': time_in
            }
        )

        if not created:
            attendance.time_in = time_in
            attendance.save()
            messages.info(request, 'Attendance updated successfully!')
        else:
            messages.success(request, 'Attendance recorded successfully!')

        return redirect('admin_attendance_list')

    return render(
        request,
        'admin_attendance_form.html',
        {
            'members': members
        }
    )


@admin_required
def admin_equipment_list(request):
    equipments = Equipment.objects.all().order_by('name')

    return render(
        request,
        'admin_equipment_list.html',
        {
            'equipments': equipments
        }
    )


@admin_required
def admin_equipment_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        units = request.POST.get('units')
        price = request.POST.get('price')
        purchase_date = request.POST.get('purchase_date') or timezone.now().date()

        if name and units and price:
            Equipment.objects.create(
                name=name,
                units=units,
                price=price,
                purchase_date=purchase_date
            )

            messages.success(request, 'Equipment added successfully!')
            return redirect('admin_equipment_list')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(
        request,
        'admin_equipment_form.html',
        {
            'mode': 'add'
        }
    )


@admin_required
def admin_equipment_edit(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        units = request.POST.get('units')
        price = request.POST.get('price')
        purchase_date = request.POST.get('purchase_date') or equipment.purchase_date

        if name and units and price:
            equipment.name = name
            equipment.units = units
            equipment.price = price
            equipment.purchase_date = purchase_date
            equipment.save()

            messages.success(request, 'Equipment updated successfully!')
            return redirect('admin_equipment_list')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    return render(
        request,
        'admin_equipment_form.html',
        {
            'equipment': equipment,
            'mode': 'edit'
        }
    )


@admin_required
def admin_equipment_delete(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)

    if request.method == 'POST':
        equipment.delete()
        messages.success(request, 'Equipment deleted successfully!')
        return redirect('admin_equipment_list')

    return redirect('admin_equipment_list')


@admin_required
def admin_enquiries_list(request):
    enquiries = Enquiry.objects.all().order_by('-created_at')

    return render(
        request,
        'admin_enquiries_list.html',
        {
            'enquiries': enquiries
        }
    )


@admin_required
def admin_enquiry_update_status(request, enquiry_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        enquiry = Enquiry.objects.get(id=enquiry_id)

        if status in ['NEW', 'SEEN', 'RESOLVED']:
            enquiry.status = status
            enquiry.save()
            messages.success(request, 'Enquiry status updated!')

    return redirect('admin_enquiries_list')


@admin_required
def admin_workout_plans_list(request):
    member_id = request.GET.get("member_id", "")

    workout_plans = WorkoutPlan.objects.select_related("member").order_by("-created_at")

    if member_id:
        workout_plans = workout_plans.filter(member_id=member_id)

    members = MemberProfile.objects.all().order_by("full_name")

    return render(
        request,
        "admin_workout_plans_list.html",
        {
            "workout_plans": workout_plans,
            "members": members,
            "selected_member_id": member_id
        }
    )

@admin_required
def admin_workout_plan_add(request):
    members = MemberProfile.objects.all().order_by('full_name')

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        title = request.POST.get('title')
        description = request.POST.get('description')

        if not member_id or not title or not description:
            messages.error(request, 'Please fill in all the required fields.')
            return redirect('admin_workout_plan_add')

        member = MemberProfile.objects.get(id=member_id)

        WorkoutPlan.objects.create(
            member=member,
            title=title,
            description=description,
        )

        messages.success(request, 'Workout plan added successfully!')
        return redirect('admin_workout_plans_list')

    return render(
        request,
        'admin_workout_plan_form.html',
        {
            'members': members
        }
    )



@admin_required
def admin_workout_plan_delete(request, plan_id):
    workout_plan = get_object_or_404(WorkoutPlan, id=plan_id)

    if request.method == 'POST':
        workout_plan.delete()
        messages.success(request, 'Workout plan deleted successfully!')
        return redirect('admin_workout_plans_list')

    return redirect('admin_workout_plans_list')


