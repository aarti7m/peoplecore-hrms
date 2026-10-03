
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from employees.decorators import admin_or_hr_required

from .forms import LoginForm
from .models import User
from departments.models import Department
from employees.models import EmployeeProfile
from leaves.models import LeaveRequest
from attendance.models import Attendance
from announcements.models import Announcement


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'hrms/login.html', {'form': form})


@login_required
def dashboard(request):
    total_employees = User.objects.filter(role='EMPLOYEE').count()
    total_hr = User.objects.filter(role='HR').count()
    total_departments = Department.objects.count()
    from django.db.models import Count
    departments = Department.objects.annotate(employee_count=Count('employeeprofile')).order_by('-employee_count')
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').count()
    pending_requests = LeaveRequest.objects.filter(employee=request.user, status='PENDING').count()

    # Latest attendance date
    latest_attendance = Attendance.objects.order_by('-date').first()
    attendance_date = latest_attendance.date if latest_attendance else None

    if attendance_date:
        present_today = Attendance.objects.filter(
            date=attendance_date,
            status='PRESENT'
        ).count()

        absent_today = Attendance.objects.filter(
            date=attendance_date,
            status='ABSENT'
        ).count()
    else:
        present_today = 0
        absent_today = 0

    total_attendance_today = present_today + absent_today

    if total_attendance_today:
        attendance_rate = round(
            (present_today / total_attendance_today) * 100
        )
    else:
        attendance_rate = 0

    # Monthly attendance for the last 6 months
    from django.db.models import Count, Q
    from django.db.models.functions import TruncMonth
    monthly_qs = Attendance.objects.filter(
        status__in=["PRESENT", "ABSENT"]
    ).annotate(
        month=TruncMonth("date")
    ).values("month").annotate(
        total=Count("id"),
        present=Count("id", filter=Q(status="PRESENT"))
    ).order_by("month")[:6]

    monthly_attendance = []
    for item in monthly_qs:
        percentage = round((item["present"] / item["total"]) * 100) if item["total"] else 0
        monthly_attendance.append({
            "month": item["month"].strftime("%b"),
            "percentage": percentage,
        })

    # Recent data
    recent_leaves = LeaveRequest.objects.select_related(
        'employee'
    ).order_by('-applied_at')[:5]

    recent_attendance = Attendance.objects.filter(
        employee=request.user
    ).order_by('-date')[:3]

    announcements = Announcement.objects.select_related(
        'created_by'
    ).order_by('-created_at')[:5]

    employee_profile = None

    if request.user.role == 'EMPLOYEE':
       employee_profile = EmployeeProfile.objects.filter(
          user=request.user
       ).first()

    attendance_summary = {
        "PRESENT": round((present_today / total_attendance_today) * 100) if total_attendance_today else 0,
        "ABSENT": round((absent_today / total_attendance_today) * 100) if total_attendance_today else 0,
    }

    context = {
        'total_employees': total_employees,
        'total_hr': total_hr,
        'total_departments': total_departments,
        'departments': departments,
        'pending_leaves': pending_leaves,
        'pending_requests': pending_requests,
        'present_today': present_today,
        'absent_today': absent_today,
        'attendance_rate': attendance_rate,
        'attendance_summary': attendance_summary,
        'recent_leaves': recent_leaves,
        'recent_attendance': recent_attendance,
        'announcements': announcements,
        'notification_count': pending_leaves,
        'monthly_attendance': monthly_attendance,
        'user_role': request.user.role,
        'employee': employee_profile,
    }

    if request.user.role == 'ADMIN':
        return render(
            request,
            'hrms/admin_dashboard.html',
            context
        )

    elif request.user.role == 'HR':
        return render(
            request,
            'hrms/hr_dashboard.html',
            context
        )

    return render(
        request,
        'hrms/employee_dashboard.html',
       context
    )


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@admin_or_hr_required
def export_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="peoplecore_attendance_report.csv"'

    import csv
    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Employee Name', 'Department', 'Date', 'Status', 'Check In', 'Check Out'])

    records = Attendance.objects.select_related(
        'employee',
        'employee__employeeprofile',
        'employee__employeeprofile__department',
    ).filter(
        status__in=['PRESENT', 'ABSENT']
    ).order_by('-date')

    for record in records:
        profile = getattr(record.employee, 'employeeprofile', None)
        department = profile.department.name if profile and profile.department else ''
        employee_id = profile.employee_id if profile else ''
        writer.writerow([
            employee_id,
            record.employee.get_full_name() or record.employee.username,
            department,
            record.date,
            record.get_status_display(),
            record.check_in or '',
            record.check_out or '',
        ])

    return response


