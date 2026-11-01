from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.user_library_log.models import UserLibraryLog


@login_required
def home_view(request):
    user_logs = (
        UserLibraryLog.objects
        .filter(user=request.user)
        .select_related('media')
        .order_by('-date_added')
    )

    total_count = user_logs.count()
    anime_count = 0
    manga_count = 0
    movie_count = 0
    novel_count = 0
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

        for g in (log.media.genre or []):
            if g:
                genre_counts[g] = genre_counts.get(g, 0) + 1

    if total_count > 0:
        anime_pct = round((anime_count / total_count) * 100)
        manga_pct = round((manga_count / total_count) * 100)
        movie_pct = round((movie_count / total_count) * 100)
        novel_pct = round((novel_count / total_count) * 100)
    else:
        anime_pct = manga_pct = movie_pct = novel_pct = 0

    top_genres_raw = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:4]
    top_genres = []
    for gname, count in top_genres_raw:
        pct = round((count / total_count) * 100) if total_count > 0 else 0
        top_genres.append({'name': gname, 'count': count, 'percent': pct})

    # Leaderboard: items with rewatches (or recent titles if none rewatched yet)
    rewatch_logs = [log for log in user_logs if (log.rewatch_count or 0) > 0]
    rewatch_logs.sort(key=lambda x: x.rewatch_count, reverse=True)
    leaderboard = rewatch_logs[:5]

    context = {
        'logs': user_logs,
        'total_count': total_count,
        'anime_count': anime_count,
        'manga_count': manga_count,
        'movie_count': movie_count,
        'novel_count': novel_count,
        'anime_pct': anime_pct,
        'manga_pct': manga_pct,
        'movie_pct': movie_pct,
        'novel_pct': novel_pct,
        'top_genres': top_genres,
        'leaderboard': leaderboard,
    }
    return render(request, 'home/home.html', context)
