from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import LeaveRequestForm
from .models import LeaveRequest


@login_required
def leave_list(request):
    if request.user.role == 'EMPLOYEE':
        leaves = LeaveRequest.objects.filter(
            employee=request.user
        )
    else:
        leaves = LeaveRequest.objects.select_related(
            'employee'
        )

    status = request.GET.get('status', '').strip()
    from_date = request.GET.get('from', '').strip()
    to_date = request.GET.get('to', '').strip()

    if status:
        leaves = leaves.filter(status=status)

    if from_date:
        leaves = leaves.filter(start_date__gte=from_date)

    if to_date:
        leaves = leaves.filter(end_date__lte=to_date)

    leaves = leaves.order_by('-applied_at')

    return render(request, 'hrms/leaves.html', {
        'leaves': leaves,
        'user_role': request.user.role,
    })


@login_required
def apply_leave(request):
    if request.user.role != 'EMPLOYEE':
        return redirect('leaves')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)

        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user
            leave.status = 'PENDING'
            leave.save()

            messages.success(
                request,
                'Leave request submitted successfully.'
            )
            return redirect('leaves')
    else:
        form = LeaveRequestForm()

    return render(request, 'hrms/apply_leave.html', {
        'form': form,
        'user_role': request.user.role,
    })


@login_required
def approve_leave(request, pk):
    if request.user.role not in ('ADMIN', 'HR'):
        return redirect('leaves')

    if request.method == 'POST':
        leave = LeaveRequest.objects.get(pk=pk)
        leave.status = 'APPROVED'
        leave.save(update_fields=['status'])
        messages.success(request, 'Leave request approved.')

    return redirect('leaves')


@login_required
def reject_leave(request, pk):
    if request.user.role not in ('ADMIN', 'HR'):
        return redirect('leaves')

    if request.method == 'POST':
        leave = LeaveRequest.objects.get(pk=pk)
        leave.status = 'REJECTED'
        leave.save(update_fields=['status'])
        messages.success(request, 'Leave request rejected.')

    return redirect('leaves')
