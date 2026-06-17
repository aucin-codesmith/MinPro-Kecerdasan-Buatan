# Sistem Seleksi Penerima Beasiswa — Fuzzy Mamdani

Aplikasi interaktif untuk menentukan prioritas penerima beasiswa menggunakan Sistem Inferensi Fuzzy metode Mamdani.

## Tech Stack

- Python 3.8+
- Tkinter (GUI bawaan Python)
- Pure Python fuzzy engine (tanpa library eksternal)

## Menjalankan Aplikasi

```bash
# Clone repository
git clone https://github.com/aucin-codesmith/MinPro-Kecerdasan-Buatan.git
cd beasiswa-fuzzy-mamdani

# Jalankan GUI
python main.py


## Variabel Input & Output

| Variabel | Range | Himpunan Fuzzy |
|---|---|---|
| IPK | 0.00 – 4.00 | Rendah, Sedang, Tinggi |
| Penghasilan Orang Tua | 0 – 20 jt/bln | Rendah, Sedang, Tinggi |
| Jumlah Tanggungan | 0 – 10 orang | Sedikit, Sedang, Banyak |
| Prestasi Non-Akademik | 0 – 100 | Kurang, Cukup, Baik |
| **Output: Prioritas Beasiswa** | 0 – 100 | Rendah, Sedang, Tinggi |

## Struktur Project

```
beasiswa-fuzzy-mamdani/
│
├── main.py     # Program utama (logika fuzzy + GUI Tkinter)
└── README.md
```

- `main.py` — entrypoint utama: fuzzifikasi, rule base, inferensi, defuzzifikasi, dan GUI

## Rule Base (9 Rules)

```
IF IPK Tinggi AND Penghasilan Rendah                            → TINGGI
IF IPK Rendah AND Penghasilan Rendah AND Tanggungan Banyak     → TINGGI
IF IPK Sedang AND Penghasilan Rendah AND Tanggungan Banyak     → TINGGI
IF IPK Tinggi AND Penghasilan Sedang AND Prestasi Baik         → TINGGI
IF IPK Sedang AND Penghasilan Sedang AND Tanggungan Sedang     → SEDANG
IF IPK Sedang AND Penghasilan Rendah AND Tanggungan Sedikit    → SEDANG
IF IPK Tinggi AND Penghasilan Tinggi                           → RENDAH
IF IPK Rendah                                                  → RENDAH
IF IPK Sedang AND Penghasilan Tinggi AND Prestasi Kurang       → RENDAH
```

## Catatan

Rule base dapat dimodifikasi langsung pada list `RULES` di `main.py`. Fungsi keanggotaan menggunakan `trimf` (segitiga), `zmf` (Z-shape), dan `smf` (S-shape) tanpa dependensi library eksternal.
