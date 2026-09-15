from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserSettings


@login_required
def settings_view(request):
    settings_obj, created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        settings_obj.dark_mode = request.POST.get('dark_mode') == 'on'
        settings_obj.email_notifications = request.POST.get('email_notifications') == 'on'
        settings_obj.save()
        messages.success(request, 'Settings updated!')
        return redirect('user_settings:settings')

    return render(request, 'user_settings/settings.html', {'settings_obj': settings_obj})