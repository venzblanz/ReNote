from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, AVAILABLE_AVATARS
from apps.user_library_log.models import UserLibraryLog


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.profile_name = request.POST.get('profile_name', '').strip()
        profile.bio = request.POST.get('bio', '').strip()
        selected_avatar = request.POST.get('profile_image', '').strip()
        if selected_avatar and selected_avatar in AVAILABLE_AVATARS:
            profile.profile_image = selected_avatar
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('user_profile:profile')

    user_logs = (
        UserLibraryLog.objects
        .filter(user=request.user)
        .select_related('media')
        .order_by('-date_added')
    )

    total_titles = user_logs.count()
    anime_count = 0
    manga_count = 0
    movie_count = 0
    novel_count = 0
    total_rewatches = 0
    genre_counts = {}

    for log in user_logs:
        mtype = (log.media.media_type or '').strip().lower()
        if mtype == 'anime':
            anime_count += 1
        elif mtype == 'manga':
            manga_count += 1
        elif mtype == 'movie':
            movie_count += 1
        elif mtype in ('novel', 'light novel'):
            novel_count += 1

        total_rewatches += (log.rewatch_count or 0)

        for g in (log.media.genre or []):
            if g and isinstance(g, str):
                cleaned_g = g.strip()
                if cleaned_g:
                    genre_counts[cleaned_g] = genre_counts.get(cleaned_g, 0) + 1

    # Favorite genre based on which genre the user has the most in the list
    if genre_counts:
        top_genres_sorted = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        favorite_genre = top_genres_sorted[0][0]
        favorite_genre_count = top_genres_sorted[0][1]
        top_genres = [{'name': name, 'count': cnt} for name, cnt in top_genres_sorted[:6]]
    else:
        favorite_genre = "None yet"
        favorite_genre_count = 0
        top_genres = []

    # Favorite items (is_favorite == True, or top rated >= 4 stars)
    favorite_logs = [log for log in user_logs if log.is_favorite]
    if not favorite_logs:
        favorite_logs = [log for log in user_logs if (log.personal_rate or 0) >= 4]

    recent_activity = user_logs[:6]

    context = {
        'profile': profile,
        'total_titles': total_titles,
        'anime_count': anime_count,
        'manga_count': manga_count,
        'movie_count': movie_count,
        'novel_count': novel_count,
        'total_rewatches': total_rewatches,
        'favorite_genre': favorite_genre,
        'favorite_genre_count': favorite_genre_count,
        'top_genres': top_genres,
        'favorite_logs': favorite_logs[:6],
        'recent_activity': recent_activity,
    }
    return render(request, 'user_profile/profile.html', context)
