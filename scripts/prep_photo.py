#!/usr/bin/env python3
"""Prepara a foto para virar ASCII (versao leve: so Pillow + numpy, roda no Termux).

- Se a imagem for PNG com fundo transparente, o fundo vira branco puro.
- Aumenta o contraste e recorta no sujeito.
Saida: source-prepped.png (tons de cinza)

Uso:  python scripts/prep_photo.py foto-fonte.jpg
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps

OUT = Path(__file__).resolve().parent.parent / "source-prepped.png"


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: python scripts/prep_photo.py foto-fonte.jpg")
    src = Path(sys.argv[1])
    if not src.exists():
        sys.exit(f"Arquivo nao encontrado: {src}")

    img = Image.open(src)
    img = ImageOps.exif_transpose(img)          # corrige foto de celular girada
    rgba = img.convert("RGBA")
    rgba.thumbnail((1400, 1400))

    alpha = np.array(rgba)[:, :, 3]
    has_alpha = alpha.min() < 250
    if has_alpha:
        ys, xs = np.where(alpha > 40)
        if len(xs):
            pad = int(0.04 * max(rgba.size))
            rgba = rgba.crop((max(xs.min() - pad, 0), max(ys.min() - pad, 0),
                              min(xs.max() + pad, rgba.width), min(ys.max() + pad, rgba.height)))

    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(white, rgba).convert("L")

    flat = ImageOps.autocontrast(flat, cutoff=2)
    flat = ImageEnhance.Contrast(flat).enhance(1.35)

    if has_alpha:
        mask = np.array(rgba)[:, :, 3] > 40
        arr = np.array(flat)
        arr[~mask] = 255
        flat = Image.fromarray(arr)

    flat.save(OUT)
    print(f"OK -> {OUT}")


if __name__ == "__main__":
    main()
