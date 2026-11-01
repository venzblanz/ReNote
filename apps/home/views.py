from datetime import datetime

from django.shortcuts import render

from django.http import HttpResponse

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

    rewatched_media_count = len(rewatch_logs)

    rewatch_logs.sort(key=lambda x: x.rewatch_count, reverse=True)

    leaderboard = rewatch_logs[:5]



    context = {

        'logs': user_logs,

        'total_count': total_count,

        'rewatched_media_count': rewatched_media_count,

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



def custom_404_view(request, exception=None):

    return render(request, '404.html', status=404)



def custom_500_view(request):

    return render(request, '500.html', status=500)



def custom_403_view(request, exception=None):

    return render(request, '403.html', status=403)



def custom_400_view(request, exception=None):

    return render(request, '400.html', status=400)



def robots_txt_view(request):

    """

    Directives for search engine web crawlers. Allows public discovery pages while

    instructing bots to keep private user dashboards and account routes unindexed.

    """

    sitemap_url = request.build_absolute_uri('/sitemap.xml')

    content = f"""User-agent: *

Allow: /

Allow: /login/

Allow: /register/

Allow: /terms/

Allow: /privacy/

Disallow: /admin/

Disallow: /library/

Disallow: /profile/

Disallow: /settings/

Disallow: /400/

Disallow: /403/

Disallow: /404/

Disallow: /500/



Sitemap: {sitemap_url}

"""

    return HttpResponse(content.strip() + "\n", content_type="text/plain; charset=utf-8")



def sitemap_xml_view(request):

    """

    Standard XML Sitemap for search engines adhering to the sitemaps.org protocol.

    """

    base_url = f"{request.scheme}://{request.get_host()}"

    today = datetime.now().strftime("%Y-%m-%d")



    routes = [

        {"loc": f"{base_url}/", "changefreq": "daily", "priority": "1.0"},

        {"loc": f"{base_url}/login/", "changefreq": "monthly", "priority": "0.8"},

        {"loc": f"{base_url}/register/", "changefreq": "monthly", "priority": "0.8"},

        {"loc": f"{base_url}/terms/", "changefreq": "yearly", "priority": "0.4"},

        {"loc": f"{base_url}/privacy/", "changefreq": "yearly", "priority": "0.4"},

    ]



    xml_lines = [

        '<?xml version="1.0" encoding="UTF-8"?>',

        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',

    ]

    for r in routes:

        xml_lines.append("  <url>")

        xml_lines.append(f"    <loc>{r['loc']}</loc>")

        xml_lines.append(f"    <lastmod>{today}</lastmod>")

        xml_lines.append(f"    <changefreq>{r['changefreq']}</changefreq>")

        xml_lines.append(f"    <priority>{r['priority']}</priority>")

        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")



    return HttpResponse("\n".join(xml_lines), content_type="application/xml; charset=utf-8")

