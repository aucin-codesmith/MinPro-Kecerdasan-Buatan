# Sistem Seleksi Penerima Beasiswa, Fuzzy Mamdani

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
```

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

## Hasil Percobaan

### Percobaan 1 — Prioritas Tinggi

**Input:**

| Variabel | Nilai |
|---|---|
| IPK | 3.8 |
| Penghasilan Orang Tua | Rp 800.000 |
| Jumlah Tanggungan | 4 orang |
| Prestasi Non-Akademik | 80 |

<img width="610" height="533" alt="image" src="https://github.com/user-attachments/assets/cb97fd65-feb5-4ec3-b4fe-965e3d814b80" />


**Penjelasan:**

Pada percobaan ini, mahasiswa memiliki IPK 3.80, penghasilan orang tua Rp 800.000/bulan, jumlah tanggungan 4 orang, dan prestasi non-akademik 80. Sistem mengaktifkan dua rule, yaitu Rule 5 (IPK Sedang AND Penghasilan Rendah AND Tanggungan Sedikit) dengan α = 0.333 dan Rule 1 (IPK Tinggi AND Penghasilan Rendah) dengan α = 0.267. Hasil defuzzifikasi menghasilkan nilai crisp 63.53/100 dengan kategori Tinggi, yang menunjukkan bahwa mahasiswa ini layak mendapatkan prioritas utama dalam seleksi beasiswa.

---

### Percobaan 2 — Prioritas Sedang

**Input:**

| Variabel | Nilai |
|---|---|
| IPK | 3.0 |
| Penghasilan Orang Tua | Rp 3.500.000 |
| Jumlah Tanggungan | 3 orang |
| Prestasi Non-Akademik | 60 |

<img width="584" height="509" alt="image" src="https://github.com/user-attachments/assets/c4d69159-4da7-47eb-920b-a990a6674008" />


**Penjelasan:**

Pada percobaan ini, mahasiswa memiliki IPK 3.00, penghasilan orang tua Rp 3.500.000/bulan, jumlah tanggungan 3 orang, dan prestasi non-akademik 60. Sistem hanya mengaktifkan satu rule, yaitu Rule 6 (IPK Sedang AND Penghasilan Rendah AND Tanggungan Sedikit) dengan α = 0.333. Hasil defuzzifikasi menghasilkan nilai crisp 50.00/100 dengan kategori Sedang, yang berarti mahasiswa ini dapat dipertimbangkan sebagai penerima beasiswa jika kuota masih tersedia.

---

### Percobaan 3 — Prioritas Rendah

**Input:**

| Variabel | Nilai |
|---|---|
| IPK | 3.5 |
| Penghasilan Orang Tua | Rp 8.000.000 |
| Jumlah Tanggungan | 1 orang |
| Prestasi Non-Akademik | 40 |

<img width="617" height="539" alt="image" src="https://github.com/user-attachments/assets/358c513b-4431-4a17-b2ca-21fead0dffec" />


**Penjelasan:**

Pada percobaan ini, mahasiswa memiliki IPK 3.50, penghasilan orang tua Rp 8.000.000/bulan, jumlah tanggungan 1 orang, dan prestasi non-akademik 30. Sistem tidak mengaktifkan satu pun rule (tidak ada rule yang aktif), sehingga hasil defuzzifikasi menghasilkan nilai crisp **0.00/100** dengan kategori Rendah. Hal ini menunjukkan bahwa kombinasi penghasilan orang tua yang tinggi dengan prestasi non-akademik yang rendah menyebabkan mahasiswa ini tidak diprioritaskan sebagai penerima beasiswa.

## Catatan

Rule base dapat dimodifikasi langsung pada list `RULES` di `main.py`. Fungsi keanggotaan menggunakan `trimf` (segitiga), `zmf` (Z-shape), dan `smf` (S-shape) tanpa dependensi library eksternal.
