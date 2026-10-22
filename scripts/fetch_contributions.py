#!/usr/bin/env python3
"""Baixa o calendario publico de contribuicoes (sem token) e grava data/contributions.json.

Usuario: 1o argumento, ou env GITHUB_USERNAME, ou (no GitHub Actions) o dono do repo.
Uso:  python scripts/fetch_contributions.py SEU_USUARIO
"""
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def get_username() -> str:
    u = (sys.argv[1] if len(sys.argv) > 1 else
         os.environ.get("GITHUB_USERNAME") or os.environ.get("GITHUB_REPOSITORY_OWNER"))
    if not u:
        sys.exit("Informe o usuario: python scripts/fetch_contributions.py SEU_USUARIO")
    return u


def parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tips = {}
    for t in soup.find_all("tool-tip"):
        target = t.get("for")
        if target:
            tips[target] = t.get_text(" ", strip=True)

    days = []
    for td in soup.select("td.ContributionCalendar-day"):
        d = td.get("data-date")
        if not d:
            continue
        level = int(td.get("data-level", 0))
        text = tips.get(td.get("id", ""), "")
        m = re.match(r"\s*(\d[\d,]*)\s+contribution", text)
        if m:
            count = int(m.group(1).replace(",", ""))
        elif text.lower().startswith("no contribution"):
            count = 0
        else:
            count = level  # fallback aproximado se o tooltip nao existir
        days.append({"date": d, "count": count, "level": level})
    days.sort(key=lambda x: x["date"])
    return days


def stats(days: list[dict]) -> dict:
    counts = {date.fromisoformat(d["date"]): d["count"] for d in days}
    ordered = sorted(counts)
    longest = run = 0
    prev = None
    for d in ordered:
        if counts[d] > 0:
            run = run + 1 if prev and (d - prev).days == 1 else 1
            longest = max(longest, run)
            prev = d
        else:
            run, prev = 0, None
    # streak atual: se hoje ainda esta zerado, conta a partir de ontem
    cur = 0
    d = ordered[-1]
    if counts[d] == 0:
        d -= timedelta(days=1)
    while d in counts and counts[d] > 0:
        cur += 1
        d -= timedelta(days=1)
    best = max(days, key=lambda x: x["count"])
    monthly = defaultdict(int)
    for x in days:
        monthly[x["date"][:7]] += x["count"]
    return {
        "total": sum(x["count"] for x in days),
        "current_streak": cur,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": dict(sorted(monthly.items())),
    }


def main() -> None:
    user = get_username()
    url = f"https://github.com/users/{user}/contributions"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
    r.raise_for_status()
    days = parse(r.text)
    if not days:
        sys.exit(f"Nenhum dia encontrado para '{user}'. Confira o usuario / o HTML mudou.")
    data = {
        "username": user,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "days": days,
        "stats": stats(days),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    s = data["stats"]
    print(f"OK -> {OUT}: {len(days)} dias, {s['total']} contribuicoes, streak atual {s['current_streak']}")


if __name__ == "__main__":
    main()
