import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from datetime import date

from .scoring import score_task
from .utils import validate_tasks, detect_cycles

# Predefined weight sets for strategies
STRATEGY_WEIGHTS = {
    "smart": {"u": 0.35, "i": 0.30, "e": 0.20, "d": 0.15},
    "fastest": {"u": 0.20, "i": 0.10, "e": 0.60, "d": 0.10},
    "impact": {"u": 0.20, "i": 0.70, "e": 0.05, "d": 0.05},
    "deadline": {"u": 0.70, "i": 0.20, "e": 0.05, "d": 0.05},
}

def _explain_score(task, breakdown, score):
    parts = []
    if breakdown.get("urgency", 0) > 0.8:
        parts.append("Urgent")
    if breakdown.get("importance", 0) > 0.6:
        parts.append("High importance")
    if breakdown.get("effort", 0) > 0.7:
        parts.append("Quick win")
    if breakdown.get("dependency", 0) > 0:
        parts.append("Blocks other tasks")
    if not parts:
        parts.append("Balanced factors")
    return f"{', '.join(parts)} — score {round(score,3)}"

@csrf_exempt
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    Body JSON: { "strategy": "smart", "tasks": [ ... ] }
    Returns: { tasks: [...], warnings: [...], cycles: [...], strategy: "smart" }
    """
    if request.method != "POST":
        return HttpResponseBadRequest(json.dumps({"error": "POST required"}), content_type="application/json")
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest(json.dumps({"error": "Invalid JSON"}), content_type="application/json")

    tasks = payload.get("tasks") or []
    strategy = payload.get("strategy", "smart")
    weights = STRATEGY_WEIGHTS.get(strategy, STRATEGY_WEIGHTS["smart"])

    tasks, warnings = validate_tasks(tasks)
    cycles = detect_cycles(tasks)
    tasks_by_id = {t["id"]: t for t in tasks}
    today = date.today()
    results = []

    for t in tasks:
        score, breakdown = score_task(t, tasks_by_id, weights=weights, today=today)
        prio = "Low"
        if score >= 0.75:
            prio = "High"
        elif score >= 0.5:
            prio = "Medium"
        results.append({
            "id": t["id"],
            "title": t["title"],
            "due_date": t.get("due_date"),
            "estimated_hours": t.get("estimated_hours"),
            "importance": t.get("importance"),
            "dependencies": t.get("dependencies"),
            "score": round(score, 3),
            "priority": prio,
            "breakdown": breakdown,
            "explanation": _explain_score(t, breakdown, score),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    resp = {"tasks": results, "warnings": warnings, "cycles": cycles, "strategy": strategy}
    return JsonResponse(resp)

def _tasks_from_query_param(request):
    """
    Extracts tasks from `tasks` query param as JSON string.
    Returns (tasks, warnings)
    """
    q = request.GET.get("tasks")
    if not q:
        return None, ["No tasks provided in query param 'tasks'"]
    try:
        tasks = json.loads(q)
        if not isinstance(tasks, list):
            return None, ["tasks must be a JSON array"]
        return tasks, []
    except Exception:
        return None, ["Invalid JSON in tasks parameter"]

def suggest_tasks(request):
    """
    GET /api/tasks/suggest/?tasks=[urlencoded-json-array]&strategy=smart
    Returns top 3 suggestions with explanations.
    """
    if request.method != "GET":
        return HttpResponseBadRequest(json.dumps({"error": "GET required"}), content_type="application/json")
    tasks, warnings = _tasks_from_query_param(request)
    if tasks is None:
        return JsonResponse({"suggestions": [], "warnings": warnings})
    strategy = request.GET.get("strategy", "smart")
    weights = STRATEGY_WEIGHTS.get(strategy, STRATEGY_WEIGHTS["smart"])
    tasks, vwarnings = validate_tasks(tasks)
    warnings += vwarnings
    cycles = detect_cycles(tasks)
    tasks_by_id = {t["id"]: t for t in tasks}
    today = date.today()
    scored = []
    for t in tasks:
        score, breakdown = score_task(t, tasks_by_id, weights=weights, today=today)
        scored.append({
            "id": t["id"],
            "title": t["title"],
            "score": round(score, 3),
            "explanation": _explain_score(t, breakdown, score),
            "priority": ("High" if score >= 0.75 else "Medium" if score >= 0.5 else "Low"),
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    top3 = scored[:3]
    return JsonResponse({"suggestions": top3, "warnings": warnings, "cycles": cycles, "strategy": strategy})
