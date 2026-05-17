#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASKI Doluluk SVG Badge Generator
"""

import json
from pathlib import Path

DATA_FILE = Path("data/aski_doluluk.json")
BADGE_DIR = Path("badges")


def get_color(value: float) -> str:
    if value >= 50:
        return "#22c55e"
    elif value >= 30:
        return "#eab308"
    else:
        return "#ef4444"


def text_width(text: str, approx: float = 6.5) -> int:
    return int(len(text) * approx) + 24


def create_badge(label: str, value: str, color: str = "#555") -> str:
    lw = text_width(label)
    vw = text_width(value, 7.5)
    tw = lw + vw

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{tw}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{lw}" height="20" fill="#555"/>
    <rect x="{lw}" width="{vw}" height="20" fill="{color}"/>
    <rect width="{tw}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{lw/2}" y="14" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{lw/2}" y="13">{label}</text>
    <text x="{lw + vw/2}" y="14" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{lw + vw/2}" y="13">{value}</text>
  </g>
</svg>"""


def main():
    print("[INFO] Badge generator basladi")
    print("[INFO] DATA_FILE: {}".format(DATA_FILE.absolute()))
    print("[INFO] DATA_FILE exists: {}".format(DATA_FILE.exists()))

    if not DATA_FILE.exists():
        print("[HATA] data/aski_doluluk.json bulunamadi")
        return 1

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    veriler = data.get("veriler", [])
    print("[INFO] Kayit sayisi: {}".format(len(veriler)))

    if not veriler:
        print("[HATA] Veri listesi bos")
        return 1

    latest = veriler[-1]
    toplam = latest["toplam_doluluk"]
    aktif = latest["aktif_doluluk"]
    tarih = latest.get("tarih_aski", "Bilinmiyor")

    print("[INFO] Son veri: {} | Toplam: {}% | Aktif: {}%".format(tarih, toplam, aktif))

    BADGE_DIR.mkdir(parents=True, exist_ok=True)

    badges = {
        "toplam-doluluk.svg": create_badge("Toplam Doluluk", "{:.1f}%".format(toplam), get_color(toplam)),
        "aktif-doluluk.svg": create_badge("Aktif Doluluk", "{:.1f}%".format(aktif), get_color(aktif)),
        "tarih.svg": create_badge("Tarih", tarih, "#3b82f6"),
    }

    for filename, svg in badges.items():
        filepath = BADGE_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)
        print("[OK] Badge yazildi: {} ({} bytes)".format(filepath.absolute(), len(svg)))

    # README'yi yeniden yaz - 5 grafik
    readme_content = """# Ankara Baraj Doluluk Oranlari

![Toplam Doluluk](badges/toplam-doluluk.svg)
![Aktif Doluluk](badges/aktif-doluluk.svg)
![Tarih](badges/tarih.svg)

## Doluluk Trendleri

### Son 30 Gün
![Son 30 Gun](charts/doluluk-30g.svg)

### Son 90 Gün
![Son 90 Gun](charts/doluluk-90g.svg)

### Son 180 Gün
![Son 180 Gun](charts/doluluk-180g.svg)

### Son 360 Gün
![Son 360 Gun](charts/doluluk-360g.svg)

### Son 12 Ay (Aylık Ortalama)
![Son 12 Ay](charts/doluluk-12ay.svg)

> ASKI verileri ile otomatik guncellenir. Her 8 saatte bir yenilenir.

## Kaynak
- [aski.gov.tr - Baraj Doluluk Oranlari](https://www.aski.gov.tr/tr/baraj.aspx)

## Son Veri
```json
{}
```
""".format(json.dumps(latest, ensure_ascii=False, indent=2))

    readme_path = Path("README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("[OK] README.md yazildi: {}".format(readme_path.absolute()))

    return 0


if __name__ == "__main__":
    exit(main())

