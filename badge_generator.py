#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASKI Doluluk SVG Badge Generator
---------------------------------
README'de gostermek icin toplam/aktif doluluk degerlerini
ve tarih badge'ini SVG olarak olusturur.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/aski_doluluk.json")
BADGE_DIR = Path("badges")


def get_color(value: float) -> str:
    """Deger araligina gore renk dondurur."""
    if value >= 50:
        return "#22c55e"  # yesil
    elif value >= 30:
        return "#eab308"  # sari
    else:
        return "#ef4444"  # kirmizi


def estimate_text_width(text: str, char_width: float = 6.5) -> int:
    """Metin genisligini daha dogru hesapla."""
    return int(len(text) * char_width) + 20


def create_badge(label: str, value: str, color: str = "#555") -> str:
    """SVG badge string olusturur."""
    label_width = estimate_text_width(label)
    value_width = estimate_text_width(value, char_width=7.5)
    total_width = label_width + value_width

    svg = f"""<<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20" role="img" aria-label="{label}: {value}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11">
    <text x="{label_width/2}" y="14" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width/2}" y="13">{label}</text>
    <text x="{label_width + value_width/2}" y="14" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{label_width + value_width/2}" y="13">{value}</text>
  </g>
</svg>"""
    return svg


def main():
    if not DATA_FILE.exists():
        print("[HATA] Veri dosyasi bulunamadi")
        return 1

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data.get("veriler"):
        print("[HATA] Veri yok")
        return 1

    latest = data["veriler"][-1]
    toplam = latest["toplam_doluluk"]
    aktif = latest["aktif_doluluk"]
    tarih = latest.get("tarih_aski", "Bilinmiyor")

    BADGE_DIR.mkdir(parents=True, exist_ok=True)

    # Badge'leri olustur
    badges = {
        "toplam-doluluk.svg": create_badge("Toplam Doluluk", f"{toplam:.1f}%", get_color(toplam)),
        "aktif-doluluk.svg": create_badge("Aktif Doluluk", f"{aktif:.1f}%", get_color(aktif)),
        "tarih.svg": create_badge("Tarih", tarih, "#3b82f6"),
    }

    for filename, svg in badges.items():
        filepath = BADGE_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"[OK] {filepath}")

    # README badge satirlarini guncelle
    readme_lines = [
        "# Ankara Baraj Doluluk Oranlari",
        "",
        f"![Toplam Doluluk](badges/toplam-doluluk.svg)",
        f"![Aktif Doluluk](badges/aktif-doluluk.svg)",
        f"![Tarih](badges/tarih.svg)",
        "",
        "## Doluluk Trendi",
        "",
        "![Doluluk Grafiği](charts/doluluk-trend.svg)",
        "",
        "> ASKI verileri ile otomatik guncellenir. Her 8 saatte bir yenilenir.",
        "",
        "## Kaynak",
        "- [aski.gov.tr - Baraj Doluluk Oranlari](https://www.aski.gov.tr/tr/baraj.aspx)",
        "",
        "## Son Veri",
        "```json",
        json.dumps(latest, ensure_ascii=False, indent=2),
        "```",
    ]

    with open("README.md", "w", encoding="utf-8") as f:
        f.write("\n".join(readme_lines))

    print("[OK] README.md guncellendi")
    return 0


if __name__ == "__main__":
    exit(main())
