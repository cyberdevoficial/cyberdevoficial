#!/usr/bin/env python3
"""Le data/contributions.json e gera contrib-heatmap.svg (animado, 860px de largura)."""
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
W = 860
LEFT, RIGHT, TOP = 40, 24, 46
MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
DAYLABELS = {1: "Seg", 3: "Qua", 5: "Sex"}


def main() -> None:
    if not SRC.exists():
        sys.exit("data/contributions.json nao existe. Rode fetch_contributions.py primeiro.")
    data = json.loads(SRC.read_text(encoding="utf-8"))
    days, st = data["days"], data["stats"]
    if not days:
        sys.exit("JSON sem dias.")

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7          # domingo = linha 0
    ncols = (len(days) + offset + 6) // 7
    pitch = min(15.0, (W - LEFT - RIGHT) / ncols)
    cell = pitch - 3

    nonzero = sorted(d["count"] for d in days if d["count"] > 0)
    p90 = nonzero[int(len(nonzero) * 0.9)] if nonzero else 10**9

    grid_h = 7 * pitch - 3
    H = int(TOP + grid_h + 62)

    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Grafico de contribuicoes">',
        "<style>"
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#8b949e;font-size:11px}"
        "@keyframes in{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}"
        ".c{opacity:0;animation:in .45s ease-out forwards;transform-box:fill-box}"
        "</style>",
        f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>',
    ]

    last_month = None
    for i, d in enumerate(days):
        dt = date.fromisoformat(d["date"])
        col, row = (i + offset) // 7, (i + offset) % 7
        x, y = LEFT + col * pitch, TOP + row * pitch
        if row == 0 and dt.month != last_month and col < ncols - 1:
            o.append(f'<text x="{x:.1f}" y="{TOP - 10}">{MONTHS[dt.month - 1]}</text>')
        if row == 0:
            last_month = dt.month
        lvl = d["level"]
        if lvl >= 4 and d["count"] >= p90 and d["count"] > 0:
            lvl = 5
        delay = (col + row) * 0.018
        o.append(
            f'<rect class="c" x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
            f'rx="2.5" fill="{PALETTE[min(lvl, 5)]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{d["count"]} contribuicoes em {d["date"]}</title></rect>'
        )

    for r, label in DAYLABELS.items():
        o.append(f'<text x="8" y="{TOP + r * pitch + cell - 1:.1f}">{label}</text>')

    fy = TOP + grid_h + 34
    o.append(f'<text x="{LEFT}" y="{fy}">{st["total"]:,} contribuicoes no ultimo ano'.replace(",", ".") + "</text>")
    o.append(
        f'<text x="{LEFT}" y="{fy + 18}">streak atual: {st["current_streak"]}d  |  '
        f'maior streak: {st["longest_streak"]}d  |  melhor dia: {st["best_day"]["count"]}</text>'
    )
    # legenda Menos -> Mais
    lx = W - RIGHT - 6 * 15 - 70
    o.append(f'<text x="{lx}" y="{fy}">Menos</text>')
    for i, c in enumerate(PALETTE):
        o.append(f'<rect x="{lx + 38 + i * 15}" y="{fy - 10}" width="12" height="12" rx="2.5" fill="{c}"/>')
    o.append(f'<text x="{lx + 38 + 6 * 15 + 4}" y="{fy}">Mais</text>')
    o.append("</svg>")
    OUT.write_text("\n".join(o), encoding="utf-8")
    print(f"OK -> {OUT}")


if __name__ == "__main__":
    main()
