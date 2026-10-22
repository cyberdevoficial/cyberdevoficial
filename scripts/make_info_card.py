#!/usr/bin/env python3
"""Gera info-card.svg (estilo neofetch)."""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"

# ================= CONFIG =================
USER_HOST = "cyberdevoficial"
LINES = [
    ("Now", "Estudante de ADS na Uniamérica"),
    ("Prev", "Construindo minha base em Backend"),
    ("Stack", "Java, Python, JavaScript"),
    ("Tools", "Git, GitHub, Linux, Termux"),
    ("Highlights", "Projetos próprios em desenvolvimento"),
    ("Contact", "cyberdevoficial"),
]
# ==========================================

W, H = 490, 330
STATIC = os.environ.get("STATIC") == "1"
COLORS = ["#7ee787", "#79c0ff", "#d2a8ff", "#ffa657", "#ff7b72", "#a5d6ff"]

def build() -> str:
    anim = "" if STATIC else (
        "@keyframes in{from{opacity:0;transform:translateX(-8px)}"
        "to{opacity:1;transform:none}}"
        ".l{opacity:0;animation:in .5s ease-out forwards}"
    )
    css = f"text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px}}{anim}"
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f"<style>{css}</style>",
        f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>',
        f'<rect width="{W}" height="30" rx="10" fill="#161b22"/>',
        f'<rect y="20" width="{W}" height="10" fill="#161b22"/>',
        '<circle cx="18" cy="15" r="5" fill="#ff5f56"/>',
        '<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>',
        '<circle cx="54" cy="15" r="5" fill="#27c93f"/>',
        '<text x="245" y="19" fill="#8b949e" text-anchor="middle">cyberdevoficial@github</text>',
    ]
    delay = 0.2
    y = 62

    def row(inner: str, y: int, d: float) -> str:
        style = "" if STATIC else f' style="animation-delay:{d:.2f}s"'
        return f'<g class="l"{style}>{inner}</g>'

    o.append(row(f'<text x="24" y="{y}" fill="#7ee787" font-weight="bold">{escape(USER_HOST)}@github</text>', y, delay))
    y += 20
    o.append(row(f'<text x="24" y="{y}" fill="#30363d">{"─" * 36}</text>', y, delay))
    y += 28

    for n, (k, v) in enumerate(LINES):
        d = delay + 0.3 + n * 0.15
        c = COLORS[n % len(COLORS)]
        inner = (
            f'<text x="24" y="{y}" fill="{c}" font-weight="bold">{escape(k)}:</text>'
            f'<text x="118" y="{y}" fill="#8b949e">➜</text>'
            f'<text x="132" y="{y}" fill="#c9d1d9">{escape(v)}</text>'
        )
        o.append(row(inner, y, d))
        y += 30

    d = delay + 0.3 + len(LINES) * 0.18
    blocks = "".join(
        f'<rect x="{24 + i * 26}" y="{H - 34}" width="22" height="12" rx="2" fill="{c}"/>'
        for i, c in enumerate(COLORS)
    )
    o.append(row(blocks, H - 34, d))
    o.append("</svg>")
    return "\n".join(o)

if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print(f"OK -> {OUT}")
