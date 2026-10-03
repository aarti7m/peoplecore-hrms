from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import AnnouncementForm
from .models import Announcement


@login_required
def announcement_list(request):
    announcements = Announcement.objects.select_related(
        'created_by'
    ).order_by('-created_at')

    if request.method == 'POST':
        if request.user.role not in ('ADMIN', 'HR'):
            return redirect('announcements')

        form = AnnouncementForm(request.POST)

        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()

            messages.success(
                request,
                'Announcement published successfully.'
            )
            return redirect('announcements')
    else:
        form = AnnouncementForm()

    return render(request, 'hrms/announcements.html', {
        'announcements': announcements,
        'user_role': request.user.role,
        'form': form,
    })

@login_required
def announcement_delete(request, pk):
    if request.user.role not in ('ADMIN', 'HR'):
        return redirect('announcements')

    if request.method == 'POST':
        announcement = Announcement.objects.get(pk=pk)
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully.')

    return redirect('announcements')


@login_required
def announcement_edit(request, pk):
    if request.user.role not in ('ADMIN', 'HR'):
        return redirect('announcements')

    announcement = Announcement.objects.get(pk=pk)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Announcement updated successfully.'
            )
            return redirect('announcements')
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, 'hrms/announcement_edit.html', {
        'form': form,
        'announcement': announcement,
        'user_role': request.user.role,
    })
