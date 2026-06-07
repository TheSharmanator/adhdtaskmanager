import json
import os
import sqlite3
import urllib.parse
from datetime import datetime, timedelta, timezone

import requests

_DB_PATH = os.path.join(os.path.dirname(__file__), 'tasks.db')
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

_SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks',
]
_AUTH_URI  = 'https://accounts.google.com/o/oauth2/v2/auth'
_TOKEN_URI = 'https://oauth2.googleapis.com/token'
_CAL_API   = 'https://www.googleapis.com/calendar/v3'
_TASKS_API = 'https://www.googleapis.com/tasks/v1'


# ─── DB helpers ──────────────────────────────────────────────────────────────

def _get_setting(key, default=None):
    try:
        conn = sqlite3.connect(_DB_PATH)
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
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value) if value is not None else ''))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"gcal_service._set_setting error: {e}")


def _get_client_credentials():
    """
    Returns (client_id, client_secret) for Calendar OAuth.
    Uses gcal_client_id/gcal_client_secret from settings DB if set,
    otherwise falls back to gdrive credentials from config.json.
    This allows the Calendar and GDrive to live in different Google accounts.
    """
    # Check DB first (Calendar-specific credentials take priority)
    db_id     = _get_setting('gcal_client_id', '')
    db_secret = _get_setting('gcal_client_secret', '')
    if db_id and db_secret:
        return db_id, db_secret

    # Fall back to gdrive credentials from config.json
    try:
        with open(_CONFIG_PATH) as f:
            cfg = json.load(f)
        return cfg.get('gdrive_client_id', ''), cfg.get('gdrive_client_secret', '')
    except Exception:
        return '', ''


# ─── OAuth ───────────────────────────────────────────────────────────────────

def get_auth_url(redirect_uri):
    client_id, _ = _get_client_credentials()
    params = {
        'client_id':     client_id,
        'redirect_uri':  redirect_uri,
        'response_type': 'code',
        'scope':         ' '.join(_SCOPES),
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
    _set_setting('gcal_access_token', data.get('access_token', ''))
    if data.get('refresh_token'):
        _set_setting('gcal_refresh_token', data['refresh_token'])
    expiry = (datetime.now(timezone.utc) + timedelta(seconds=data.get('expires_in', 3600))).isoformat()
    _set_setting('gcal_token_expiry', expiry)


def _refresh_access_token():
    client_id, client_secret = _get_client_credentials()
    refresh_token = _get_setting('gcal_refresh_token', '')
    if not refresh_token:
        raise Exception("No refresh token — re-authorize Google Calendar in settings.")
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
    access_token = _get_setting('gcal_access_token', '')
    if not access_token:
        raise Exception("Google Calendar not authorized.")
    expiry_str = _get_setting('gcal_token_expiry', '')
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
    return bool(_get_setting('gcal_refresh_token', ''))


def disconnect():
    for key in ('gcal_access_token', 'gcal_refresh_token', 'gcal_token_expiry', 'gcal_tasklist_id'):
        _set_setting(key, '')


# ─── Calendar reading ─────────────────────────────────────────────────────────

def fetch_busy_slots(days_ahead=21):
    """
    Read primary calendar and return busy slots as:
    {date_str: [(start_dt_naive_local, end_dt_naive_local), ...]}
    """
    token = get_access_token()
    now = datetime.now(timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=days_ahead)).isoformat()

    events = []
    page_token = None
    while True:
        params = {
            'timeMin':      time_min,
            'timeMax':      time_max,
            'singleEvents': 'true',
            'orderBy':      'startTime',
            'maxResults':   250,
        }
        if page_token:
            params['pageToken'] = page_token
        r = requests.get(
            f'{_CAL_API}/calendars/primary/events',
            headers={'Authorization': f'Bearer {token}'},
            params=params,
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        events.extend(data.get('items', []))
        page_token = data.get('nextPageToken')
        if not page_token:
            break

    busy = {}
    for ev in events:
        start_raw = ev.get('start', {})
        end_raw   = ev.get('end', {})
        if 'dateTime' not in start_raw:
            continue  # skip all-day events
        try:
            start_dt = datetime.fromisoformat(start_raw['dateTime'].replace('Z', '+00:00'))
            end_dt   = datetime.fromisoformat(end_raw['dateTime'].replace('Z', '+00:00'))
        except Exception:
            continue
        # Convert to local naive datetime
        start_local = start_dt.astimezone().replace(tzinfo=None)
        end_local   = end_dt.astimezone().replace(tzinfo=None)
        date_str = start_local.strftime('%Y-%m-%d')
        busy.setdefault(date_str, []).append((start_local, end_local))

    return busy


# ─── Google Tasks ─────────────────────────────────────────────────────────────

def get_or_create_tasklist():
    """Return the ID of the 'ADHD Tasks' tasklist, creating it if needed."""
    tasklist_id = _get_setting('gcal_tasklist_id', '')
    if tasklist_id:
        return tasklist_id

    token = get_access_token()
    r = requests.get(f'{_TASKS_API}/users/@me/lists',
                     headers={'Authorization': f'Bearer {token}'}, timeout=10)
    r.raise_for_status()
    for tl in r.json().get('items', []):
        if tl.get('title') == 'ADHD Tasks':
            _set_setting('gcal_tasklist_id', tl['id'])
            return tl['id']

    r = requests.post(
        f'{_TASKS_API}/users/@me/lists',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'title': 'ADHD Tasks'},
        timeout=10,
    )
    r.raise_for_status()
    tl_id = r.json()['id']
    _set_setting('gcal_tasklist_id', tl_id)
    return tl_id


def create_task(title, due_date_str):
    """Create a task. Returns the new task ID."""
    token = get_access_token()
    tl_id = get_or_create_tasklist()
    r = requests.post(
        f'{_TASKS_API}/lists/{tl_id}/tasks',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'title': title, 'due': due_date_str + 'T00:00:00.000Z'},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()['id']


def update_task(task_id, title, due_date_str=None):
    """Update title and optionally due date of an existing task."""
    token = get_access_token()
    tl_id = get_or_create_tasklist()
    body = {'title': title}
    if due_date_str:
        body['due'] = due_date_str + 'T00:00:00.000Z'
    r = requests.patch(
        f'{_TASKS_API}/lists/{tl_id}/tasks/{task_id}',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json=body,
        timeout=10,
    )
    r.raise_for_status()


def complete_task(task_id):
    """Mark a Google Task as completed."""
    token = get_access_token()
    tl_id = get_or_create_tasklist()
    r = requests.patch(
        f'{_TASKS_API}/lists/{tl_id}/tasks/{task_id}',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        json={'status': 'completed'},
        timeout=10,
    )
    r.raise_for_status()


def delete_task(task_id):
    """Delete a Google Task."""
    token = get_access_token()
    tl_id = get_or_create_tasklist()
    r = requests.delete(
        f'{_TASKS_API}/lists/{tl_id}/tasks/{task_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10,
    )
    r.raise_for_status()
