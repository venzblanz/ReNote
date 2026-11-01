from .models import AVAILABLE_AVATARS, DEFAULT_AVATAR, Profile


def user_avatar_processor(request):
    avatar = DEFAULT_AVATAR
    if getattr(request, 'user', None) and request.user.is_authenticated:
        try:
            profile, _ = Profile.objects.get_or_create(user=request.user)
            av_str = str(profile.profile_image or '').strip()
            if av_str in AVAILABLE_AVATARS:
                avatar = av_str
            else:
                avatar = DEFAULT_AVATAR
        except Exception:
            avatar = DEFAULT_AVATAR

    return {
        'user_avatar': avatar,
        'available_avatars': AVAILABLE_AVATARS,
    }
