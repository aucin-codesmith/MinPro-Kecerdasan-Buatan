"""
Sistem Seleksi Penerima Beasiswa - Fuzzy Mamdani
================================================
Input  : IPK, Penghasilan Orang Tua, Jumlah Tanggungan, Prestasi Non-Akademik
Output : Prioritas Beasiswa (Rendah, Sedang, Tinggi)
Metode : Mamdani + Defuzzifikasi Centroid (Center of Area)
"""

import tkinter as tk
from tkinter import ttk
import math

# 1. FUNGSI KEANGGOTAAN (Membership Functions)

def trimf(x, a, b, c):
    """Segitiga: naik dari a ke b, turun dari b ke c."""
    if x <= a or x >= c:
        return 0.0
    if x <= b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)

def zmf(x, a, b):
    """Z-shape: 1 di kiri a, 0 di kanan b."""
    if x <= a:
        return 1.0
    if x >= b:
        return 0.0
    return (b - x) / (b - a)

def smf(x, a, b):
    """S-shape: 0 di kiri a, 1 di kanan b."""
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    return (x - a) / (b - a)


# 2. FUZZIFIKASI

def fuzzify_ipk(ipk):
    return {
        "Rendah": zmf(ipk, 1.5, 2.5),
        "Sedang": trimf(ipk, 2.0, 3.0, 3.5),
        "Tinggi": smf(ipk, 3.0, 3.75),
    }

def fuzzify_penghasilan(penghasilan):
    return {
        "Rendah": zmf(penghasilan, 3.0, 8.0),
        "Sedang": trimf(penghasilan, 5.0, 10.0, 15.0),
        "Tinggi": smf(penghasilan, 12.0, 18.0),
    }

def fuzzify_tanggungan(tanggungan):
    return {
        "Sedikit": zmf(tanggungan, 1.0, 4.0),
        "Sedang":  trimf(tanggungan, 2.0, 5.0, 8.0),
        "Banyak":  smf(tanggungan, 6.0, 9.0),
    }

def fuzzify_prestasi(prestasi):
    return {
        "Kurang": zmf(prestasi, 20.0, 50.0),
        "Cukup":  trimf(prestasi, 30.0, 55.0, 80.0),
        "Baik":   smf(prestasi, 65.0, 90.0),
    }


# 3. RULES

RULES = [
    (lambda i, n, d, a: min(i["Tinggi"], n["Rendah"]),
     "Tinggi",
     "IF IPK Tinggi AND Penghasilan Rendah THEN Tinggi"),

    (lambda i, n, d, a: min(i["Rendah"], n["Rendah"], d["Banyak"]),
     "Tinggi",
     "IF IPK Rendah AND Penghasilan Rendah AND Tanggungan Banyak THEN Tinggi"),

    (lambda i, n, d, a: min(i["Sedang"], n["Rendah"], d["Banyak"]),
     "Tinggi",
     "IF IPK Sedang AND Penghasilan Rendah AND Tanggungan Banyak THEN Tinggi"),

    (lambda i, n, d, a: min(i["Tinggi"], n["Sedang"], a["Baik"]),
     "Tinggi",
     "IF IPK Tinggi AND Penghasilan Sedang AND Prestasi Baik THEN Tinggi"),

    (lambda i, n, d, a: min(i["Sedang"], n["Sedang"], d["Sedang"]),
     "Sedang",
     "IF IPK Sedang AND Penghasilan Sedang AND Tanggungan Sedang THEN Sedang"),

    (lambda i, n, d, a: min(i["Sedang"], n["Rendah"], d["Sedikit"]),
     "Sedang",
     "IF IPK Sedang AND Penghasilan Rendah AND Tanggungan Sedikit THEN Sedang"),

    (lambda i, n, d, a: min(i["Tinggi"], n["Tinggi"]),
     "Rendah",
     "IF IPK Tinggi AND Penghasilan Tinggi THEN Rendah"),

    (lambda i, n, d, a: i["Rendah"],
     "Rendah",
     "IF IPK Rendah THEN Rendah"),

    (lambda i, n, d, a: min(i["Sedang"], n["Tinggi"], a["Kurang"]),
     "Rendah",
     "IF IPK Sedang AND Penghasilan Tinggi AND Prestasi Kurang THEN Rendah"),
]


