from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from apps.user_profile.models import Profile
from apps.user_settings.models import UserSettings
from apps.accounts.models import User
from apps.media_catalog.models import Media
from apps.user_library_log.models import UserLibraryLog, LibraryFolder, FolderItem

def run_database_sync():
    if 'supabase' not in settings.DATABASES:
        return {
            'success': False,
            'error': 'Supabase database is not configured. Ensure that the SUPABASE_DB_URL in the .env file is available and correct.'
        }
    try:
        connections['supabase'].ensure_connection()
    except OperationalError as e:
        return {
            'success': False,
            'error': f'Cannot establish connection to the Supabase database: {str(e)}'
        }

    stats = {
        'pulled': 0,
        'pushed': 0,
        'media_synced': 0,
        'logs_synced': 0,
        'folders_synced': 0,
    }

    # Sync Users muna
    remote_users = {u.username: u for u in User.objects.using('supabase').all()}
    local_users = {u.username: u for u in User.objects.using('default').all()}

    for username, r_user in remote_users.items():
        if username not in local_users:
            l_user = User.objects.using('default').create(
                username = r_user.username,
                email= r_user.email,
                password = r_user.password,
                is_active = r_user.is_active,
                is_staff = r_user.is_staff,
                is_superuser = r_user.is_superuser,
            )
            local_users[username] = l_user
            stats['pulled'] += 1

    # Sync Medias dayon IM GETTING BRAIN FUCKED!
    remote_media = {(m.external_id, m.media_type): m for m in Media.objects.using('supabase').all()}
    local_media = {(m.external_id, m.media_type): m for m in Media.objects.using('default').all()}

    # Pull from supa to local SQLite
    for key, r_media in remote_media.items():
        if key not in local_media:
            l_media = Media.objects.using('default').create(
                external_id = r_media.external_id,
                media_type = r_media.media_type,
                media_title = r_media.media_title,
                media_description = r_media.media_description,
                media_image = r_media.media_image,
                media_release_date = r_media.media_release_date,
                media_rate = r_media.media_rate,
                genre = r_media.genre or [],
            )
            local_media[key] = l_media
            stats['media_synced'] += 1
            stats['pulled'] += 1

    # Push from Local to supa
    for key, l_med in local_media.items():
        if key not in remote_media:
            r_med = Media.objects.using('supabase').create(
                external_id = l_med.external_id,
                media_type = l_med.media_type,
                media_title = l_med.media_title,
                media_description = l_med.media_description,
                media_image = l_med.media_image,
                media_release_date = l_med.media_release_date,
                media_rate = l_med.media_rate,
                genre = l_med.genre or [],
            )
            remote_media[key] = r_med
            stats['media_synced'] += 1
            stats['pushed'] += 1

    # Sync each User's Library
    local_logs = {}
    for log in UserLibraryLog.objects.using('default').select_related('user', 'media').all():
        key = (log.user.username, log.media.external_id, log.media.media_type)
        local_logs[key] = log

    remote_logs = {}
    for log in UserLibraryLog.objects.using('supabase').select_related('user', 'media').all():
        key = (log.user.username, log.media.external_id, log.media.media_type)
        remote_logs[key] = log

    all_log_keys = set(local_logs.keys()).union(set(remote_logs.keys()))

    for key in all_log_keys:
        l_log = local_logs.get(key)
        r_log = remote_logs.get(key)
        username, ext_id, mtype = key

        l_user = local_users.get(username)
        r_user = remote_users.get(username)
        l_med = local_media.get((ext_id, mtype))
        r_med = remote_media.get((ext_id, mtype))

        # In local but not in remote so push to supa
        if l_log and not r_log:
            if r_user and r_med:
                UserLibraryLog.objects.using('supabase').create(
                    user = r_user,
                    media = r_med,
                    personal_rate = l_log.personal_rate,
                    status = l_log.status,
                    rewatch_count = l_log.rewatch_count,
                    media_note = l_log.media_note,
                    is_favorite = l_log.is_favorite,
                    is_deleted = l_log.is_deleted,
                )
                stats['logs_synced'] += 1
                stats['pushed'] += 1

        # In remote but not in local so pull from supa
        elif r_log and not l_log:
            if l_user and l_med:
                UserLibraryLog.objects.using('default').create(
                    user = l_user,
                    media = l_med,
                    personal_rate = r_log.personal_rate,
                    status = r_log.status,
                    rewatch_count = r_log.rewatch_count,
                    media_note = r_log.media_note,
                    is_favorite = r_log.is_favorite,
                    is_deleted = r_log.is_deleted,
                )
                stats['logs_synced'] += 1
                stats['pulled'] += 1

        # exists in both, check time diff then update
        elif l_log and r_log:
            if l_log.updated_at > r_log.updated_at:
                # if ang local log is more recent, update remote log
                if l_log.updated_at > r_log.updated_at:
                    r_log.personal_rate = l_log.personal_rate
                    r_log.status = l_log.status
                    r_log.rewatch_count = l_log.rewatch_count
                    r_log.media_note = l_log.media_note
                    r_log.is_favorite = l_log.is_favorite
                    r_log.is_deleted = l_log.is_deleted
                    r_log.save(using='supabase')
                    stats['logs_synced'] += 1
                    stats['pushed'] += 1
                elif r_log.updated_at > l_log.updated_at:
                    l_log.personal_rate = r_log.personal_rate
                    l_log.status = r_log.status
                    l_log.rewatch_count = r_log.rewatch_count
                    l_log.media_note = r_log.media_note
                    l_log.is_favorite = r_log.is_favorite
                    l_log.is_deleted = r_log.is_deleted
                    l_log.save(using='default')
                    stats['logs_synced'] += 1
                    stats['pulled'] += 1

    # Sync the folders and its items
    local_folders = {(f.user.username, f.name): f for f in LibraryFolder.objects.using('default').select_related('user').all()}
    remote_folders = {(f.user.username, f.name): f for f in LibraryFolder.objects.using('supabase').select_related('user').all()}
    all_folder_keys = set(local_folders.keys()).union(set(remote_folders.keys()))

    for key in all_folder_keys:
        l_f = local_folders.get(key)
        r_f = remote_folders.get(key)
        username, folder_name = key
        l_user = local_users.get(username)
        r_user = remote_users.get(username)

        # exists locally
        if l_f and not r_f:
            if r_user:
                LibraryFolder.objects.using('supabase').create(
                    user = r_user,
                    name = l_f.name,
                    description = l_f.description,
                    is_deleted = l_f.is_deleted,
                )
                stats['folders_synced'] += 1
                stats['pushed'] += 1

        # exists on supa
        elif r_f and not l_f:
            if l_user:
                LibraryFolder.objects.using('default').create(
                    user = l_user,
                    name = r_f.name,
                    description = r_f.description,
                    is_deleted = r_f.is_deleted
                )
                stats['folders_synced'] += 1
                stats['pulled'] += 1

        # exists on both so update
        elif r_f and l_f:
            if l_f.updated_at and r_f.updated_at:
                if r_f.updated_at > l_f.updated_at:
                    l_f.description = r_f.description
                    l_f.is_deleted = r_f.is_deleted
                    l_f.save(using='default')
                    stats['folders_synced'] += 1
                    stats['pulled'] += 1
                elif l_f.updated_at > r_f.updated_at:
                    r_f.description = l_f.description
                    r_f.is_deleted = l_f.is_deleted
                    r_f.save(using='supabase')
                    stats['folders_synced'] += 1
                    stats['pushed'] += 1

     # Sync Profile
    remote_profiles = {p.user.username: p for p in Profile.objects.using('supabase').select_related('user').all()}
    local_profiles = {p.user.username: p for p in Profile.objects.using('default').select_related('user').all()}
    all_profiles = set(remote_profiles.keys()).union(set(local_profiles.keys()))

    for username in all_profiles:
        r_prof = remote_profiles.get(username)
        l_prof = local_profiles.get(username)
        l_user = local_users.get(username)
        r_user = remote_users.get(username)

        if r_prof and not l_prof:
            if l_user:
                Profile.objects.using('default').create(
                    user = l_user,
                    profile_name = r_prof.profile_name,
                    bio = r_prof.bio,
                    profile_image = r_prof.profile_image,
                    data_privacy_consent = r_prof.data_privacy_consent,
                )
                stats['pulled'] += 1
        elif l_prof and not r_prof:
            if r_user:
                Profile.objects.using('supabase').create(
                    user = r_user,
                    profile_name = l_prof.profile_name,
                    bio = l_prof.bio,
                    profile_image = l_prof.profile_image,
                    data_privacy_consent = l_prof.data_privacy_consent,
                )
                stats['pushed'] += 1
        elif l_prof and r_prof:
            if r_prof.updated_at > l_prof.updated_at:
                l_prof.profile_name = r_prof.profile_name
                l_prof.bio = r_prof.bio
                l_prof.profile_image = r_prof.profile_image
                l_prof.data_privacy_consent = r_prof.data_privacy_consent
                l_prof.save(using='default')
                stats['pulled'] += 1
            elif l_prof.updated_at > r_prof.updated_at:
                r_prof.profile_name = l_prof.profile_name
                r_prof.bio = l_prof.bio
                r_prof.profile_image = l_prof.profile_image
                r_prof.data_privacy_consent = l_prof.data_privacy_consent
                r_prof.save(using='supabase')
                stats['pushed'] += 1

    # Sync Settings
    remote_settings = {s.user.username: s for s in UserSettings.objects.using('supabase').select_related('user').all()}
    local_settings = {s.user.username: s for s in UserSettings.objects.using('default').select_related('user').all()}
    all_settings = set(remote_settings.keys()).union(set(local_settings.keys()))

    for username in all_settings:
        r_sett = remote_settings.get(username)
        l_sett = local_settings.get(username)
        r_user = remote_users.get(username)
        l_user = local_users.get(username)

        if r_sett and not l_sett:
            if l_user:
                UserSettings.objects.create(
                    user = l_user,
                    dark_mode = r_sett.dark_mode,
                    email_notification = r_sett.email_notification,
                )
                stats['pulled'] += 1
        elif l_sett and not r_sett:
            if r_user:
                UserSettings.objects.create(
                    user = r_user,
                    dark_mode = l_sett.dark_mode,
                    email_notification = l_sett.email_notification,
                )
                stats['pushed'] += 1
        elif l_sett and r_sett:
            if l_sett.updated_at > r_sett.updated_at:
                r_sett.dark_mode = l_sett.dark_mode
                r_sett.email_notification = l_sett.email_notification
                r_sett.save(using='supabase')
                stats['pushed'] += 1
            elif r_sett.updated_at > l_sett.updated_at:
                l_sett.dark_mode = r_sett.dark_mode
                l_sett.email_notification = r_sett.email_notification
                l_sett.save(using='default')
                stats['pulled'] += 1

    return {
        'success': True,
        'stats': stats,
        'message': f"Synced successfully! Pushed {stats['pushed']} changes, pulled {stats['pulled']} changes."
    }

class Command(BaseCommand):
    help = 'Synchronize local SQLite database with cloud Supabase PostgreSQL'

    def handle(self, *args, **options):
        self.stdout.write("Starting database sync with Supabase")
        result = run_database_sync()
        if result['success']:
            self.stdout.write(self.style.SUCCESS(result['message']))
        else:
            self.stdout.write(self.style.ERROR(result['error']))