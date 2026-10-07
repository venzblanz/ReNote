from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.media_catalog.models import Media
from apps.user_library_log.models import UserLibraryLog
from .api import search_media


@login_required
def library_view(request):
    logs = UserLibraryLog.objects.filter(user=request.user).select_related('media')
    return render(request, 'library/library.html', {'logs': logs})


@login_required
def add_title_view(request):
    media_type = request.GET.get('media_type', 'anime')
    query = request.GET.get('q', '')
    results = []
    error = None

    if query:
        try:
            results = search_media(query, media_type)
        except Exception:
            error = "Couldn't reach the search service right now. Try again in a moment."

    return render(request, 'library/add_title.html', {
        'results': results,
        'media_type': media_type,
        'query': query,
        'error': error,
    })


@login_required
def save_title_view(request):
    if request.method != 'POST':
        return redirect('library:add')

    media, _ = Media.objects.get_or_create(
        external_id=request.POST.get('external_id'),
        media_type=request.POST.get('media_type'),
        defaults={
            'media_title': request.POST.get('media_title', ''),
            'media_description': request.POST.get('media_description', ''),
            'media_image': request.POST.get('media_image', ''),
            'media_release_date': request.POST.get('media_release_date') or None,
            'media_rate': request.POST.get('media_rate') or None,
            'genre': request.POST.getlist('genre'),
        }
    )

    log_entry, created = UserLibraryLog.objects.get_or_create(
        user=request.user,
        media=media,
        defaults={'status': 'plan to watch'}
    )

    if created:
        messages.success(request, f'Added "{media.media_title}" to your library!')
    else:
        messages.info(request, f'"{media.media_title}" is already in your library.')

    return redirect('library:list')