# 4. INFERENSI & DEFUZZIFIKASI

def mf_output_rendah(x):
    return trimf(x, 0.0, 20.0, 40.0)

def mf_output_sedang(x):
    return trimf(x, 30.0, 50.0, 70.0)

def mf_output_tinggi(x):
    return trimf(x, 60.0, 80.0, 100.0)

def inferensi_mamdani(ipk, penghasilan, tanggungan, prestasi):
    i = fuzzify_ipk(ipk)
    n = fuzzify_penghasilan(penghasilan)
    d = fuzzify_tanggungan(tanggungan)
    a = fuzzify_prestasi(prestasi)

    alpha_R = 0.0
    alpha_S = 0.0
    alpha_T = 0.0
    active_rules = []

    for cond, output, desc in RULES:
        alpha = cond(i, n, d, a)
        if output == "Rendah":
            alpha_R = max(alpha_R, alpha)
        elif output == "Sedang":
            alpha_S = max(alpha_S, alpha)
        elif output == "Tinggi":
            alpha_T = max(alpha_T, alpha)
        if alpha > 0.001:
            active_rules.append((alpha, output, desc))

    return alpha_R, alpha_S, alpha_T, active_rules

def defuzzifikasi_centroid(alpha_R, alpha_S, alpha_T, n_points=500):
    total_numerator = 0.0
    total_denominator = 0.0
    for k in range(n_points + 1):
        x = k / n_points * 100.0
        mu_R = min(alpha_R, mf_output_rendah(x))
        mu_S = min(alpha_S, mf_output_sedang(x))
        mu_T = min(alpha_T, mf_output_tinggi(x))
        mu   = max(mu_R, mu_S, mu_T)
        total_numerator   += x * mu
        total_denominator += mu
    if total_denominator == 0:
        return 0.0
    return total_numerator / total_denominator

def hitung_prioritas(ipk, penghasilan, tanggungan, prestasi):
    aR, aS, aT, active = inferensi_mamdani(ipk, penghasilan, tanggungan, prestasi)
    crisp = defuzzifikasi_centroid(aR, aS, aT)

    if crisp >= 60:
        label = "TINGGI"
    elif crisp >= 35:
        label = "SEDANG"
    else:
        label = "RENDAH"

    return {
        "crisp": crisp,
        "label": label,
        "alpha_R": aR,
        "alpha_S": aS,
        "alpha_T": aT,
        "active_rules": sorted(active, key=lambda x: -x[0]),
    }


# 5. GUI (Tkinter)

class BeasiswaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Seleksi Beasiswa — Fuzzy Mamdani")
        self.resizable(True, True)
        self.configure(bg="#F8F8F6")
        self._build_ui()

    # ── Warna & Style ──────────────────────────
    BG      = "#E6E4F1"
    PANEL   = "#FFFFFF"
    BORDER  = "#E0DED8"
    TEXT1   = "#1A1A18"
    TEXT2   = "#6B6B67"
    RED     = "#E24B4A"
    AMBER   = "#EF9F27"
    GREEN   = "#639922"
    ACCENT  = "#4A4A46"

    # Graph colors (semi-transparent look using stipple or solid)
    C_RENDAH = "#E24B4A"
    C_SEDANG  = "#EF9F27"
    C_TINGGI  = "#639922"
    C_FILL_R  = "#F5A8A8"
    C_FILL_S  = "#FAD79A"
    C_FILL_T  = "#B8D98B"
    C_DEFUZZ  = "#4A4A46"  # centroid line

    def _panel(self, parent, **kwargs):
        f = tk.Frame(parent, bg=self.PANEL, bd=0, highlightthickness=1,
                     highlightbackground=self.BORDER, **kwargs)
        return f

    def _label(self, parent, text, size=13, color=None, bold=False):
        c = color or self.TEXT1
        w = "bold" if bold else "normal"
        return tk.Label(parent, text=text, font=("Helvetica", size, w),
                        bg=parent["bg"], fg=c)

    def _slider_row(self, parent, label, var, from_, to_, resolution, fmt):
        header = tk.Frame(parent, bg=self.PANEL)
        header.pack(fill="x", pady=(6, 0))
        tk.Label(header, text=label, font=("Helvetica", 12), bg=self.PANEL,
                 fg=self.TEXT2, anchor="w").pack(side="left")
        val_lbl = tk.Label(header, text="", font=("Helvetica", 12, "bold"),
                           bg=self.PANEL, fg=self.TEXT1, anchor="e")
        val_lbl.pack(side="right")

        s = ttk.Scale(parent, from_=from_, to=to_, variable=var,
                      orient="horizontal")
        s.pack(fill="x", pady=(2, 4))

        def update_label(*_):
            v = var.get()
            val_lbl.config(text=fmt.format(v))

        var.trace_add("write", update_label)
        update_label()
        return s

    # ── Bangun UI ─────────────────────────────
    def _build_ui(self):
        # Outer scrollable container
        outer = tk.Frame(self, bg=self.BG)
        outer.pack(fill="both", expand=True)

        root_pad = tk.Frame(outer, bg=self.BG, padx=16, pady=14)
        root_pad.pack(fill="both", expand=True)

        # Judul
        self._label(root_pad, "Sistem Seleksi Penerima Beasiswa",
                    size=15, bold=True).pack(anchor="w", pady=(0, 2))
        self._label(root_pad, "Metode Fuzzy Mamdani — Defuzzifikasi Centroid",
                    size=11, color=self.TEXT2).pack(anchor="w", pady=(0, 10))

        content = tk.Frame(root_pad, bg=self.BG)
        content.pack(fill="both")

        # ── Panel Kiri: Input ────────────────
        left = self._panel(content)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        self._label(left, "Data Input Mahasiswa", size=11, color=self.TEXT2,
                    bold=True).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Frame(left, height=1, bg=self.BORDER).pack(fill="x", padx=12, pady=(0, 8))

        inp = tk.Frame(left, bg=self.PANEL, padx=12, pady=0)
        inp.pack(fill="x")

        self.var_ipk = tk.DoubleVar(value=3.2)
        self.var_inc = tk.DoubleVar(value=4.0)
        self.var_dep = tk.IntVar(value=3)
        self.var_ach = tk.IntVar(value=60)

        self._slider_row(inp, "IPK  (0.00 – 4.00)",
                         self.var_ipk, 0.0, 4.0, 0.01, "{:.2f}")
        self._slider_row(inp, "Penghasilan  (0 – 20 jt/bln)",
                         self.var_inc, 0.0, 20.0, 0.5, "{:.1f} jt")
        self._slider_row(inp, "Jumlah tanggungan  (0 – 10)",
                         self.var_dep, 0, 10, 1, "{:d} orang")
        self._slider_row(inp, "Prestasi non-akademik  (0 – 100)",
                         self.var_ach, 0, 100, 1, "{:d}")

        tk.Frame(inp, height=8, bg=self.PANEL).pack()

        btn = tk.Button(inp, text="Hitung Prioritas Beasiswa ▶",
                        font=("Helvetica", 12, "bold"),
                        bg=self.ACCENT, fg="white", relief="flat",
                        cursor="hand2", padx=10, pady=8,
                        command=self._hitung)
        btn.pack(fill="x", pady=(0, 12))

        # ── Panel Kanan: Hasil ───────────────
        right = tk.Frame(content, bg=self.BG)
        right.grid(row=0, column=1, sticky="nsew")

        res_panel = self._panel(right)
        res_panel.pack(fill="x", pady=(0, 8))

        self._label(res_panel, "Hasil Defuzzifikasi", size=11,
                    color=self.TEXT2, bold=True).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Frame(res_panel, height=1, bg=self.BORDER).pack(fill="x", padx=12, pady=(0, 8))

        rinner = tk.Frame(res_panel, bg=self.PANEL, padx=12, pady=0)
        rinner.pack(fill="x")

        self.lbl_priority = tk.Label(rinner, text="—",
                                     font=("Helvetica", 28, "bold"),
                                     bg=self.PANEL, fg=self.TEXT2)
        self.lbl_priority.pack()

        self.lbl_crisp = tk.Label(rinner, text="Jalankan perhitungan terlebih dahulu",
                                  font=("Helvetica", 11), bg=self.PANEL, fg=self.TEXT2)
        self.lbl_crisp.pack(pady=(0, 4))

        bar_frame = tk.Frame(rinner, bg=self.PANEL)
        bar_frame.pack(fill="x", pady=(4, 10))

        self.bars = {}
        self.bar_labels = {}
        for out, color in [("Rendah", self.RED), ("Sedang", self.AMBER), ("Tinggi", self.GREEN)]:
            row = tk.Frame(bar_frame, bg=self.PANEL)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=out, font=("Helvetica", 11), bg=self.PANEL,
                     fg=self.TEXT2, width=7, anchor="w").pack(side="left")
            bg_bar = tk.Frame(row, bg="#EEECE6", height=10, bd=0)
            bg_bar.pack(side="left", fill="x", expand=True, padx=(4, 6))
            fill = tk.Frame(bg_bar, bg=color, height=10, width=0)
            fill.place(x=0, y=0, relheight=1)
            self.bars[out] = (bg_bar, fill)
            lbl = tk.Label(row, text="α = 0.00", font=("Helvetica", 11),
                           bg=self.PANEL, fg=self.TEXT2, width=8, anchor="e")
            lbl.pack(side="left")
            self.bar_labels[out] = lbl

        rules_panel = self._panel(right)
        rules_panel.pack(fill="both", expand=True)

        self._label(rules_panel, "Rules Aktif (α > 0)", size=11,
                    color=self.TEXT2, bold=True).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Frame(rules_panel, height=1, bg=self.BORDER).pack(fill="x", padx=12, pady=(0, 4))

        self.rules_text = tk.Text(rules_panel, font=("Helvetica", 10),
                                  bg=self.PANEL, fg=self.TEXT1, relief="flat",
                                  height=8, wrap="word", padx=10, pady=4,
                                  state="disabled")
        self.rules_text.pack(fill="both", expand=True, padx=4, pady=(0, 8))

        # ── Panel Bawah: Graf Mamdani ────────
        self._build_graph_panel(root_pad)

        self.after(100, self._hitung)

    def _build_graph_panel(self, parent):
        """Panel grafik Mamdani di bawah dua panel utama."""
        graph_outer = self._panel(parent)
        graph_outer.pack(fill="both", expand=True, pady=(12, 0))

        # Header
        hdr = tk.Frame(graph_outer, bg=self.PANEL, padx=12)
        hdr.pack(fill="x", pady=(10, 0))

        self._label(hdr, "Visualisasi Inferensi Mamdani", size=11,
                    color=self.TEXT2, bold=True).pack(side="left")

        # Legend
        legend = tk.Frame(hdr, bg=self.PANEL)
        legend.pack(side="right")
        for lbl, color in [("Rendah", self.C_RENDAH), ("Sedang", self.C_SEDANG),
                            ("Tinggi", self.C_TINGGI)]:
            dot = tk.Frame(legend, bg=color, width=10, height=10)
            dot.pack(side="left", padx=(6, 2), pady=4)
            tk.Label(legend, text=lbl, font=("Helvetica", 10), bg=self.PANEL,
                     fg=self.TEXT2).pack(side="left", padx=(0, 6))
        # Centroid legend
        tk.Frame(legend, bg=self.C_DEFUZZ, width=2, height=14).pack(side="left", padx=(6,2))
        tk.Label(legend, text="Centroid", font=("Helvetica", 10), bg=self.PANEL,
                 fg=self.TEXT2).pack(side="left", padx=(0, 6))

        tk.Frame(graph_outer, height=1, bg=self.BORDER).pack(fill="x", padx=12, pady=(6, 0))

        # Sub-panels: 3 kolom (MF Output | Aggregasi | Keterangan)
        graph_content = tk.Frame(graph_outer, bg=self.PANEL, padx=12, pady=10)
        graph_content.pack(fill="both", expand=True)
        graph_content.columnconfigure(0, weight=3)
        graph_content.columnconfigure(1, weight=3)
        graph_content.columnconfigure(2, weight=2)

        # ── Canvas kiri: Fungsi Keanggotaan Output (asli, tanpa alpha cut) ──
        lbl_mf = tk.Label(graph_content, text="Fungsi Keanggotaan Output",
                          font=("Helvetica", 10, "bold"), bg=self.PANEL, fg=self.TEXT2)
        lbl_mf.grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.canvas_mf = tk.Canvas(graph_content, bg="#FAFAF8", height=180,
                                   highlightthickness=1, highlightbackground=self.BORDER)
        self.canvas_mf.grid(row=1, column=0, sticky="nsew", padx=(0, 8))

        # ── Canvas tengah: Hasil Agregasi + Centroid ──
        lbl_agg = tk.Label(graph_content, text="Hasil Agregasi & Defuzzifikasi",
                           font=("Helvetica", 10, "bold"), bg=self.PANEL, fg=self.TEXT2)
        lbl_agg.grid(row=0, column=1, sticky="w", pady=(0, 4))

        self.canvas_agg = tk.Canvas(graph_content, bg="#FAFAF8", height=180,
                                    highlightthickness=1, highlightbackground=self.BORDER)
        self.canvas_agg.grid(row=1, column=1, sticky="nsew", padx=(0, 8))

        # ── Panel kanan: ringkasan alpha ──
        lbl_sum = tk.Label(graph_content, text="Ringkasan Alpha",
                           font=("Helvetica", 10, "bold"), bg=self.PANEL, fg=self.TEXT2)
        lbl_sum.grid(row=0, column=2, sticky="w", pady=(0, 4))

        summary_frame = tk.Frame(graph_content, bg="#FAFAF8", highlightthickness=1,
                                 highlightbackground=self.BORDER)
        summary_frame.grid(row=1, column=2, sticky="nsew")

        self.alpha_labels = {}
        self.alpha_bars_canvas = {}

        for idx, (name, color, fill_c) in enumerate([
            ("Rendah", self.C_RENDAH, self.C_FILL_R),
            ("Sedang", self.C_SEDANG, self.C_FILL_S),
            ("Tinggi", self.C_TINGGI, self.C_FILL_T),
        ]):
            blk = tk.Frame(summary_frame, bg="#FAFAF8", padx=10, pady=8)
            blk.pack(fill="x", expand=True)

            # Title row
            title_row = tk.Frame(blk, bg="#FAFAF8")
            title_row.pack(fill="x")
            dot = tk.Frame(title_row, bg=color, width=10, height=10)
            dot.pack(side="left", pady=2)
            tk.Label(title_row, text=f"  {name}", font=("Helvetica", 11, "bold"),
                     bg="#FAFAF8", fg=self.TEXT1).pack(side="left")

            # Alpha value
            val_lbl = tk.Label(blk, text="α = 0.000", font=("Helvetica", 10),
                               bg="#FAFAF8", fg=self.TEXT2)
            val_lbl.pack(anchor="w")
            self.alpha_labels[name] = val_lbl

            # Mini progress bar
            bar_bg = tk.Frame(blk, bg="#E8E6E0", height=8)
            bar_bg.pack(fill="x", pady=(3, 0))
            bar_fill = tk.Frame(bar_bg, bg=color, height=8, width=0)
            bar_fill.place(x=0, y=0, relheight=1)
            self.alpha_bars_canvas[name] = (bar_bg, bar_fill, color)

            if idx < 2:
                tk.Frame(summary_frame, height=1, bg=self.BORDER).pack(fill="x", padx=10)

        # Crisp value di bawah
        self.lbl_crisp_graph = tk.Label(summary_frame, text="Crisp: —",
                                        font=("Helvetica", 11, "bold"),
                                        bg="#FAFAF8", fg=self.TEXT1)
        self.lbl_crisp_graph.pack(pady=(8, 8))

    # ── Gambar Grafik ────────────────────────────────────────────────────────

    def _draw_graph(self, alpha_R, alpha_S, alpha_T, crisp):
        """Gambar kedua canvas: MF asli + Agregasi+Centroid."""
        self.canvas_mf.update_idletasks()
        self.canvas_agg.update_idletasks()
        W_mf  = self.canvas_mf.winfo_width()
        H_mf  = self.canvas_mf.winfo_height()
        W_agg = self.canvas_agg.winfo_width()
        H_agg = self.canvas_agg.winfo_height()

        if W_mf < 10 or H_mf < 10:
            return  # belum ter-render

        PAD_L, PAD_R, PAD_T, PAD_B = 36, 12, 12, 28

        # Helper: domain x=0..100 → canvas pixel
        def to_px(x, W):
            return PAD_L + (x / 100.0) * (W - PAD_L - PAD_R)

        def to_py(mu, H):
            return PAD_T + (1.0 - mu) * (H - PAD_T - PAD_B)

        N = 400  # resolusi sampling

        # ── Canvas MF (kiri): tampilkan MF asli tanpa alpha cut ──
        c = self.canvas_mf
        c.delete("all")
        W, H = W_mf, H_mf

        # Grid & sumbu
        self._draw_axes(c, W, H, PAD_L, PAD_R, PAD_T, PAD_B)

        # Plot 3 MF output
        configs_mf = [
            ("Rendah", mf_output_rendah, self.C_RENDAH, self.C_FILL_R),
            ("Sedang",  mf_output_sedang,  self.C_SEDANG,  self.C_FILL_S),
            ("Tinggi",  mf_output_tinggi,  self.C_TINGGI,  self.C_FILL_T),
        ]
        for name, fn, col, fill in configs_mf:
            pts = []
            for k in range(N + 1):
                x = k / N * 100.0
                mu = fn(x)
                pts.append(to_px(x, W))
                pts.append(to_py(mu, H))
            # Fill area
            fill_pts = [to_px(0, W), to_py(0, H)] + pts + [to_px(100, W), to_py(0, H)]
            c.create_polygon(fill_pts, fill=fill, outline="", stipple="")
            # Outline
            c.create_line(pts, fill=col, width=2, smooth=False)

        # Legend kecil di dalam canvas
        for i, (name, _, col, _) in enumerate(configs_mf):
            c.create_rectangle(W - 70, PAD_T + i*16, W - 60, PAD_T + i*16 + 10,
                               fill=col, outline="")
            c.create_text(W - 56, PAD_T + i*16 + 5, text=name,
                          anchor="w", font=("Helvetica", 8), fill=self.TEXT2)

        # Label sumbu
        c.create_text(W // 2, H - 6, text="Prioritas Beasiswa (0–100)",
                      font=("Helvetica", 8), fill=self.TEXT2)

        # ── Canvas AGG (kanan): MF dipotong alpha + centroid ──
        c2 = self.canvas_agg
        c2.delete("all")
        W2, H2 = W_agg, H_agg

        self._draw_axes(c2, W2, H2, PAD_L, PAD_R, PAD_T, PAD_B)

        configs_agg = [
            ("Rendah", mf_output_rendah, alpha_R, self.C_RENDAH, self.C_FILL_R),
            ("Sedang",  mf_output_sedang,  alpha_S, self.C_SEDANG,  self.C_FILL_S),
            ("Tinggi",  mf_output_tinggi,  alpha_T, self.C_TINGGI,  self.C_FILL_T),
        ]

        # Gambar area yang terpotong (alpha cut) + aggregasi (max)
        # Kumpulkan semua titik per x untuk max aggregation
        agg_pts_top = []
        for k in range(N + 1):
            x = k / N * 100.0
            mu_R = min(alpha_R, mf_output_rendah(x))
            mu_S = min(alpha_S, mf_output_sedang(x))
            mu_T = min(alpha_T, mf_output_tinggi(x))
            mu_agg = max(mu_R, mu_S, mu_T)
            agg_pts_top.append((x, mu_agg))

        # Gambar fill masing-masing MF terclip dulu (di belakang)
        for name, fn, alpha, col, fill in configs_agg:
            if alpha < 0.001:
                continue
            pts = []
            for k in range(N + 1):
                x = k / N * 100.0
                mu = min(alpha, fn(x))
                pts.append(to_px(x, W2))
                pts.append(to_py(mu, H2))
            fill_pts = [to_px(0, W2), to_py(0, H2)] + pts + [to_px(100, W2), to_py(0, H2)]
            c2.create_polygon(fill_pts, fill=fill, outline="")

        # Gambar garis MF asli (tipis, putus-putus) sebagai referensi
        for name, fn, alpha, col, fill in configs_agg:
            pts_ref = []
            for k in range(N + 1):
                x = k / N * 100.0
                mu = fn(x)
                pts_ref.append(to_px(x, W2))
                pts_ref.append(to_py(mu, H2))
            c2.create_line(pts_ref, fill=col, width=1, dash=(4, 3))

        # Garis horizontal alpha cut per MF
        for name, fn, alpha, col, fill in configs_agg:
            if alpha < 0.001:
                continue
            # Cari rentang x di mana fn(x) > 0
            xs_active = [k / N * 100.0 for k in range(N + 1) if fn(k / N * 100.0) > 0.001]
            if xs_active:
                x_start, x_end = xs_active[0], xs_active[-1]
                # alpha cut line
                py_alpha = to_py(alpha, H2)
                c2.create_line(to_px(x_start, W2), py_alpha,
                               to_px(x_end, W2), py_alpha,
                               fill=col, width=1.5, dash=(2, 2))
                # label α
                c2.create_text(to_px(x_end, W2) + 4, py_alpha,
                               text=f"α={alpha:.2f}", anchor="w",
                               font=("Helvetica", 7), fill=col)

        # Gambar outline aggregasi (max dari semua)
        agg_line = []
        for x, mu in agg_pts_top:
            agg_line.append(to_px(x, W2))
            agg_line.append(to_py(mu, H2))
        if len(agg_line) >= 4:
            c2.create_line(agg_line, fill="#333333", width=1.5)

        # Garis centroid vertikal
        if crisp > 0:
            px_crisp = to_px(crisp, W2)
            c2.create_line(px_crisp, PAD_T, px_crisp, H2 - PAD_B,
                           fill=self.C_DEFUZZ, width=2, dash=(6, 3))
            # Label crisp
            txt_x = px_crisp + 4 if px_crisp < W2 * 0.75 else px_crisp - 4
            anchor = "w" if px_crisp < W2 * 0.75 else "e"
            c2.create_text(txt_x, PAD_T + 10,
                           text=f"z* = {crisp:.1f}",
                           anchor=anchor, font=("Helvetica", 8, "bold"),
                           fill=self.C_DEFUZZ)
            # Titik centroid di sumbu x
            c2.create_oval(px_crisp - 4, H2 - PAD_B - 4,
                           px_crisp + 4, H2 - PAD_B + 4,
                           fill=self.C_DEFUZZ, outline="white", width=1.5)

        # Label sumbu
        c2.create_text(W2 // 2, H2 - 6, text="Prioritas Beasiswa (0–100)",
                       font=("Helvetica", 8), fill=self.TEXT2)

    def _draw_axes(self, c, W, H, PAD_L, PAD_R, PAD_T, PAD_B):
        """Gambar grid, sumbu X dan Y."""
        # Grid horizontal (0.0, 0.25, 0.5, 0.75, 1.0)
        for mu_tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
            py = PAD_T + (1.0 - mu_tick) * (H - PAD_T - PAD_B)
            c.create_line(PAD_L, py, W - PAD_R, py,
                          fill="#E8E6E0", width=1)
            c.create_text(PAD_L - 4, py, text=f"{mu_tick:.2f}",
                          anchor="e", font=("Helvetica", 7), fill="#9A9A96")

        # Grid vertikal (0, 20, 40, 60, 80, 100)
        for x_tick in range(0, 101, 20):
            px = PAD_L + (x_tick / 100.0) * (W - PAD_L - PAD_R)
            c.create_line(px, PAD_T, px, H - PAD_B,
                          fill="#E8E6E0", width=1)
            c.create_text(px, H - PAD_B + 4, text=str(x_tick),
                          anchor="n", font=("Helvetica", 7), fill="#9A9A96")

        # Sumbu utama
        c.create_line(PAD_L, PAD_T, PAD_L, H - PAD_B,
                      fill="#CCCAC4", width=1.5)
        c.create_line(PAD_L, H - PAD_B, W - PAD_R, H - PAD_B,
                      fill="#CCCAC4", width=1.5)

        # Label Y
        c.create_text(10, PAD_T + (H - PAD_T - PAD_B) // 2,
                      text="μ", font=("Helvetica", 9, "bold"),
                      fill="#9A9A96", angle=90)

    # ── Hitung & Update UI ───────────────────
    def _hitung(self):
        ipk         = round(self.var_ipk.get(), 2)
        penghasilan = round(self.var_inc.get(), 1)
        tanggungan  = self.var_dep.get()
        prestasi    = self.var_ach.get()

        hasil = hitung_prioritas(ipk, penghasilan, tanggungan, prestasi)

        # Warna prioritas
        col_map = {"TINGGI": self.GREEN, "SEDANG": self.AMBER, "RENDAH": self.RED}
        self.lbl_priority.config(text=hasil["label"],
                                 fg=col_map.get(hasil["label"], self.TEXT1))
        self.lbl_crisp.config(
            text=f"Nilai crisp (defuzzifikasi): {hasil['crisp']:.2f} / 100")

        # Update bar alpha (panel atas)
        total = (hasil["alpha_R"] + hasil["alpha_S"] + hasil["alpha_T"]) or 1.0
        for out, key in [("Rendah", "alpha_R"), ("Sedang", "alpha_S"), ("Tinggi", "alpha_T")]:
            alpha = hasil[key]
            pct   = alpha / total
            bg_bar, fill = self.bars[out]
            bg_bar.update_idletasks()
            w = int(bg_bar.winfo_width() * pct)
            fill.place(x=0, y=0, height=10, width=max(w, 0))
            self.bar_labels[out].config(text=f"α = {alpha:.2f}")

        # Update rules aktif
        self.rules_text.config(state="normal")
        self.rules_text.delete("1.0", "end")
        if hasil["active_rules"]:
            for alpha, output, desc in hasil["active_rules"]:
                self.rules_text.insert("end", f"α = {alpha:.3f}  →  {desc}\n")
        else:
            self.rules_text.insert("end", "Tidak ada rule yang aktif.")
        self.rules_text.config(state="disabled")

        # Update ringkasan alpha (panel graf)
        for name, key in [("Rendah", "alpha_R"), ("Sedang", "alpha_S"), ("Tinggi", "alpha_T")]:
            alpha = hasil[key]
            self.alpha_labels[name].config(text=f"α = {alpha:.3f}")
            bg_bar, bar_fill, color = self.alpha_bars_canvas[name]
            bg_bar.update_idletasks()
            w = int(bg_bar.winfo_width() * alpha)  # alpha 0-1
            bar_fill.place(x=0, y=0, height=8, width=max(w, 0))

        self.lbl_crisp_graph.config(text=f"Crisp: {hasil['crisp']:.2f} / 100")

        # Gambar grafik Mamdani
        self._draw_graph(hasil["alpha_R"], hasil["alpha_S"], hasil["alpha_T"], hasil["crisp"])

        # Jadwalkan redraw setelah resize
        self.after(50, lambda: self._draw_graph(
            hasil["alpha_R"], hasil["alpha_S"], hasil["alpha_T"], hasil["crisp"]))


# 6. DEMO CLI

def demo_cli():
    contoh = [
        (3.7, 2.0, 5, 80),
        (2.3, 12.0, 2, 40),
        (3.1, 6.0, 4, 65),
    ]
    print("=" * 60)
    print("  DEMO CLI — Sistem Seleksi Beasiswa Fuzzy Mamdani")
    print("=" * 60)
    for ipk, inc, dep, ach in contoh:
        h = hitung_prioritas(ipk, inc, dep, ach)
        print(f"\nInput  : IPK={ipk}, Penghasilan={inc} jt, "
              f"Tanggungan={dep}, Prestasi={ach}")
        print(f"Crisp  : {h['crisp']:.2f}")
        print(f"Output : {h['label']}")
        print(f"Alpha  : R={h['alpha_R']:.3f}  S={h['alpha_S']:.3f}  T={h['alpha_T']:.3f}")
        print("Rules aktif:")
        for a, out, desc in h["active_rules"]:
            print(f"  α={a:.3f}  {desc}")
    print("=" * 60)


# MAIN

if __name__ == "__main__":
    import sys
    if "--cli" in sys.argv:
        demo_cli()
    else:
        app = BeasiswaApp()
        app.mainloop()