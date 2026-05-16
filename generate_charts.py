#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASKI Doluluk Trend Grafiği Oluşturucu
---------------------------------------
Son 30 kayıt için toplam/aktif doluluk trendini
SVG olarak çizer.
"""

import json
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA_FILE = Path("data/aski_doluluk.json")
CHART_DIR = Path("charts")


def main():
    if not DATA_FILE.exists():
        print("[HATA] Veri dosyasi bulunamadi")
        return 1

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    veriler = data.get("veriler", [])
    if len(veriler) < 2:
        print("[UYARI] Grafik icin en az 2 kayit gerekli")
        # Bos placeholder SVG olustur
        CHART_DIR.mkdir(parents=True, exist_ok=True)
        placeholder = '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300"><text x="300" y="150" text-anchor="middle" font-size="14">Yeterli veri yok</text></svg>'
        (CHART_DIR / "doluluk-trend.svg").write_text(placeholder, encoding="utf-8")
        return 0

    # Son 30 kaydi al
    kayitlar = veriler[-30:]

    tarihler = []
    toplam = []
    aktif = []

    for k in kayitlar:
        ts = k.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                tarihler.append(dt)
            except ValueError:
                continue
        else:
            continue
        toplam.append(k.get("toplam_doluluk", 0))
        aktif.append(k.get("aktif_doluluk", 0))

    if len(tarihler) < 2:
        print("[HATA] Gecerli tarih yok")
        return 1

    CHART_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(tarihler, toplam, marker="o", linewidth=2, markersize=4, label="Toplam Doluluk", color="#22c55e")
    ax.plot(tarihler, aktif, marker="s", linewidth=2, markersize=4, label="Aktif Doluluk", color="#3b82f6")

    ax.set_ylabel("Doluluk (%)", fontsize=12)
    ax.set_title("Ankara Baraj Doluluk Trendi", fontsize=14, fontweight="bold")
    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.set_ylim(0, 105)

    # X ekseni formatlama
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m %H:%M"))
    plt.xticks(rotation=30, ha="right")

    # 30% ve 50% referans cizgileri
    ax.axhline(y=30, color="#ef4444", linestyle=":", alpha=0.5, label="Kritik (30%)")
    ax.axhline(y=50, color="#eab308", linestyle=":", alpha=0.5, label="Normal (50%)")

    plt.tight_layout()
    plt.savefig(CHART_DIR / "doluluk-trend.svg", format="svg", bbox_inches="tight")
    plt.close()

    print(f"[OK] {CHART_DIR / 'doluluk-trend.svg'} olusturuldu ({len(tarihler)} kayit)")
    return 0


if __name__ == "__main__":
    exit(main())

