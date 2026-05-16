#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASKI Doluluk Trend Grafiği - Pure SVG
Matplotlib kullanmadan, son N kayit icin SVG trend grafiği üretir.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/aski_doluluk.json")
CHART_DIR = Path("charts")
MAX_POINTS = 30


def main():
    print("[INFO] Chart generator basladi")
    print(f"[INFO] DATA_FILE: {DATA_FILE.absolute()}")
    print(f"[INFO] DATA_FILE exists: {DATA_FILE.exists()}")

    if not DATA_FILE.exists():
        print("[HATA] data/aski_doluluk.json bulunamadi")
        return 1

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    veriler = data.get("veriler", [])
    print(f"[INFO] Kayit sayisi: {len(veriler)}")

    if len(veriler) < 2:
        print("[UYARI] Grafik icin en az 2 kayit gerekli")
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        placeholder = '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300"><text x="300" y="150" text-anchor="middle" font-size="14" fill="#888">Yeterli veri yok (en az 2 kayit gerekli)</text></svg>'
        (CHART_DIR / "doluluk-trend.svg").write_text(placeholder, encoding="utf-8")
        print("[OK] Placeholder SVG yazildi")
        return 0

    kayitlar = veriler[-MAX_POINTS:]

    points = []
    for k in kayitlar:
        ts = k.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        toplam = k.get("toplam_doluluk")
        aktif = k.get("aktif_doluluk")
        if toplam is None or aktif is None:
            continue
        points.append((dt, float(toplam), float(aktif)))

    print(f"[INFO] Gecerli nokta sayisi: {len(points)}")

    if len(points) < 2:
        print("[HATA] Gecerli veri yok")
        return 1

    # SVG boyutlari
    width, height = 800, 400
    margin = {"top": 40, "right": 40, "bottom": 80, "left": 60}
    chart_w = width - margin["left"] - margin["right"]
    chart_h = height - margin["top"] - margin["bottom"]

    # Olcekleme
    min_t = points[0][0].timestamp()
    max_t = points[-1][0].timestamp()
    time_range = max_t - min_t if max_t != min_t else 1

    def sx(dt):
        return margin["left"] + ((dt.timestamp() - min_t) / time_range) * chart_w

    def sy(val):
        return margin["top"] + chart_h - (val / 100) * chart_h

    # Polyline noktalari
    toplam_pts = " ".join(f"{sx(dt):.1f},{sy(t):.1f}" for dt, t, a in points)
    aktif_pts = " ".join(f"{sx(dt):.1f},{sy(a):.1f}" for dt, t, a in points)

    # X ekseni etiketleri
    x_labels = []
    step = max(1, len(points) // 6)
    for i in range(0, len(points), step):
        dt, _, _ = points[i]
        label = dt.strftime("%d.%m %H:%M")
        x_labels.append(f'<text x="{sx(dt):.1f}" y="{height - 20}" text-anchor="middle" font-size="10" fill="#888">{label}</text>')

    # Y grid ve etiketler
    y_grid = []
    for val in range(0, 101, 20):
        y = sy(val)
        y_grid.append(f'<line x1="{margin["left"]}" y1="{y:.1f}" x2="{width - margin["right"]}" y2="{y:.1f}" stroke="#333" stroke-width="1" stroke-dasharray="4,4" opacity="0.5"/>')
        y_grid.append(f'<text x="{margin["left"] - 10}" y="{y:.1f}" text-anchor="end" dominant-baseline="middle" font-size="10" fill="#888">{val}%</text>')

    # Referans cizgileri
    ref_lines = []
    for val, color, label in [(30, "#ef4444", "Kritik"), (50, "#eab308", "Normal")]:
        y = sy(val)
        ref_lines.append(f'<line x1="{margin["left"]}" y1="{y:.1f}" x2="{width - margin["right"]}" y2="{y:.1f}" stroke="{color}" stroke-width="1" stroke-dasharray="2,2" opacity="0.7"/>')
        ref_lines.append(f'<text x="{width - margin["right"] + 5}" y="{y:.1f}" dominant-baseline="middle" font-size="9" fill="{color}">{label} ({val}%)</text>')

    # Noktalar (circle)
    toplam_circles = "".join(f'<circle cx="{sx(dt):.1f}" cy="{sy(t):.1f}" r="3" fill="#22c55e"/>' for dt, t, a in points)
    aktif_circles = "".join(f'<circle cx="{sx(dt):.1f}" cy="{sy(a):.1f}" r="3" fill="#3b82f6"/>' for dt, t, a in points)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" style="max-width:{width}px;">
  <rect width="{width}" height="{height}" fill="#0d1117" rx="6"/>
  <text x="{width/2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#c9d1d9">Ankara Baraj Doluluk Trendi</text>

  <!-- Y grid -->
  {"
  ".join(y_grid)}

  <!-- Referans cizgileri -->
  {"
  ".join(ref_lines)}

  <!-- Toplam doluluk -->
  <polyline points="{toplam_pts}" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <polyline points="{toplam_pts}" fill="none" stroke="#22c55e" stroke-width="5" opacity="0.1" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Aktif doluluk -->
  <polyline points="{aktif_pts}" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <polyline points="{aktif_pts}" fill="none" stroke="#3b82f6" stroke-width="5" opacity="0.1" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Noktalar -->
  {toplam_circles}
  {aktif_circles}

  <!-- X ekseni -->
  {"
  ".join(x_labels)}

  <!-- Legend -->
  <g transform="translate({margin["left"]}, {height - 55})">
    <rect x="0" y="0" width="12" height="12" fill="#22c55e" rx="2"/>
    <text x="18" y="10" font-size="11" fill="#c9d1d9">Toplam Doluluk</text>
    <rect x="140" y="0" width="12" height="12" fill="#3b82f6" rx="2"/>
    <text x="158" y="10" font-size="11" fill="#c9d1d9">Aktif Doluluk</text>
  </g>
</svg>'''

    CHART_DIR.mkdir(parents=True, exist_ok=True)
    chart_path = CHART_DIR / "doluluk-trend.svg"
    with open(chart_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[OK] Chart yazildi: {chart_path.absolute()}")
    return 0


if __name__ == "__main__":
    exit(main())
