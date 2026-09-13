#!/usr/bin/env python3
"""Собирает data.json из Google Таблицы-пульта и waiting.json.

Запускается роботом GitHub раз в час. Руками ничего делать не нужно:
меняете этап в таблице — через час страница показывает новый.
"""
import csv, io, json, sys, urllib.request
from datetime import datetime, timezone, timedelta

SHEET_ID = "1tSxRTUUWCPW2qZdsper7CMhWqZ9-u5NEjix18QOcSIM"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# как подписи в таблице превращаются в этапы страницы
KEYS = {
    "сценарий готов": "plan",
    "снято": "shot",
    "монтаж": "edit",
    "ждём вашего слова": "review",
    "ждем вашего слова": "review",
    "принято": "accepted",
    "опубликовано": "published",
}

def main():
    meta = json.load(open("waiting.json", encoding="utf-8"))

    with urllib.request.urlopen(CSV_URL, timeout=60) as r:
        text = r.read().decode("utf-8")

    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        sys.exit("Таблица пустая — data.json не трогаем")

    items, unknown = [], set()
    for r in rows:
        num = (r.get("Номер") or "").strip()
        if not num:
            continue
        label = (r.get("Этап") or "").strip().lower()
        key = KEYS.get(label)
        if not key:
            unknown.add(r.get("Этап"))
            key = "plan"
        items.append({
            "n": int(float(num)),
            "title": (r.get("Название") or "").strip(),
            "hook": (r.get("О чём коротко") or "").strip(),
            "plan": (r.get("Выход по плану") or "").strip(),
            "who": (r.get("Кто в кадре") or "").strip(),
            "len": (r.get("Хронометраж") or "").strip(),
            "stage": key,
            "note": (r.get("Заметка") or "").strip(),
        })

    if unknown:
        print("Непонятные этапы в таблице (поставлен «Сценарий готов»):", ", ".join(map(str, unknown)))

    msk = timezone(timedelta(hours=3))
    out = {
        "updated": datetime.now(msk).strftime("%Y-%m-%d"),
        "project": meta["project"],
        "month": meta["month"],
        "stages": meta["stages"],
        "waiting": meta["waiting"],
        "items": sorted(items, key=lambda i: i["n"]),
    }
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Записано {len(items)} роликов")

if __name__ == "__main__":
    main()
