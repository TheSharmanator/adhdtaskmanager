import io
import json
import os
import sqlite3
import urllib.parse
import zipfile
from datetime import datetime, timedelta, timezone

import requests

_DB_PATH = os.path.join(os.path.dirname(__file__), 'tasks.db')
_APP_DIR = os.path.dirname(os.path.abspath(__file__))

_SCOPE = 'https://www.googleapis.com/auth/drive.file'
_AUTH_URI = 'https://accounts.google.com/o/oauth2/v2/auth'
_TOKEN_URI = 'https://oauth2.googleapis.com/token'
_DRIVE_API = 'https://www.googleapis.com/drive/v3'
_DRIVE_UPLOAD = 'https://www.googleapis.com/upload/drive/v3'
_FOLDER_NAME = 'adhdtaskmanager'
_KEEP_BACKUPS = 7

_EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}
_EXCLUDE_EXTS = ('.pyc', '.pyo', '-wal', '-shm')


# ─── DB helpers ──────────────────────────────────────────────────────────────

def _get_setting(key, default=None):
    try:
        conn = sqlite3.connect(_DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default
    except Exception:
        return default


def _set_setting(key, value):
    try:
        conn = sqlite3.connect(_DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                  (key, str(value) if value is not None else ''))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"gdrive_backup._set_setting error: {e}")


# ─── Credentials ─────────────────────────────────────────────────────────────

def _get_client_credentials():
    """Read gdrive_client_id / gdrive_client_secret from the settings DB."""
    return _get_setting('gdrive_client_id', ''), _get_setting('gdrive_client_secret', '')


# ─── OAuth ───────────────────────────────────────────────────────────────────

def get_auth_url(redirect_uri):
    client_id, _ = _get_client_credentials()
    params = {
        'client_id':     client_id,
        'redirect_uri':  redirect_uri,
        'response_type': 'code',
        'scope':         _SCOPE,
        'access_type':   'offline',
        'prompt':        'consent',
    }
    return _AUTH_URI + '?' + urllib.parse.urlencode(params)


def exchange_code(code, redirect_uri):
    client_id, client_secret = _get_client_credentials()
    r = requests.post(_TOKEN_URI, data={
        'code':          code,
        'client_id':     client_id,
        'client_secret': client_secret,
        'redirect_uri':  redirect_uri,
        'grant_type':    'authorization_code',
    }, timeout=15)
    r.raise_for_status()
    _store_tokens(r.json())


def _store_tokens(data):
    _set_setting('gdrive_backup_access_token', data.get('access_token', ''))
    if data.get('refresh_token'):
        _set_setting('gdrive_backup_refresh_token', data['refresh_token'])
    expiry = (datetime.now(timezone.utc) + timedelta(seconds=data.get('expires_in', 3600))).isoformat()
    _set_setting('gdrive_backup_token_expiry', expiry)


def _refresh_access_token():
    client_id, client_secret = _get_client_credentials()
    refresh_token = _get_setting('gdrive_backup_refresh_token', '')
    if not refresh_token:
        raise Exception("No refresh token — re-authorize Google Drive Backup in settings.")
    r = requests.post(_TOKEN_URI, data={
        'client_id':     client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type':    'refresh_token',
    }, timeout=15)
    r.raise_for_status()
    data = r.json()
    _store_tokens(data)
    return data['access_token']


def get_access_token():
    access_token = _get_setting('gdrive_backup_access_token', '')
    if not access_token:
        raise Exception("Google Drive Backup not authorized.")
    expiry_str = _get_setting('gdrive_backup_token_expiry', '')
    if expiry_str:
        try:
            expiry = datetime.fromisoformat(expiry_str)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            if (expiry - datetime.now(timezone.utc)).total_seconds() < 300:
                access_token = _refresh_access_token()
        except Exception:
            access_token = _refresh_access_token()
    return access_token


def is_authorized():
    return bool(_get_setting('gdrive_backup_refresh_token', ''))


def disconnect():
    for key in ('gdrive_backup_access_token', 'gdrive_backup_refresh_token', 'gdrive_backup_token_expiry'):
        _set_setting(key, '')


# ─── Drive operations ─────────────────────────────────────────────────────────

def _get_or_create_folder(token):
    """Find or create the adhdtaskmanager folder at Drive root. Returns folder ID."""
    headers = {'Authorization': f'Bearer {token}'}
    q = f"name='{_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    r = requests.get(
        f"{_DRIVE_API}/files",
        headers=headers,
        params={'q': q, 'fields': 'files(id,name)'},
        timeout=15,
    )
    r.raise_for_status()
    files = r.json().get('files', [])
    if files:
        return files[0]['id']

    r = requests.post(
        f"{_DRIVE_API}/files",
        headers={**headers, 'Content-Type': 'application/json'},
        json={'name': _FOLDER_NAME, 'mimeType': 'application/vnd.google-apps.folder'},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()['id']


def _build_zip():
    """Return a ZIP of the app directory as bytes, excluding dev/cache artifacts."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(_APP_DIR):
            dirs[:] = [d for d in dirs if d not in _EXCLUDE_DIRS]
            for fname in files:
                if any(fname.endswith(ext) for ext in _EXCLUDE_EXTS):
                    continue
                full_path = os.path.join(root, fname)
                arcname = os.path.relpath(full_path, _APP_DIR)
                try:
                    zf.write(full_path, arcname)
                except (PermissionError, OSError):
                    pass
    return buf.getvalue()


def _cleanup_old_backups(folder_id, token):
    """Delete oldest backups so at most _KEEP_BACKUPS remain."""
    headers = {'Authorization': f'Bearer {token}'}
    q = f"'{folder_id}' in parents and name contains 'adhdtaskmanager_' and trashed=false"
    r = requests.get(
        f"{_DRIVE_API}/files",
        headers=headers,
        params={'q': q, 'fields': 'files(id,name,createdTime)', 'orderBy': 'createdTime'},
        timeout=15,
    )
    r.raise_for_status()
    files = r.json().get('files', [])
    for f in files[:-_KEEP_BACKUPS]:
        try:
            requests.delete(f"{_DRIVE_API}/files/{f['id']}", headers=headers, timeout=10)
        except Exception:
            pass


def run_backup():
    """Build a ZIP of the app folder and upload it to My Drive/adhdtaskmanager/.
    Keeps the last 7 backups. Returns the uploaded filename."""
    token = get_access_token()
    folder_id = _get_or_create_folder(token)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    filename = f"adhdtaskmanager_{timestamp}.zip"
    zip_bytes = _build_zip()

    r = requests.post(
        f"{_DRIVE_UPLOAD}/files?uploadType=multipart",
        headers={'Authorization': f'Bearer {token}'},
        files={
            'metadata': ('metadata', json.dumps({'name': filename, 'parents': [folder_id]}),
                         'application/json; charset=UTF-8'),
            'file': (filename, zip_bytes, 'application/zip'),
        },
        timeout=120,
    )
    r.raise_for_status()

    _cleanup_old_backups(folder_id, token)
    _set_setting('gdrive_last_backup', datetime.now().strftime('%Y-%m-%d %H:%M'))
    return filename
