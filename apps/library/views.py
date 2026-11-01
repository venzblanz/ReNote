from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.media_catalog.models import Media
from apps.user_library_log.models import UserLibraryLog
from .api import search_media
import json


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

    mtype = (media.media_type or '').strip().lower()
    default_status = 'plan to read' if mtype in ('manga', 'novel', 'light novel') else 'plan to watch'

    log_entry, created = UserLibraryLog.objects.get_or_create(
        user=request.user,
        media=media,
        defaults={'status': default_status}
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


@login_required
def media_detail_view(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    user_log = UserLibraryLog.objects.filter(user=request.user, media=media).first()

    is_reading = (media.media_type or '').strip().lower() in ('manga', 'novel', 'light novel')
    if is_reading:
        status_options = [
            ('reading', 'Reading'),
            ('plan to read', 'Plan to Read'),
            ('completed', 'Completed'),
            ('on hold', 'On Hold'),
            ('dropped', 'Dropped'),
        ]
        rewatch_label = 'Rereads'
        rewatch_noun = 'reread'
    else:
        status_options = [
            ('watching', 'Watching'),
            ('plan to watch', 'Plan to Watch'),
            ('completed', 'Completed'),
            ('on hold', 'On Hold'),
            ('dropped', 'Dropped'),
        ]
        rewatch_label = 'Rewatches'
        rewatch_noun = 'rewatch'

    if request.method == 'POST':
        action = request.POST.get('action', 'save_all')
        if action == 'add_to_library':
            default_status = 'plan to read' if is_reading else 'plan to watch'
            user_log, created = UserLibraryLog.objects.get_or_create(
                user=request.user,
                media=media,
                defaults={'status': default_status}
            )
            messages.success(request, f'Added "{media.media_title}" to your library!')
            return redirect('library:detail', media_id=media.id)

        elif action == 'remove_from_library':
            if user_log:
                user_log.delete()
                messages.info(request, f'Removed "{media.media_title}" from your library.')
            return redirect('library:list')

        elif action == 'save_all':
            if not user_log:
                default_status = 'plan to read' if is_reading else 'plan to watch'
                user_log = UserLibraryLog.objects.create(
                    user=request.user,
                    media=media,
                    status=default_status
                )

            status_val = request.POST.get('status')
            if status_val:
                user_log.status = status_val.strip().lower()

            rate_val = request.POST.get('personal_rate')
            if rate_val in (None, '', '0', 0):
                user_log.personal_rate = None
            else:
                try:
                    user_log.personal_rate = max(1, min(5, int(rate_val)))
                except (ValueError, TypeError):
                    pass

            rewatch_val = request.POST.get('rewatch_count')
            if rewatch_val is not None:
                try:
                    user_log.rewatch_count = max(0, int(rewatch_val))
                except (ValueError, TypeError):
                    pass

            user_log.media_note = request.POST.get('media_note', '').strip()
            user_log.is_favorite = ('is_favorite' in request.POST)
            user_log.save()
            messages.success(request, f'Updated your log for "{media.media_title}".')
            return redirect('library:detail', media_id=media.id)

    context = {
        'media': media,
        'user_log': user_log,
        'is_in_library': user_log is not None,
        'status_options': status_options,
        'is_reading': is_reading,
        'rewatch_label': rewatch_label,
        'rewatch_noun': rewatch_noun,
    }
    return render(request, 'library/media_detail.html', context)


@login_required
def update_library_log_view(request, media_id):
    """
    Live API endpoint for instant client-side toggling:
    - Status toggle
    - Star rate toggle (1 to 5)
    - Rewatch count increment/decrement
    - Favorite heart toggle
    - Personal comments/notes save
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    media = get_object_or_404(Media, id=media_id)
    user_log = UserLibraryLog.objects.filter(user=request.user, media=media).first()

    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            pass
    else:
        data = request.POST

    action = data.get('action')
    is_reading = (media.media_type or '').strip().lower() in ('manga', 'novel', 'light novel')
    default_status = 'plan to read' if is_reading else 'plan to watch'

    # Auto-create entry if performing an action on a catalog title
    if not user_log:
        user_log = UserLibraryLog.objects.create(
            user=request.user,
            media=media,
            status=data.get('status') or default_status
        )

    if action == 'toggle_favorite':
        user_log.is_favorite = not user_log.is_favorite
        user_log.save(update_fields=['is_favorite'])

    elif action == 'set_status':
        new_status = (data.get('status') or '').strip().lower()
        if new_status:
            user_log.status = new_status
            user_log.save(update_fields=['status'])

    elif action == 'set_rate':
        rate_val = data.get('personal_rate')
        if rate_val in (None, '', '0', 0):
            user_log.personal_rate = None
        else:
            try:
                user_log.personal_rate = max(1, min(5, int(rate_val)))
            except (ValueError, TypeError):
                pass
        user_log.save(update_fields=['personal_rate'])

    elif action == 'increment_rewatch':
        user_log.rewatch_count = (user_log.rewatch_count or 0) + 1
        user_log.save(update_fields=['rewatch_count'])

    elif action == 'decrement_rewatch':
        user_log.rewatch_count = max(0, (user_log.rewatch_count or 0) - 1)
        user_log.save(update_fields=['rewatch_count'])

    elif action == 'save_note':
        user_log.media_note = data.get('media_note', '').strip()
        user_log.save(update_fields=['media_note'])

    elif action == 'save_all' or not action:
        if 'status' in data and data.get('status'):
            user_log.status = data.get('status').strip().lower()
        if 'personal_rate' in data:
            r = data.get('personal_rate')
            if r in (None, '', '0', 0):
                user_log.personal_rate = None
            else:
                try:
                    user_log.personal_rate = max(1, min(5, int(r)))
                except (ValueError, TypeError):
                    pass
        if 'rewatch_count' in data:
            try:
                user_log.rewatch_count = max(0, int(data.get('rewatch_count', 0)))
            except (ValueError, TypeError):
                pass
        if 'media_note' in data:
            user_log.media_note = data.get('media_note', '').strip()
        if 'is_favorite' in data:
            fav = data.get('is_favorite')
            user_log.is_favorite = (fav is True or str(fav).lower() in ('true', '1'))
        user_log.save()

    return JsonResponse({
        'success': True,
        'is_in_library': True,
        'status': user_log.status,
        'status_display': user_log.status.title(),
        'personal_rate': user_log.personal_rate,
        'rewatch_count': user_log.rewatch_count,
        'media_note': user_log.media_note,
        'is_favorite': user_log.is_favorite,
    })
