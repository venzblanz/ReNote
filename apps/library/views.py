from datetime import datetime
from urllib.parse import urlencode, urlparse
import json
import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from apps.media_catalog.models import Media
from apps.user_library_log.models import UserLibraryLog
from .api import search_media

MEDIA_GENRES = {
    'all': [
        'Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy', 'Horror',
        'Mystery', 'Psychological', 'Romance', 'Sci-Fi', 'Slice of Life',
        'Supernatural', 'Thriller',
    ],
    'anime': [
        'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Fantasy', 'Horror',
        'Mahou Shoujo', 'Mecha', 'Music', 'Mystery', 'Psychological',
        'Romance', 'Sci-Fi', 'Slice of Life', 'Sports', 'Supernatural', 'Thriller',
    ],
    'manga': [
        'Action', 'Adventure', 'Comedy', 'Drama', 'Ecchi', 'Fantasy', 'Horror',
        'Mystery', 'Psychological', 'Romance', 'Sci-Fi', 'Slice of Life',
        'Sports', 'Supernatural', 'Thriller',
    ],
    'movie': [
        'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
        'Drama', 'Family', 'Fantasy', 'Horror', 'Music', 'Mystery',
        'Romance', 'Sci-Fi', 'Thriller', 'War',
    ],
    'novel': [
        'Action', 'Adventure', 'Fantasy', 'Historical', 'Horror',
        'Mystery', 'Non-Fiction', 'Romance', 'Sci-Fi', 'Thriller',
    ],
}

@login_required
def library_view(request):
    logs = (
        UserLibraryLog.objects
        .filter(user=request.user)
        .select_related('media')
        .order_by('-date_added')
    )
    return render(request, 'library/library.html', {
        'logs': logs,
        'media_genres': MEDIA_GENRES,
        'media_genres_json': json.dumps(MEDIA_GENRES),
    })

@login_required
def add_title_view(request):
    media_type = request.GET.get('media_type', 'anime').strip().lower()
    if media_type not in ('anime', 'manga', 'movie', 'novel'):
        media_type = 'anime'

    query = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    if genre.lower() == 'all':
        genre = ''

    is_json = (
        request.GET.get('format') == 'json'
        or request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('Accept', '')
    )
    results = []
    error = None

    if query or genre:
        try:
            results = search_media(query, media_type, genre=genre)
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
            'genre': genre,
            'media_type': media_type,
            'error': error,
        })

    return render(request, 'library/add_title.html', {
        'results': results,
        'media_type': media_type,
        'query': query,
        'genre': genre,
        'media_genres': MEDIA_GENRES,
        'media_genres_json': json.dumps(MEDIA_GENRES),
        'available_genres': MEDIA_GENRES.get(media_type, MEDIA_GENRES['anime']),
        'error': error,
    })

def _build_add_back_url(query, media_type, genre):
    """Build a safe return URL back to the Add Title page with active search filters."""
    mtype = (media_type or 'anime').strip().lower()
    if mtype not in ('anime', 'manga', 'movie', 'novel'):
        mtype = 'anime'

    params = {'media_type': mtype}
    if query:
        params['q'] = query
    if genre and genre.lower() != 'all':
        params['genre'] = genre
    return f"{reverse('library:add')}?{urlencode(params)}"

