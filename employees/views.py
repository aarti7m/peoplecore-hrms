

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from departments.models import Department
from .models import EmployeeProfile
from .forms import EmployeeForm, EmployeeSelfEditForm
from .decorators import admin_or_hr_required


@login_required
@admin_or_hr_required
def employee_list(request):
    employees = EmployeeProfile.objects.select_related(
        'user', 'department'
    ).order_by('employee_id')

    search = request.GET.get('q', '').strip()
    department = request.GET.get('department', '').strip()
    status = request.GET.get('status', '').strip()

    if search:
        employees = employees.filter(
            Q(employee_id__icontains=search)
            | Q(user__first_name__icontains=search)
            | Q(user__last_name__icontains=search)
            | Q(user__username__icontains=search)
            | Q(user__email__icontains=search)
        )

    if department:
        employees = employees.filter(department__name=department)

    if status == 'active':
        employees = employees.filter(user__is_active=True)
    elif status == 'inactive':
        employees = employees.filter(user__is_active=False)

    departments = Department.objects.order_by('name')

    return render(request, 'hrms/employees.html', {
        'employees': employees,
        'departments': departments,
        'user_role': request.user.role,
    })


@login_required
@admin_or_hr_required
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(
            request.POST,
            request.FILES,
            editing=False
        )

        if form.is_valid():
            employee = form.save()

            messages.success(
                request,
                f"Employee '{employee.employee_id}' added successfully."
            )

            return redirect('employees')

        messages.error(
            request,
            'Please correct the errors below.'
        )

    else:
        form = EmployeeForm(editing=False)

    departments = Department.objects.order_by('name')

    return render(request, 'hrms/employee_form.html', {
        'form': form,
        'departments': departments,
        'user_role': request.user.role,
        'form_title': 'Add Employee',
    })


@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(
        EmployeeProfile.objects.select_related(
            'user',
            'department'
        ),
        pk=pk
    )

    # Employees can edit only their own profile.
    if request.user.role == 'EMPLOYEE':
        if employee.user_id != request.user.id:
            raise PermissionDenied

        if request.method == 'POST':
            form = EmployeeSelfEditForm(
                request.POST,
                request.FILES,
                instance=employee
            )

            if form.is_valid():
                employee = form.save()

                messages.success(
                    request,
                    'Your profile was updated successfully.'
                )

                return redirect(
                    'employee_profile',
                    pk=employee.pk
                )

        else:
            form = EmployeeSelfEditForm(instance=employee)

        return render(request, 'hrms/employee_self_edit.html', {
            'employee': employee,
            'form': form,
            'user_role': request.user.role,
            'form_title': 'Edit My Profile',
        })

    # Admin and HR can edit any employee.
    if request.user.role not in ('ADMIN', 'HR'):
        raise PermissionDenied

    if request.method == 'POST':
        form = EmployeeForm(
            request.POST,
            request.FILES,
            instance=employee,
            editing=True
        )

        if form.is_valid():
            employee = form.save()

            messages.success(
                request,
                f"Employee '{employee.employee_id}' updated successfully."
            )

            return redirect(
                'employee_profile',
                pk=employee.pk
            )

        messages.error(
            request,
            'Please correct the errors below.'
        )

    else:
        form = EmployeeForm(
            instance=employee,
            editing=True
        )

    departments = Department.objects.order_by('name')

    return render(request, 'hrms/employee_form.html', {
        'employee': employee,
        'form': form,
        'departments': departments,
        'user_role': request.user.role,
        'form_title': 'Edit Employee',
    })


@login_required
def employee_profile(request, pk):
    employee = get_object_or_404(
        EmployeeProfile.objects.select_related(
            'user',
            'department'
        ),
        pk=pk
    )
    if request.user.role == 'EMPLOYEE' and employee.user_id != request.user.id:
        raise PermissionDenied

    return render(request, 'hrms/employee_profile.html', {
        'employee': employee,
        'user_role': request.user.role,
    })


@login_required
@admin_or_hr_required
def employee_toggle_status(request, pk):
    if request.method != 'POST':
        return redirect('employees')

    employee = get_object_or_404(
        EmployeeProfile.objects.select_related('user'),
        pk=pk
    )

    employee.user.is_active = not employee.user.is_active
    employee.user.save(update_fields=['is_active'])

    status = "activated" if employee.user.is_active else "deactivated"

    messages.success(
        request,
        f"Employee '{employee.employee_id}' {status} successfully."
    )

    return redirect('employees')
