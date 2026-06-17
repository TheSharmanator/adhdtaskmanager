from datetime import datetime, timedelta, date, time as dt_time

GAP_MINS = 10  # rest buffer between consecutive scheduled tasks


def schedule_tasks(tasks, busy_slots_by_date, now=None):
    """
    Assign each active task to the earliest available time slot.

    tasks: list of dicts — id, title, duration_minutes, deadline (YYYY-MM-DDTHH:MM),
                           deadline_type, scheduled_start (existing, may be None)
    busy_slots_by_date: {date_str: [(start_dt_naive, end_dt_naive), ...]}

    Available slots are the gaps between calendar events across the full day (00:00–23:59).
    The Google Calendar defines all busy time — no separate work-hour window.

    Returns: list of dicts — task_id, scheduled_start (ISO str or None),
                              scheduled_end (ISO str or None), status
             status: 'scheduled' | 'unschedulable' | 'skipped'
    """
    if now is None:
        now = datetime.now()
    today = now.date()
    results = []
    allocated = {}  # date_str -> [(start_dt, end_dt)] — slots taken in this run

    # Tightest deadline first — this ensures high-priority tasks get earlier slots
    def _sort_key(t):
        dl = t.get('deadline') or ''
        if not dl or '2099' in dl:
            return '2099-12-31'
        return dl[:10]

    for task in sorted(tasks, key=_sort_key):
        deadline_str  = task.get('deadline') or ''
        duration_mins = int(task.get('duration_minutes') or 30)
        dl_type       = task.get('deadline_type') or 'none'

        # Skip backlog / no-deadline tasks
        if dl_type == 'none' or not deadline_str or '2099' in deadline_str:
            results.append(_result(task['id'], None, None, 'skipped'))
            continue

        try:
            deadline_date = datetime.strptime(deadline_str[:10], '%Y-%m-%d').date()
        except ValueError:
            results.append(_result(task['id'], None, None, 'skipped'))
            continue

        if task.get('pin_to_date'):
            slot = _find_slot(deadline_date, deadline_date, duration_mins, busy_slots_by_date, allocated, now)
        else:
            slot = _find_slot(today, deadline_date, duration_mins, busy_slots_by_date, allocated, now)

        if slot:
            start_dt, end_dt = slot
            date_str = start_dt.strftime('%Y-%m-%d')
            allocated.setdefault(date_str, []).append(slot)
            results.append(_result(
                task['id'],
                start_dt.strftime('%Y-%m-%dT%H:%M'),
                end_dt.strftime('%Y-%m-%dT%H:%M'),
                'scheduled',
            ))
        else:
            results.append(_result(task['id'], None, None, 'unschedulable'))

    return results


def _result(task_id, start, end, status):
    return {'task_id': task_id, 'scheduled_start': start, 'scheduled_end': end, 'status': status}


def _find_slot(from_date, deadline_date, duration_mins, busy_by_date, allocated, now=None):
    if now is None:
        now = datetime.now()
    check = from_date
    while check <= deadline_date:
        # Never schedule a slot that starts in the past
        day_start = max(datetime.combine(check, dt_time(0, 0)), now)
        day_end   = datetime.combine(check, dt_time(23, 59))
        date_str  = check.strftime('%Y-%m-%d')

        busy = sorted(
            list(busy_by_date.get(date_str, [])) +
            [(s, e + timedelta(minutes=GAP_MINS)) for s, e in allocated.get(date_str, [])],
            key=lambda x: x[0],
        )

        slot = _first_gap(day_start, day_end, duration_mins, busy)
        if slot:
            return slot

        check += timedelta(days=1)

    return None


def _first_gap(day_start, day_end, duration_mins, busy_sorted):
    """Return (start, end) of the first gap that fits duration_mins, or None."""
    cursor = day_start
    for bstart, bend in busy_sorted:
        if bend <= cursor:
            continue
        if bstart > cursor:
            gap = (min(bstart, day_end) - cursor).total_seconds() / 60
            if gap >= duration_mins:
                return cursor, cursor + timedelta(minutes=duration_mins)
        cursor = max(cursor, bend)

    # Remaining time after last block
    if (day_end - cursor).total_seconds() / 60 >= duration_mins:
        return cursor, cursor + timedelta(minutes=duration_mins)

    return None
