from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .forms import SalaryForm
from .models import Salary


def admin_or_hr(request):
    if request.user.role not in ('ADMIN', 'HR'):
        raise PermissionDenied


@login_required
def salary_list(request):
    if request.user.role == 'EMPLOYEE':
        return redirect('my_salary')

    salaries = Salary.objects.select_related('employee').all()

    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    month = request.GET.get('month', '').strip()

    if search:
        salaries = salaries.filter(
            employee__first_name__icontains=search
        ) | salaries.filter(
            employee__last_name__icontains=search
        ) | salaries.filter(
            employee__username__icontains=search
        )

    if status:
        salaries = salaries.filter(status=status)

    if month:
        salaries = salaries.filter(month=month)

    return render(request, 'hrms/salary.html', {
        'salaries': salaries.order_by('-month', 'employee__first_name'),
        'user_role': request.user.role,
    })


@login_required
def salary_add(request):
    admin_or_hr(request)

    if request.method == 'POST':
        form = SalaryForm(request.POST)
        if form.is_valid():
            salary = form.save()
            messages.success(
                request,
                f"Salary record for {salary.employee.get_full_name() or salary.employee.username} added successfully."
            )
            return redirect('salary')
    else:
        form = SalaryForm()

    return render(request, 'hrms/salary_form.html', {
        'form': form,
        'user_role': request.user.role,
        'form_title': 'Add Salary',
    })


@login_required
def salary_edit(request, pk):
    admin_or_hr(request)

    salary = get_object_or_404(
        Salary.objects.select_related('employee'),
        pk=pk
    )

    if request.method == 'POST':
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary record updated successfully.')
            return redirect('salary')
    else:
        form = SalaryForm(instance=salary)

    return render(request, 'hrms/salary_form.html', {
        'form': form,
        'user_role': request.user.role,
        'form_title': 'Edit Salary',
        'salary': salary,
    })


@login_required
def my_salary(request):
    if request.user.role != 'EMPLOYEE':
        return redirect('salary')

    salaries = Salary.objects.filter(
        employee=request.user
    ).order_by('-month')

    return render(request, 'hrms/my_salary.html', {
        'salaries': salaries,
        'user_role': request.user.role,
    })
