# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from employees.decorators import admin_or_hr_required
from .models import Department


@login_required
@admin_or_hr_required
def department_list(request):
    departments = Department.objects.all().order_by('name')

    for department in departments:
        department.employee_count = department.employeeprofile_set.count()
        department.status = 'Active'

    return render(request, 'hrms/departments.html', {
        'departments': departments,
        'user_role': request.user.role,
    })


@login_required
@admin_or_hr_required

def department_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if name:
            Department.objects.create(
                name=name,
                description=description
            )

            messages.success(
                request,
                'Department added successfully.'
            )

            return redirect('departments')

        messages.error(
            request,
            'Department name is required.'
        )

    return render(request, 'hrms/department_form.html', {
        'user_role': request.user.role,
        'form_title': 'Add Department',
    })


@login_required
@admin_or_hr_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if name:
            department.name = name
            department.description = description
            department.save()

            messages.success(
                request,
                'Department updated successfully.'
            )

            return redirect('departments')

        messages.error(
            request,
            'Department name is required.'
        )

    return render(request, 'hrms/department_form.html', {
        'department': department,
        'user_role': request.user.role,
        'form_title': 'Edit Department',
    })


@login_required
@admin_or_hr_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        department.delete()

        messages.success(
            request,
            'Department deleted successfully.'
        )

        return redirect('departments')

    return render(request, 'hrms/departments.html', {
        'departments': Department.objects.all().order_by('name'),
        'user_role': request.user.role,
    })