def _parse_preview_date(date_str):
    """Parse YYYY-MM-DD strings into date objects so template date filters work."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
    except ValueError:
        return None

@login_required
def media_preview_view(request):
    """
    Preview a search result from Add Title without saving it to the user's library.
    Uses Post-Redirect-Get backed by session storage so refreshes and Back navigation stay clean.
    """
    if request.method == 'POST':
        external_id = request.POST.get('external_id', '').strip()
        media_title = request.POST.get('media_title', '').strip()
        back_url = _build_add_back_url(
            request.POST.get('search_q', '').strip(),
            request.POST.get('search_media_type', ''),
            request.POST.get('search_genre', '').strip(),
        )
        if not external_id and not media_title:
            return redirect(back_url)

        raw_rate = request.POST.get('media_rate', '').strip()
        if raw_rate.lower() in ('', 'none', 'null'):
            raw_rate = ''

        preview_items = dict(request.session.get('preview_items') or {})
        key = uuid.uuid4().hex[:12]
        preview_items[key] = {
            'external_id': external_id,
            'media_type': (request.POST.get('media_type') or 'anime').strip().lower(),
            'media_title': media_title,
            'media_description': request.POST.get('media_description', '').strip(),
            'media_image': request.POST.get('media_image', '').strip(),
            'media_release_date': request.POST.get('media_release_date', '').strip(),
            'media_rate': raw_rate,
            'genre': [g.strip() for g in request.POST.getlist('genre') if g and g.strip()],
            'back_url': back_url,
        }
        if len(preview_items) > 10:
            for old_key in list(preview_items.keys())[:-10]:
                preview_items.pop(old_key, None)

        request.session['preview_items'] = preview_items
        request.session.modified = True
        return redirect(f"{reverse('library:preview')}?key={key}")

    key = request.GET.get('key', '').strip()
    preview_items = request.session.get('preview_items') or {}
    raw_item = preview_items.get(key)
    if not raw_item:
        return redirect('library:add')

    raw_rate = (raw_item.get('media_rate') or '').strip()
    media_data = {
        'external_id': raw_item.get('external_id', ''),
        'media_type': raw_item.get('media_type', 'anime'),
        'media_title': raw_item.get('media_title', ''),
        'media_description': raw_item.get('media_description', ''),
        'media_image': raw_item.get('media_image', ''),
        'media_release_date': _parse_preview_date(raw_item.get('media_release_date', '')),
        'media_rate': None if raw_rate.lower() in ('', 'none', 'null') else raw_rate,
        'genre': raw_item.get('genre') or [],
    }

    existing_media = None
    existing_log = None
    if media_data['external_id'] and media_data['media_type']:
        existing_media = Media.objects.filter(
            external_id=media_data['external_id'],
            media_type=media_data['media_type'],
        ).first()
        if existing_media:
            existing_log = UserLibraryLog.objects.filter(
                user=request.user,
                media=existing_media,
            ).first()

    return render(request, 'library/media_preview.html', {
        'media': media_data,
        'back_url': raw_item.get('back_url') or reverse('library:add'),
        'is_in_library': existing_log is not None,
        'existing_media': existing_media,
        'existing_log': existing_log,
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

    if request.POST.get('next') == 'detail':
        return redirect('library:detail', media_id=media.id)

    return redirect('library:list')

def _get_safe_library_back_url(request, raw_url=None):
    """Return a validated URL pointing back to the library list (preserving filter query params)."""
    library_url = reverse('library:list')
    candidate = (raw_url or '').strip()
    if not candidate:
        return library_url
    if not url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return library_url
    parsed = urlparse(candidate)
    if parsed.path != library_url:
        return library_url
    return f"{library_url}?{parsed.query}" if parsed.query else library_url

def _build_detail_redirect_url(media_id, back_url):
    """Preserve ?back=... across POST redirects on media_detail_view."""
    detail_url = reverse('library:detail', kwargs={'media_id': media_id})
    if back_url and back_url != reverse('library:list'):
        return f"{detail_url}?{urlencode({'back': back_url})}"
    return detail_url

@login_required
def media_detail_view(request, media_id):
    media = get_object_or_404(Media, id=media_id)
    user_log = UserLibraryLog.objects.filter(user=request.user, media=media).first()
    back_url = _get_safe_library_back_url(
        request,
        request.POST.get('back') or request.GET.get('back') or request.META.get('HTTP_REFERER'),
    )

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
            return redirect(_build_detail_redirect_url(media.id, back_url))

        elif action == 'remove_from_library':
            if user_log:
                user_log.delete()
                messages.info(request, f'Removed "{media.media_title}" from your library.')
            return redirect(back_url)

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
            return redirect(_build_detail_redirect_url(media.id, back_url))

    context = {
        'media': media,
        'user_log': user_log,
        'is_in_library': user_log is not None,
        'status_options': status_options,
        'is_reading': is_reading,
        'rewatch_label': rewatch_label,
        'rewatch_noun': rewatch_noun,
        'back_url': back_url,
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
