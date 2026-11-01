from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
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
    query = request.GET.get('q', '').strip()
    is_json = (
        request.GET.get('format') == 'json'
        or request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
    )
    results = []
    error = None

    if query:
        try:
            results = search_media(query, media_type)
        except Exception:
            error = "Couldn't reach the search service right now. Try again in a moment."

    if is_json:
        serialized = []
        for item in results:
            rel_date = item.get('media_release_date')
            serialized.append({
                'external_id': str(item.get('external_id') or ''),
                'media_type': item.get('media_type') or media_type,
                'media_title': item.get('media_title') or '',
                'media_description': item.get('media_description') or '',
                'media_image': item.get('media_image') or '',
                'media_release_date': rel_date.strftime('%Y-%m-%d') if rel_date else '',
                'media_year': str(rel_date.year) if rel_date else '',
                'media_rate': item.get('media_rate'),
                'genre': item.get('genre') or [],
            })
        return JsonResponse({
            'results': serialized,
            'query': query,
            'media_type': media_type,
            'error': error,
        })

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

    is_json = (
        request.POST.get('format') == 'json'
        or request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
    )

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

    message = f'Added "{media.media_title}" to your library!' if created else f'"{media.media_title}" is already in your library.'

    if is_json:
        return JsonResponse({
            'success': True,
            'created': created,
            'message': message,
            'media_id': media.id,
            'media_title': media.media_title,
        })

    if created:
        messages.success(request, message)
    else:
        messages.info(request, message)

    return redirect('library:list')
