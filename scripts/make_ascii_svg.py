#!/usr/bin/env python3
"""Converte source-prepped.png em avi-ascii.svg (ASCII monocromatico que se 'digita').

Uso:  python scripts/make_ascii_svg.py
"""
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "avi-ascii.svg"

# ---- ajustes ----
COLS = 100                 # caracteres por linha
RAMP = " .:-=+*#%@"        # claro (esparso) -> escuro (denso)
CHAR_W = 6.0               # largura de cada caractere (px do SVG)
CHAR_H = 11.0              # altura da linha
FILL = "#c9d1d9"           # cinza claro unico
BG = "#0d1117"
ROW_STAGGER = 0.07         # s entre linhas
ROW_DUR = 0.55             # s para cada linha ser digitada
PAD = 14


def to_rows() -> list[str]:
    if not SRC.exists():
        raise SystemExit("source-prepped.png nao existe. Rode prep_photo.py primeiro.")
    img = Image.open(SRC).convert("L")
    aspect = img.height / img.width
    rows = max(1, round(COLS * aspect * (CHAR_W / CHAR_H)))
    img = img.resize((COLS, rows), Image.LANCZOS)
    a = np.asarray(img, dtype=float) / 255.0          # 1 = branco
    idx = ((1.0 - a) * (len(RAMP) - 1)).round().astype(int)
    return ["".join(RAMP[i] for i in line) for line in idx]


def build(rows: list[str]) -> str:
    w = COLS * CHAR_W + 2 * PAD
    h = len(rows) * CHAR_H + 2 * PAD
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="Retrato em ASCII">',
        f'<rect width="{w:.0f}" height="{h:.0f}" rx="10" fill="{BG}"/>',
        "<defs>",
    ]
    for i in range(len(rows)):
        begin = i * ROW_STAGGER
        out.append(
            f'<clipPath id="c{i}"><rect x="{PAD}" y="{PAD + i * CHAR_H - 1:.1f}" width="0" '
            f'height="{CHAR_H + 2:.1f}"><animate attributeName="width" from="0" '
            f'to="{COLS * CHAR_W:.0f}" begin="{begin:.2f}s" dur="{ROW_DUR}s" '
            f'fill="freeze"/></rect></clipPath>'
        )
    out.append("</defs>")
    out.append(
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="{CHAR_H - 1:.1f}" fill="{FILL}" xml:space="preserve" '
        f'style="white-space:pre">'
    )
    for i, line in enumerate(rows):
        stripped = line.rstrip()
        if not stripped.strip():
            continue
        y = PAD + i * CHAR_H + CHAR_H - 2
        out.append(
            f'<text x="{PAD}" y="{y:.1f}" textLength="{len(stripped) * CHAR_W:.1f}" '
            f'lengthAdjust="spacing" clip-path="url(#c{i})" xml:space="preserve">'
            f"{escape(stripped)}</text>"
        )
    out.append("</g>")
    # cursor: pequeno bloco que acompanha a borda de cada linha
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        begin = i * ROW_STAGGER
        y = PAD + i * CHAR_H
        out.append(
            f'<rect x="{PAD}" y="{y:.1f}" width="{CHAR_W:.0f}" height="{CHAR_H - 2:.1f}" '
            f'fill="{FILL}" opacity="0"><set attributeName="opacity" to="0.9" '
            f'begin="{begin:.2f}s"/><animate attributeName="x" from="{PAD}" '
            f'to="{PAD + COLS * CHAR_W:.0f}" begin="{begin:.2f}s" dur="{ROW_DUR}s" '
            f'fill="freeze"/><set attributeName="opacity" to="0" '
            f'begin="{begin + ROW_DUR:.2f}s"/></rect>'
        )
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    rows = to_rows()
    OUT.write_text(build(rows), encoding="utf-8")
    print(f"OK -> {OUT} ({COLS}x{len(rows)} caracteres)")