@login_required
@admin_or_hr_required
def reports(request):
    from django.db.models import Count

    total_employees = User.objects.filter(
        role='EMPLOYEE'
    ).count()

    inactive_employees = User.objects.filter(
        role='EMPLOYEE', is_active=False
    ).count()

    latest_attendance = Attendance.objects.order_by("-date").first()
    latest_date = latest_attendance.date if latest_attendance else None

    if latest_date:
        present_count = Attendance.objects.filter(
            date=latest_date,
            status="PRESENT"
        ).count()

        total_attendance = Attendance.objects.filter(
            date=latest_date,
            status__in=["PRESENT", "ABSENT"]
        ).count()
    else:
        present_count = 0
        total_attendance = 0

    if total_attendance:
        attendance_rate = round(
            (present_count / total_attendance) * 100,
            1
        )
    else:
        attendance_rate = 0

    approved_leave = LeaveRequest.objects.filter(
        status='APPROVED'
    ).count()

    attendance_summary = {
        'PRESENT': 0,
        'ABSENT': 0,
    }

    if total_attendance:
        attendance_summary['PRESENT'] = round(
            (present_count / total_attendance) * 100
        )
        attendance_summary['ABSENT'] = 100 - attendance_summary['PRESENT']

    departments = Department.objects.annotate(
        employee_count=Count('employeeprofile')
    ).order_by('-employee_count')

    leave_total = LeaveRequest.objects.count()

    leave_summary = {
        'CASUAL': 0,
        'SICK': 0,
        'OTHER': 0,
    }

    if leave_total:
        for leave_type in leave_summary:
            leave_summary[leave_type] = round(
                LeaveRequest.objects.filter(
                    leave_type=leave_type
                ).count() / leave_total * 100
            )

    from django.db.models import Q
    from django.db.models.functions import TruncMonth

    monthly_qs = Attendance.objects.filter(
        status__in=['PRESENT', 'ABSENT']
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='PRESENT'))
    ).order_by('month')

    monthly_qs = list(monthly_qs)[-6:]

    monthly_attendance = []
    for item in monthly_qs:
        percentage = round((item['present'] / item['total']) * 100) if item['total'] else 0
        monthly_attendance.append({
            'month': item['month'].strftime('%b'),
            'percentage': percentage,
        })

    return render(request, 'hrms/reports.html', {
        'user_role': request.user.role,
        'total_employees': total_employees,
        'attendance_rate': f'{attendance_rate}%',
        'approved_leave': approved_leave,
        'attendance_summary': attendance_summary,
        'departments': departments,
        'leave_summary': leave_summary,
        'monthly_attendance': monthly_attendance,
    })

 
@login_required
def settings_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')

        name_parts = full_name.split(' ', 1)

        request.user.first_name = name_parts[0] if name_parts else ''
        request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        request.user.email = email

        if new_password:
            if not current_password:
                from django.contrib import messages
                messages.error(request, 'Enter your current password.')
                return redirect('settings')

            if not request.user.check_password(current_password):
                from django.contrib import messages
                messages.error(request, 'Current password is incorrect.')
                return redirect('settings')

            request.user.set_password(new_password)

        request.user.save()

        if new_password:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

        from django.contrib import messages
        messages.success(request, 'Settings updated successfully.')
        return redirect('settings')

    return render(request, 'hrms/settings.html', {
        'user_role': request.user.role,
    })
