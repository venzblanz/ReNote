from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserSettings
from apps.user_profile.models import Profile


@login_required
def settings_view(request):
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.profile_name = request.POST.get('profile_name', '')
        profile.bio = request.POST.get('bio', '')
        profile.data_privacy_consent = request.POST.get('data_privacy_consent') == 'on'
        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES['profile_image']
        profile.save()

        settings_obj.dark_mode = request.POST.get('dark_mode') == 'on'
        settings_obj.email_notification = request.POST.get('email_notification') == 'on'
        settings_obj.save()

        messages.success(request, 'Settings updated!')
        return redirect('user_settings:settings')

    return render(request, 'user_settings/settings.html', {'settings_obj': settings_obj, 'profile': profile})