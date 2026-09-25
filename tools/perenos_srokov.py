#!/usr/bin/env python3
"""Автоперенос сроков на странице заказчиков (правило Сандры 26.09).
Задача не готова за час до срока -> срок +3 часа. Счётчик переносов в поле perenos.
Задачи с publish (время выхода ролика) не трогаем. Ручная смена срока обнуляет счётчик."""
import json, sys
from datetime import datetime, timedelta, timezone
P = "tasks.json"
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
d = json.load(open(P, encoding="utf-8"))
changed = []

def gotovo(t):
    if "platforms" in t:
        st = t["platforms"].get("stages", []); lst = t["platforms"].get("list", [])
        return bool(lst) and all(p.get("done", 0) >= len(st) for p in lst)
    steps = t.get("steps", [])
    return bool(steps) and all(s.get("status") == "done" for s in steps)

for t in d.get("tasks", []):
    due = t.get("due")
    if not due or t.get("publish") or gotovo(t):
        continue
    dt = datetime.fromisoformat(due)
    pr = t.get("perenos") or {}
    if pr.get("posledniy") != due:          # срок поставили вручную -> счёт заново
        pr = {"n": 0}
    if dt - now > timedelta(hours=1):
        continue
    new = max(dt, now) + timedelta(hours=3)
    new = new.replace(second=0, microsecond=0)
    ns = new.isoformat(timespec="seconds")
    pr["n"] = pr.get("n", 0) + 1
    pr["posledniy"] = ns
    pr.setdefault("istoriya", []).append({"bylo": due, "stalo": ns, "kogda": now.isoformat(timespec="seconds")})
    pr["istoriya"] = pr["istoriya"][-6:]
    t["due"] = ns
    t["perenos"] = pr
    changed.append(f'{t["title"]}: {due} -> {ns} (перенос {pr["n"]})')

if changed:
    d["updated"] = now.isoformat(timespec="seconds")
    s = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
    json.loads(s)
    open(P, "w", encoding="utf-8").write(s)
print("\n".join(changed) or "без изменений")
