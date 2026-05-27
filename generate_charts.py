#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASKI Doluluk Trend Grafiği - Pure SVG
5 grafik üretir:
  1. doluluk-30g.svg   -> Son 30 gün (günlük ortalama)
  2. doluluk-90g.svg   -> Son 90 gün (günlük ortalama)
  3. doluluk-180g.svg  -> Son 180 gün (günlük ortalama)
  4. doluluk-360g.svg  -> Son 360 gün (günlük ortalama)
  5. doluluk-12ay.svg  -> Son 12 ay (aylık ortalama)
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

DATA_FILE = Path("data/aski_doluluk.json")
CHART_DIR = Path("charts")


def create_svg(points, title, width=800, height=400, show_ref=True, date_fmt=None):
    """Verilen (tarih, toplam, aktif) noktalarından SVG oluşturur.
    Tek nokta bile olsa genişletilmiş görünüm sağlar."""

    margin_top, margin_right, margin_bottom, margin_left = 40, 40, 80, 60
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom

    # Tek nokta varsa sahte ikinci nokta ekle (genişletilmiş görünüm için)
    if len(points) == 1:
        dt, t, a = points[0]
        # Sahte nokta: +30 gün, aynı değerler
        fake_dt = dt + timedelta(days=30)
        points = [points[0], (fake_dt, t, a)]

    min_t = points[0][0].timestamp()
    max_t = points[-1][0].timestamp()
    time_range = max(1, max_t - min_t)

    def sx(dt):
        return margin_left + ((dt.timestamp() - min_t) / time_range) * chart_w

    def sy(val):
        return margin_top + chart_h - (val / 100) * chart_h

    toplam_pts = " ".join("{:.1f},{:.1f}".format(sx(dt), sy(t)) for dt, t, a in points)
    aktif_pts = " ".join("{:.1f},{:.1f}".format(sx(dt), sy(a)) for dt, t, a in points)

    # X ekseni etiketleri
    x_labels = []
    step = max(1, len(points) // 6)
    for i in range(0, len(points), step):
        dt, _, _ = points[i]
        if date_fmt:
            label = dt.strftime(date_fmt)
        elif len(points) <= 30:
            label = dt.strftime("%d.%m %H:%M")
        else:
            label = dt.strftime("%d.%m.%Y")
        x_labels.append('<text x="{:.1f}" y="{}" text-anchor="middle" font-size="10" fill="#888">{}</text>'.format(sx(dt), height - 20, label))

    # Y grid
    y_grid = []
    for val in range(0, 101, 20):
        y = sy(val)
        y_grid.append('<line x1="{}" y1="{:.1f}" x2="{}" y2="{:.1f}" stroke="#333" stroke-width="1" stroke-dasharray="4,4" opacity="0.5"/>'.format(margin_left, y, width - margin_right, y))
        y_grid.append('<text x="{}" y="{:.1f}" text-anchor="end" dominant-baseline="middle" font-size="10" fill="#888">{}%</text>'.format(margin_left - 10, y, val))

    # Referans çizgileri
    ref_lines = []
    if show_ref:
        for val, color, label in [(30, "#ef4444", "Kritik"), (50, "#eab308", "Normal")]:
            y = sy(val)
            ref_lines.append('<line x1="{}" y1="{:.1f}" x2="{}" y2="{:.1f}" stroke="{}" stroke-width="1" stroke-dasharray="2,2" opacity="0.7"/>'.format(margin_left, y, width - margin_right, y, color))
            ref_lines.append('<text x="{}" y="{:.1f}" dominant-baseline="middle" font-size="9" fill="{}">{} ({}%)</text>'.format(width - margin_right - 5, y, color, label, val))

    # Noktalar (sadece gerçek noktalar, sahte nokta yok)
    real_points = points[:-1] if len(points) > 1 and points[-1][0] - points[-2][0] > timedelta(days=25) else points
    toplam_circles = "".join('<circle cx="{:.1f}" cy="{:.1f}" r="3" fill="#22c55e"/>'.format(sx(dt), sy(t)) for dt, t, a in real_points)
    aktif_circles = "".join('<circle cx="{:.1f}" cy="{:.1f}" r="3" fill="#3b82f6"/>'.format(sx(dt), sy(a)) for dt, t, a in real_points)

    svg_lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {} {}" width="100%" style="max-width:{}px;">'.format(width, height, width),
        '  <rect width="{}" height="{}" fill="#0d1117" rx="6"/>'.format(width, height),
        '  <text x="{:.1f}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#c9d1d9">{}</text>'.format(width / 2, title),
        '',
        '  <!-- Y grid -->',
    ]
    for line in y_grid:
        svg_lines.append("  " + line)

    if ref_lines:
        svg_lines.append('')
        svg_lines.append('  <!-- Referans çizgileri -->')
        for line in ref_lines:
            svg_lines.append("  " + line)

    svg_lines.extend([
        '',
        '  <!-- Toplam doluluk -->',
        '  <polyline points="{}" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'.format(toplam_pts),
        '  <polyline points="{}" fill="none" stroke="#22c55e" stroke-width="5" opacity="0.1" stroke-linecap="round" stroke-linejoin="round"/>'.format(toplam_pts),
        '',
        '  <!-- Aktif doluluk -->',
        '  <polyline points="{}" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'.format(aktif_pts),
        '  <polyline points="{}" fill="none" stroke="#3b82f6" stroke-width="5" opacity="0.1" stroke-linecap="round" stroke-linejoin="round"/>'.format(aktif_pts),
        '',
        '  <!-- Noktalar -->',
        '  ' + toplam_circles,
        '  ' + aktif_circles,
        '',
        '  <!-- X ekseni -->',
    ])
    for line in x_labels:
        svg_lines.append("  " + line)

    svg_lines.extend([
        '',
        '  <!-- Legend -->',
        '  <g transform="translate({}, {})">'.format(margin_left, height - 55),
        '    <rect x="0" y="0" width="12" height="12" fill="#22c55e" rx="2"/>',
        '    <text x="18" y="10" font-size="11" fill="#c9d1d9">Toplam Doluluk</text>',
        '    <rect x="140" y="0" width="12" height="12" fill="#3b82f6" rx="2"/>',
        '    <text x="158" y="10" font-size="11" fill="#c9d1d9">Aktif Doluluk</text>',
        '  </g>',
        '</svg>',
    ])

    return "\n".join(svg_lines)


