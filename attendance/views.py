from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone

from departments.models import Department
from leaves.models import LeaveRequest
from employees.decorators import admin_or_hr_required

from .forms import AttendanceForm
from .models import Attendance


@login_required
@admin_or_hr_required
def attendance_list(request):
    attendance_records = Attendance.objects.select_related(
        'employee',
        'employee__employeeprofile',
        'employee__employeeprofile__department',
    ).all()

    search = request.GET.get('q', '').strip()
    department = request.GET.get('department', '').strip()
    status = request.GET.get('status', '').strip()
    date = request.GET.get('date', '').strip()

    if search:
        attendance_records = attendance_records.filter(
            Q(employee__first_name__icontains=search)
            | Q(employee__last_name__icontains=search)
            | Q(employee__username__icontains=search)
            | Q(employee__employeeprofile__employee_id__icontains=search)
        )

    if department:
        attendance_records = attendance_records.filter(
            employee__employeeprofile__department_id=department
        )

    if status:
        attendance_records = attendance_records.filter(status=status)

    if date:
        attendance_records = attendance_records.filter(date=date)

    departments = Department.objects.all().order_by('name')

    return render(request, 'hrms/attendance.html', {
        'attendance_records': attendance_records.order_by('-date'),
        'departments': departments,
        'user_role': request.user.role,
    })


@login_required
@admin_or_hr_required
def attendance_add(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Attendance marked successfully.'
            )
            return redirect('attendance')
    else:
        form = AttendanceForm()

    return render(request, 'hrms/attendance_form.html', {
        'form': form,
        'user_role': request.user.role,
        'form_title': 'Mark Attendance',
    })


@login_required
def my_attendance(request):
    attendance_records = Attendance.objects.filter(
        employee=request.user
    ).order_by('-date')

    today = timezone.localdate()
    month_records = attendance_records.filter(
        date__year=today.year,
        date__month=today.month,
    )

    present_count = month_records.filter(status='PRESENT').count()
    absent_count = month_records.filter(status='ABSENT').count()
    leave_count = LeaveRequest.objects.filter(
        employee=request.user,
        status='APPROVED',
        start_date__year=today.year,
        start_date__month=today.month,
    ).count()

    working_minutes = 0
    working_days = 0

    for record in month_records:
        if record.check_in and record.check_out:
            start = record.check_in.hour * 60 + record.check_in.minute
            end = record.check_out.hour * 60 + record.check_out.minute
            if end > start:
                working_minutes += end - start
                working_days += 1

    if working_days:
        average_minutes = round(working_minutes / working_days)
        average_hours = f'{average_minutes // 60}h {average_minutes % 60:02d}m'
    else:
        average_hours = '—'

    for record in attendance_records:
        if record.check_in and record.check_out:
            start = record.check_in.hour * 60 + record.check_in.minute
            end = record.check_out.hour * 60 + record.check_out.minute
            if end > start:
                minutes = end - start
                record.working_hours_display = f'{minutes // 60}h {minutes % 60:02d}m'
            else:
                record.working_hours_display = '—'
        else:
            record.working_hours_display = '—'

    return render(request, 'hrms/my_attendance.html', {
        'attendance_records': attendance_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'leave_count': leave_count,
        'average_hours': average_hours,
        'total_records': attendance_records.count(),
        'user_role': request.user.role,
    })
