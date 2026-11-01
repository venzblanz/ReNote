from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserSettings
from apps.user_profile.models import Profile, AVAILABLE_AVATARS
from apps.accounts.models import User
from apps.user_library_log.models import UserLibraryLog
from apps.library.views import MEDIA_GENRES


@login_required
def settings_view(request):
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        updated_any = False

        # 1. Update Username
        new_username = request.POST.get('username', '').strip()
        if new_username and new_username != user.username:
            if User.objects.filter(username__iexact=new_username).exclude(pk=user.pk).exists():
                messages.error(request, f'Username "{new_username}" is already taken.')
                return redirect('user_settings:settings')
            user.username = new_username
            updated_any = True

        # 2. Update Email
        new_email = request.POST.get('email', '').strip()
        if new_email and new_email != user.email:
            try:
                validate_email(new_email)
            except ValidationError:
                messages.error(request, 'Please enter a valid email address.')
                return redirect('user_settings:settings')

            if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
                messages.error(request, f'Email "{new_email}" is already in use by another account.')
                return redirect('user_settings:settings')
            user.email = new_email
            updated_any = True

        # 3. Password Change (if attempted)
        current_pw = request.POST.get('current_password', '')
        new_pw = request.POST.get('new_password', '')
        confirm_pw = request.POST.get('confirm_password', '')

        if current_pw or new_pw or confirm_pw:
            if not user.check_password(current_pw):
                messages.error(request, 'Current password is incorrect.')
                return redirect('user_settings:settings')
            if not new_pw or len(new_pw) < 6:
                messages.error(request, 'New password must be at least 6 characters long.')
                return redirect('user_settings:settings')
            if new_pw != confirm_pw:
                messages.error(request, 'New passwords do not match.')
                return redirect('user_settings:settings')

            user.set_password(new_pw)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            updated_any = True
        elif updated_any:
            user.save()

        # 4. Profile Updates
        profile.profile_name = request.POST.get('profile_name', '').strip()
        profile.bio = request.POST.get('bio', '').strip()[:200]
        profile.data_privacy_consent = request.POST.get('data_privacy_consent') == 'on'
        selected_avatar = request.POST.get('profile_image', '').strip()
        if selected_avatar and selected_avatar in AVAILABLE_AVATARS:
            profile.profile_image = selected_avatar
        profile.save()

        # 5. User Settings Updates
        settings_obj.dark_mode = request.POST.get('dark_mode') == 'on'
        settings_obj.email_notification = request.POST.get('email_notification') == 'on'
        settings_obj.save()

        messages.success(request, 'Settings saved successfully!')
        return redirect('user_settings:settings')

    # Compute top genre for display/reference
    user_logs = UserLibraryLog.objects.filter(user=request.user).select_related('media')
    genre_counts = {}
    for log in user_logs:
        for g in (log.media.genre or []):
            if g and isinstance(g, str):
                cleaned_g = g.strip()
                if cleaned_g:
                    genre_counts[cleaned_g] = genre_counts.get(cleaned_g, 0) + 1

    favorite_genre = (
        max(genre_counts.items(), key=lambda x: x[1])[0]
        if genre_counts
        else 'None yet'
    )

    all_genres = MEDIA_GENRES.get('all', [])

    return render(request, 'user_settings/settings.html', {
        'settings_obj': settings_obj,
        'profile': profile,
        'favorite_genre': favorite_genre,
        'all_genres': all_genres,
    })


@login_required
def deactivate_account_view(request):
    """Deactivate user account temporarily (sets is_active=False)."""
    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        messages.info(request, 'Your account has been deactivated. You can log in again anytime to reactivate.')
        return redirect('login:login')
    return redirect('user_settings:settings')


@login_required
def delete_account_view(request):
    """Permanently delete user account and associated data."""
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_delete', '').strip()
        if confirm_text == 'DELETE':
            user = request.user
            username = user.username
            logout(request)
            user.delete()
            messages.success(request, f'Account @{username} and all your library data have been permanently deleted.')
            return redirect('login:login')
        else:
            messages.error(request, 'You must type "DELETE" exactly to confirm account deletion.')
            return redirect('user_settings:settings')
    return redirect('user_settings:settings')
