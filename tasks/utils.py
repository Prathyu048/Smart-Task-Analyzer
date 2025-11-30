def validate_tasks(tasks):
    """
    Returns (cleaned_tasks, warnings)
    - Ensures each task has id/title, sanitizes numeric fields, normalizes dependencies to list.
    """
    warnings = []
    clean = []
    for idx, t in enumerate(tasks):
        t = dict(t)  # shallow copy to avoid mutating original
        if "id" not in t or not str(t.get("id")).strip():
            t["id"] = f"__t{idx}"
            warnings.append(f"Task at index {idx} missing id; assigned {t['id']}")
        if "title" not in t or not str(t.get("title")).strip():
            warnings.append(f"Task {t['id']} missing title; set to 'Untitled'")
            t["title"] = t.get("title") or "Untitled"
        # importance -> int 1..10
        try:
            t["importance"] = int(t.get("importance", 5))
        except Exception:
            t["importance"] = 5
            warnings.append(f"Task {t['id']} importance invalid, defaulting to 5")
        # estimated_hours -> float or None
        try:
            eh = t.get("estimated_hours", None)
            t["estimated_hours"] = float(eh) if (eh is not None and str(eh).strip() != "") else None
        except Exception:
            t["estimated_hours"] = None
            warnings.append(f"Task {t['id']} estimated_hours invalid, set to None")
        # dependencies -> list
        deps = t.get("dependencies") or []
        if not isinstance(deps, list):
            warnings.append(f"Task {t['id']} dependencies not list; ignoring")
            deps = []
        t["dependencies"] = deps
        clean.append(t)
    return clean, warnings

def detect_cycles(tasks):
    """
    Detect directed cycles in dependencies.
    Each task's 'dependencies' are the tasks it depends on (prereqs).
    Return list of cycles (each cycle is list of node ids).
    """
    g = {t["id"]: t.get("dependencies") or [] for t in tasks}
    visited = {}
    cycles = []
    path = []

    def dfs(u):
        visited[u] = 1  # visiting
        path.append(u)
        for v in g.get(u, []):
            if v not in g:
                continue  # dependency points to missing task -> ignore here (warning handled elsewhere)
            if visited.get(v, 0) == 0:
                dfs(v)
            elif visited.get(v, 0) == 1:
                # found a cycle: path from v to end
                try:
                    i = path.index(v)
                    cycles.append(path[i:].copy())
                except ValueError:
                    cycles.append([v, u])
        path.pop()
        visited[u] = 2

    for node in g:
        if visited.get(node, 0) == 0:
            dfs(node)

    # dedupe cycles by sorted tuple
    unique = []
    seen = set()
    for c in cycles:
        key = tuple(sorted(c))
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique
