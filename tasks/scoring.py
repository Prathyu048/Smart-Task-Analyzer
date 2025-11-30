from datetime import datetime, date
from math import exp

# Tunable constants
MAX_EFFORT = 24.0  # hours used to normalize effort

def parse_date(s):
    if not s:
        return None
    try:
        # Accepts ISO format like '2025-11-30' or '2025-11-30T00:00:00'
        return datetime.fromisoformat(s).date()
    except Exception:
        return None

def normalize_importance(importance):
    try:
        imp = float(importance)
    except Exception:
        imp = 5.0
    imp = max(1.0, min(10.0, imp))
    return (imp - 1.0) / 9.0  # map 1..10 -> 0..1

def compute_urgency(due_date: date, today: date = None):
    if today is None:
        today = date.today()
    if due_date is None:
        return 0.1  # low urgency if no due date
    days_left = (due_date - today).days
    # Past-due: give a boost ( > 1 ), capped
    if days_left < 0:
        return min(1.5, 1.0 + min(abs(days_left) / 7.0, 0.5))
    # Smooth decay function: sooner -> closer to 1, far -> close to 0
    return 1.0 / (1.0 + exp((days_left - 3.0) / 2.5))

def compute_effort_score(estimated_hours):
    try:
        h = float(estimated_hours)
    except Exception:
        return 0.2  # assume moderate-high effort if unknown
    if h <= 0:
        return 1.0
    return max(0.0, 1.0 - min(h / MAX_EFFORT, 1.0))

def dependency_score(task_id, tasks_by_id):
    # Count how many other tasks list this task as a dependency (i.e., it blocks many tasks)
    blockers = 0
    for t in tasks_by_id.values():
        deps = t.get("dependencies") or []
        if task_id in deps:
            blockers += 1
    return min(1.0, blockers / 3.0)  # normalize with scale K=3

def score_task(task, tasks_by_id, weights=None, today=None):
    if weights is None:
        weights = {"u": 0.35, "i": 0.30, "e": 0.20, "d": 0.15}
    imp = normalize_importance(task.get("importance"))
    due = parse_date(task.get("due_date"))
    urg = compute_urgency(due, today=today)
    effort = compute_effort_score(task.get("estimated_hours"))
    dep = dependency_score(task.get("id"), tasks_by_id)
    raw = weights["u"] * urg + weights["i"] * imp + weights["e"] * effort + weights["d"] * dep
    # Because urgency can exceed 1 for past-due tasks (up to ~1.5), compute a normalization divisor
    max_possible = weights["u"] * 1.5 + weights["i"] * 1.0 + weights["e"] * 1.0 + weights["d"] * 1.0
    score = max(0.0, min(1.0, raw / max_possible))
    breakdown = {
        "urgency": round(urg, 3),
        "importance": round(imp, 3),
        "effort": round(effort, 3),
        "dependency": round(dep, 3),
    }
    return score, breakdown
