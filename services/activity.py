from storage import read_json, write_json
from datetime import datetime, timedelta

ACT = "data/user_activity.json"

def _now(): return datetime.utcnow()
def _today_key(dt): return dt.strftime("%Y-%m-%d")

def _store():
    data = read_json(ACT) or {"activity": []}
    if "activity" not in data: data["activity"] = []
    return data

def track_activity(username, action):
    """Record an action and maintain a simple daily streak counter."""
    data = _store()
    today = _today_key(_now())
    entry = next((a for a in data["activity"] if a.get("username")==username), None)
    if not entry:
        entry = {"username": username, "last_day": None, "streak": 0, "log": []}
        data["activity"].append(entry)

    # append log
    entry["log"].append({"at": _now().isoformat()+"Z", "action": action})

    # streak logic
    last = entry.get("last_day")
    if last == today:
        pass  # already counted today
    else:
        if last:
            prev = datetime.fromisoformat(last)
            if _today_key(prev + timedelta(days=1)) == today:
                entry["streak"] = int(entry.get("streak", 0)) + 1
            else:
                entry["streak"] = 1
        else:
            entry["streak"] = 1
        entry["last_day"] = today

    write_json(ACT, data)
    return entry["streak"]