def gunluk_ozet(veriler, gun_sayisi):
    """Son N günün günlük ortalamasını döndürür."""
    gunluk = defaultdict(lambda: {"toplam": [], "aktif": []})
    for k in veriler:
        tarih = k.get("tarih_aski")
        if tarih:
            gunluk[tarih]["toplam"].append(k["toplam_doluluk"])
            gunluk[tarih]["aktif"].append(k["aktif_doluluk"])

    tum_tarihler = sorted(gunluk.keys(), key=lambda x: datetime.strptime(x, "%d.%m.%Y"))
    son_tarihler = tum_tarihler[-gun_sayisi:]

    points = []
    for tarih in son_tarihler:
        toplam_list = gunluk[tarih]["toplam"]
        aktif_list = gunluk[tarih]["aktif"]
        dt = datetime.strptime(tarih, "%d.%m.%Y")
        points.append((dt, sum(toplam_list) / len(toplam_list), sum(aktif_list) / len(aktif_list)))

    return points


def aylik_ozet(veriler, ay_sayisi):
    """Son N ayın aylık ortalamasını döndürür."""
    aylik = defaultdict(lambda: {"toplam": [], "aktif": []})
    for k in veriler:
        ts = k.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        ay_key = dt.strftime("%Y-%m")
        aylik[ay_key]["toplam"].append(k["toplam_doluluk"])
        aylik[ay_key]["aktif"].append(k["aktif_doluluk"])

    tum_aylar = sorted(aylik.keys())
    son_aylar = tum_aylar[-ay_sayisi:]

    points = []
    for ay_key in son_aylar:
        toplam_list = aylik[ay_key]["toplam"]
        aktif_list = aylik[ay_key]["aktif"]
        dt = datetime.strptime(ay_key, "%Y-%m")
        points.append((dt, sum(toplam_list) / len(toplam_list), sum(aktif_list) / len(aktif_list)))

    return points


def main():
    print("[INFO] Chart generator başladı")
    print("[INFO] DATA_FILE: {}".format(DATA_FILE.absolute()))

    if not DATA_FILE.exists():
        print("[HATA] data/aski_doluluk.json bulunamadı")
        return 1

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    veriler = data.get("veriler", [])
    print("[INFO] Toplam kayıt: {}".format(len(veriler)))

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    grafikler = []

    # 1. Son 30 gün
    points = gunluk_ozet(veriler, 30)
    if len(points) >= 1:
        svg = create_svg(points, "Son 30 Gün - Günlük Ortalama", width=800, height=400)
        path = CHART_DIR / "doluluk-30g.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        grafikler.append(("30g", len(points), path, len(svg)))

    # 2. Son 90 gün
    points = gunluk_ozet(veriler, 90)
    if len(points) >= 1:
        svg = create_svg(points, "Son 90 Gün - Günlük Ortalama", width=800, height=400)
        path = CHART_DIR / "doluluk-90g.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        grafikler.append(("90g", len(points), path, len(svg)))

    # 3. Son 180 gün
    points = gunluk_ozet(veriler, 180)
    if len(points) >= 1:
        svg = create_svg(points, "Son 180 Gün - Günlük Ortalama", width=900, height=400)
        path = CHART_DIR / "doluluk-180g.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        grafikler.append(("180g", len(points), path, len(svg)))

    # 4. Son 360 gün
    points = gunluk_ozet(veriler, 360)
    if len(points) >= 1:
        svg = create_svg(points, "Son 360 Gün - Günlük Ortalama", width=900, height=400)
        path = CHART_DIR / "doluluk-360g.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        grafikler.append(("360g", len(points), path, len(svg)))

    # 5. Son 12 ay (aylık ortalama)
    points = aylik_ozet(veriler, 12)
    if len(points) >= 1:
        svg = create_svg(points, "Son 12 Ay - Aylık Ortalama", width=800, height=400, date_fmt="%m.%Y")
        path = CHART_DIR / "doluluk-12ay.svg"
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        grafikler.append(("12ay", len(points), path, len(svg)))

    for name, nokta, path, size in grafikler:
        print("[OK] {}: {} nokta, {} bytes".format(path.name, nokta, size))

    return 0


if __name__ == "__main__":
    exit(main())

