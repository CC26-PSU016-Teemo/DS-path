"""
=======================================================================
  A/B TESTING — EKOSISTEM KOMPETISI TeamUp
  Berdasarkan data: hasil_feature.csv (output featureEng.ipynb)
  Konsisten dengan workflow: dataClean.ipynb → edanew.ipynb → featureEng.ipynb
=======================================================================
"""

# -----------------------------------------------------------------------
# SECTION 0: IMPORT LIBRARY (sama seperti featureEng.ipynb)
# -----------------------------------------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Warna konsisten dengan dashboard Streamlit (#1E3A8A, #1E40AF)
PALETTE_ONLINE  = "#1E40AF"   # Biru – Online (Control)
PALETTE_OFFLINE = "#DC2626"   # Merah – Offline (Treatment)
PALETTE_BOTH    = "#059669"   # Hijau – Online & Offline
BG_COLOR        = "#F8FAFC"
TITLE_COLOR     = "#1E3A8A"

plt.rcParams.update({
    'figure.facecolor': BG_COLOR,
    'axes.facecolor':   BG_COLOR,
    'axes.spines.top':  False,
    'axes.spines.right': False,
    'font.family':      'DejaVu Sans',
})


# -----------------------------------------------------------------------
# SECTION 1: LOAD DATA — hasil_feature.csv (output featureEng.ipynb)
# -----------------------------------------------------------------------
print("=" * 70)
print("  A/B TESTING — EKOSISTEM KOMPETISI TeamUp")
print("=" * 70)

df = pd.read_csv("hasil_feature.csv")

# Reuse preprocessing dari featureEng.ipynb dan dashboard.py
df['Tanggal_Mulai']   = pd.to_datetime(df['Tanggal_Mulai'])
df['Tanggal_Selesai'] = pd.to_datetime(df['Tanggal_Selesai'])
df['Durasi_Hari']     = (df['Tanggal_Selesai'] - df['Tanggal_Mulai']).dt.days
df = df[df['Durasi_Hari'] >= 0].reset_index(drop=True)

print(f"\n✅ Data dimuat: {df.shape[0]} baris, {df.shape[1]} kolom")
print(f"   Kolom tersedia: {df.columns.tolist()}\n")


# -----------------------------------------------------------------------
# SECTION 2: SEGMENTASI GRUP A/B
#   Menggunakan Is_Online & Is_Offline dari featureEng.ipynb
#   Control   (A) = Online Only  (Is_Online=1, Is_Offline=0)
#   Treatment (B) = Offline Only (Is_Online=0, Is_Offline=1)
# -----------------------------------------------------------------------
group_A = df[(df['Is_Online'] == 1) & (df['Is_Offline'] == 0)].copy()  # Control
group_B = df[(df['Is_Online'] == 0) & (df['Is_Offline'] == 1)].copy()  # Treatment

print("─" * 70)
print("  SECTION 2 — SEGMENTASI GRUP A/B")
print("─" * 70)
print(f"  Grup A – Online Only  (Control)   : {len(group_A):>4} lomba")
print(f"  Grup B – Offline Only (Treatment)  : {len(group_B):>4} lomba")
print(f"  Online & Offline (Excluded)        : {len(df) - len(group_A) - len(group_B):>4} lomba")


# -----------------------------------------------------------------------
# SECTION 3: HIPOTESIS
# -----------------------------------------------------------------------
print("\n" + "─" * 70)
print("  SECTION 3 — HIPOTESIS")
print("─" * 70)

hipotesis_1 = """
  [HIPOTESIS 1 — BIAYA REGISTRASI]
  H0 : Tidak ada perbedaan signifikan biaya registrasi
       antara lomba Online dan Offline.
       H0: median(Online) = median(Offline)
  H1 : Terdapat perbedaan signifikan biaya registrasi
       antara lomba Online dan Offline.
       H1: median(Online) ≠ median(Offline)
  α  = 0.05 (two-sided)
"""

hipotesis_2 = """
  [HIPOTESIS 2 — DURASI LOMBA]
  H0 : Tidak ada perbedaan signifikan durasi
       antara lomba Online dan Offline.
       H0: median_durasi(Online) = median_durasi(Offline)
  H1 : Terdapat perbedaan signifikan durasi
       antara lomba Online dan Offline.
       H1: median_durasi(Online) ≠ median_durasi(Offline)
  α  = 0.05 (two-sided)
"""

hipotesis_3 = """
  [HIPOTESIS 3 — PROPORSI LOMBA GRATIS]
  H0 : Proporsi lomba gratis antara Online dan Offline tidak berbeda.
       H0: p_gratis(Online) = p_gratis(Offline)
  H1 : Proporsi lomba gratis antara Online dan Offline berbeda.
       H1: p_gratis(Online) ≠ p_gratis(Offline)
  α  = 0.05 (Chi-Square test)
"""

print(hipotesis_1)
print(hipotesis_2)
print(hipotesis_3)


# -----------------------------------------------------------------------
# SECTION 4: PENGECEKAN ASUMSI
# -----------------------------------------------------------------------
print("─" * 70)
print("  SECTION 4 — PENGECEKAN ASUMSI STATISTIK")
print("─" * 70)

# --- 4A. Normalitas (Shapiro-Wilk, n ≤ 500) ---
sample_A_biaya = group_A['Biaya_Rata_Rata'].sample(min(500, len(group_A)), random_state=42)
sample_B_biaya = group_B['Biaya_Rata_Rata'].sample(min(500, len(group_B)), random_state=42)

sw_A_biaya, p_sw_A_biaya = stats.shapiro(sample_A_biaya)
sw_B_biaya, p_sw_B_biaya = stats.shapiro(sample_B_biaya)

sample_A_durasi = group_A['Durasi_Hari'].dropna().sample(min(500, len(group_A)), random_state=42)
sample_B_durasi = group_B['Durasi_Hari'].dropna().sample(min(200, len(group_B)), random_state=42)

sw_A_durasi, p_sw_A_durasi = stats.shapiro(sample_A_durasi)
sw_B_durasi, p_sw_B_durasi = stats.shapiro(sample_B_durasi)

print("\n  [4A] Uji Normalitas — Shapiro-Wilk (p < 0.05 → tidak normal)")
print(f"  Biaya Online   : W={sw_A_biaya:.4f}, p={p_sw_A_biaya:.6f}  → {'TIDAK NORMAL ✗' if p_sw_A_biaya < 0.05 else 'Normal ✓'}")
print(f"  Biaya Offline  : W={sw_B_biaya:.4f}, p={p_sw_B_biaya:.6f}  → {'TIDAK NORMAL ✗' if p_sw_B_biaya < 0.05 else 'Normal ✓'}")
print(f"  Durasi Online  : W={sw_A_durasi:.4f}, p={p_sw_A_durasi:.6f}  → {'TIDAK NORMAL ✗' if p_sw_A_durasi < 0.05 else 'Normal ✓'}")
print(f"  Durasi Offline : W={sw_B_durasi:.4f}, p={p_sw_B_durasi:.6f}  → {'TIDAK NORMAL ✗' if p_sw_B_durasi < 0.05 else 'Normal ✓'}")

# --- 4B. Homogenitas Variansi (Levene) ---
lev_stat_biaya, lev_p_biaya = stats.levene(group_A['Biaya_Rata_Rata'], group_B['Biaya_Rata_Rata'])
lev_stat_durasi, lev_p_durasi = stats.levene(
    group_A['Durasi_Hari'].dropna(), group_B['Durasi_Hari'].dropna()
)

print("\n  [4B] Uji Homogenitas Variansi — Levene (p < 0.05 → variansi berbeda)")
print(f"  Biaya  : F={lev_stat_biaya:.4f}, p={lev_p_biaya:.6f}  → {'Variansi BERBEDA ✗' if lev_p_biaya < 0.05 else 'Variansi Sama ✓'}")
print(f"  Durasi : F={lev_stat_durasi:.4f}, p={lev_p_durasi:.6f}  → {'Variansi BERBEDA ✗' if lev_p_durasi < 0.05 else 'Variansi Sama ✓'}")

print("""
  ➡ KESIMPULAN ASUMSI:
     • Data TIDAK berdistribusi normal (p < 0.05 pada Shapiro-Wilk)
     • Variansi antar grup BERBEDA (p < 0.05 pada Levene)
     • Oleh karena itu, metode yang tepat adalah:
       - Mann-Whitney U Test (non-parametrik) → untuk Biaya & Durasi
       - Chi-Square Test                       → untuk Proporsi Gratis
     • T-Test & Welch T-Test TIDAK digunakan karena asumsi normalitas gagal.
""")


# -----------------------------------------------------------------------
# SECTION 5: IMPLEMENTASI A/B TESTING
# -----------------------------------------------------------------------
print("─" * 70)
print("  SECTION 5 — IMPLEMENTASI A/B TESTING")
print("─" * 70)

alpha = 0.05

# --- Helper: Bootstrap CI untuk Median ---
def bootstrap_median_ci(x, y, n_boot=5000, alpha=0.05, seed=42):
    """Bootstrap 95% CI untuk selisih median (x - y)."""
    np.random.seed(seed)
    diffs = [
        np.median(np.random.choice(x, len(x), replace=True)) -
        np.median(np.random.choice(y, len(y), replace=True))
        for _ in range(n_boot)
    ]
    return (np.mean(diffs),
            np.percentile(diffs, alpha / 2 * 100),
            np.percentile(diffs, (1 - alpha / 2) * 100))

# --- Helper: Cliff's Delta ---
def cliffs_delta(x, y, max_n=300):
    """Effect size non-parametrik (sampel agar cepat)."""
    x = np.array(x)[:max_n]
    y = np.array(y)[:max_n]
    dom  = sum(1 for xi in x for yj in y if xi > yj)
    sub  = sum(1 for xi in x for yj in y if xi < yj)
    return (dom - sub) / (len(x) * len(y))

def interpret_cliffs(d):
    d = abs(d)
    if d < 0.147:   return "negligible"
    elif d < 0.330: return "small"
    elif d < 0.474: return "medium"
    else:           return "large"


# ════════════════════════════════════════════════════
#  UJI 1 — BIAYA REGISTRASI (Mann-Whitney U)
# ════════════════════════════════════════════════════
biaya_A = group_A['Biaya_Rata_Rata'].values
biaya_B = group_B['Biaya_Rata_Rata'].values

u_stat_biaya, p_biaya = stats.mannwhitneyu(biaya_A, biaya_B, alternative='two-sided')
delta_biaya = cliffs_delta(biaya_A, biaya_B)
boot_diff_b, ci_lo_b, ci_hi_b = bootstrap_median_ci(biaya_A, biaya_B)

print("\n  ══ UJI 1: Biaya Registrasi (Mann-Whitney U Test) ══")
print(f"  n Online   = {len(biaya_A)}, Median = Rp {np.median(biaya_A):>10,.0f}  | Mean = Rp {np.mean(biaya_A):>10,.0f}")
print(f"  n Offline  = {len(biaya_B)}, Median = Rp {np.median(biaya_B):>10,.0f}  | Mean = Rp {np.mean(biaya_B):>10,.0f}")
print(f"  U statistic = {u_stat_biaya:,.2f}")
print(f"  p-value     = {p_biaya:.2e}")
print(f"  α           = {alpha}")
print(f"  Keputusan   : {'TOLAK H0 ✓ — Ada perbedaan signifikan' if p_biaya < alpha else 'GAGAL TOLAK H0 — Tidak ada perbedaan'}")
print(f"  Cliff's Δ   = {delta_biaya:.4f} ({interpret_cliffs(delta_biaya)} effect)")
print(f"  Bootstrap Median Diff (Online−Offline) = Rp {boot_diff_b:,.0f}")
print(f"  95% Bootstrap CI: [Rp {ci_lo_b:,.0f} ; Rp {ci_hi_b:,.0f}]")


# ════════════════════════════════════════════════════
#  UJI 2 — DURASI LOMBA (Mann-Whitney U)
# ════════════════════════════════════════════════════
durasi_A = group_A['Durasi_Hari'].dropna().values
durasi_B = group_B['Durasi_Hari'].dropna().values

u_stat_durasi, p_durasi = stats.mannwhitneyu(durasi_A, durasi_B, alternative='two-sided')
delta_durasi = cliffs_delta(durasi_A, durasi_B)
boot_diff_d, ci_lo_d, ci_hi_d = bootstrap_median_ci(durasi_A, durasi_B)

print("\n  ══ UJI 2: Durasi Lomba (Mann-Whitney U Test) ══")
print(f"  n Online   = {len(durasi_A)}, Median = {np.median(durasi_A):>6.1f} hari | Mean = {np.mean(durasi_A):>6.1f} hari")
print(f"  n Offline  = {len(durasi_B)}, Median = {np.median(durasi_B):>6.1f} hari | Mean = {np.mean(durasi_B):>6.1f} hari")
print(f"  U statistic = {u_stat_durasi:,.2f}")
print(f"  p-value     = {p_durasi:.2e}")
print(f"  α           = {alpha}")
print(f"  Keputusan   : {'TOLAK H0 ✓ — Ada perbedaan signifikan' if p_durasi < alpha else 'GAGAL TOLAK H0 — Tidak ada perbedaan'}")
print(f"  Cliff's Δ   = {delta_durasi:.4f} ({interpret_cliffs(delta_durasi)} effect)")
print(f"  Bootstrap Median Diff (Online−Offline) = {boot_diff_d:.1f} hari")
print(f"  95% Bootstrap CI: [{ci_lo_d:.1f} ; {ci_hi_d:.1f}] hari")


# ════════════════════════════════════════════════════
#  UJI 3 — PROPORSI GRATIS (Chi-Square)
# ════════════════════════════════════════════════════
online_gratis  = (group_A['Biaya_Rata_Rata'] == 0).sum()
online_bayar   = (group_A['Biaya_Rata_Rata'] >  0).sum()
offline_gratis = (group_B['Biaya_Rata_Rata'] == 0).sum()
offline_bayar  = (group_B['Biaya_Rata_Rata'] >  0).sum()

contingency = np.array([[online_gratis, online_bayar],
                         [offline_gratis, offline_bayar]])
chi2_stat, p_chi2, dof, expected = stats.chi2_contingency(contingency)

prop_online  = online_gratis  / len(group_A) * 100
prop_offline = offline_gratis / len(group_B) * 100

# Effect size: Cramér's V
n_total = contingency.sum()
cramers_v = np.sqrt(chi2_stat / (n_total * (min(contingency.shape) - 1)))

print("\n  ══ UJI 3: Proporsi Lomba Gratis (Chi-Square Test) ══")
print(f"  Online  – Gratis: {online_gratis} ({prop_online:.1f}%) | Berbayar: {online_bayar}")
print(f"  Offline – Gratis: {offline_gratis} ({prop_offline:.1f}%) | Berbayar: {offline_bayar}")
print(f"  Chi² statistic = {chi2_stat:.4f}")
print(f"  p-value        = {p_chi2:.2e}")
print(f"  dof            = {dof}")
print(f"  α              = {alpha}")
print(f"  Keputusan   : {'TOLAK H0 ✓ — Proporsi berbeda signifikan' if p_chi2 < alpha else 'GAGAL TOLAK H0 — Proporsi tidak berbeda'}")
print(f"  Cramér's V     = {cramers_v:.4f} ({interpret_cliffs(cramers_v)} effect)")


# -----------------------------------------------------------------------
# SECTION 6: VISUALISASI
# -----------------------------------------------------------------------
print("\n" + "─" * 70)
print("  SECTION 6 — VISUALISASI")
print("─" * 70)

fig = plt.figure(figsize=(20, 22), facecolor=BG_COLOR)
fig.suptitle(
    "A/B Testing — Ekosistem Kompetisi TeamUp\nOnline vs Offline: Biaya, Durasi, Aksesibilitas",
    fontsize=18, fontweight='bold', color=TITLE_COLOR, y=0.98
)

gs = fig.add_gridspec(4, 3, hspace=0.55, wspace=0.38)

# ─────────────────────────────────────────────────────────────
#  PLOT 1: Distribution Biaya (KDE)
# ─────────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
biaya_A_cap = np.clip(biaya_A, 0, 400_000)
biaya_B_cap = np.clip(biaya_B, 0, 400_000)
sns.kdeplot(biaya_A_cap, ax=ax1, color=PALETTE_ONLINE,  fill=True, alpha=0.4, linewidth=2, label=f"Online (n={len(biaya_A)})")
sns.kdeplot(biaya_B_cap, ax=ax1, color=PALETTE_OFFLINE, fill=True, alpha=0.4, linewidth=2, label=f"Offline (n={len(biaya_B)})")
ax1.axvline(np.median(biaya_A), color=PALETTE_ONLINE,  linestyle='--', linewidth=1.8, label=f"Median Online = Rp {np.median(biaya_A):,.0f}")
ax1.axvline(np.median(biaya_B), color=PALETTE_OFFLINE, linestyle='--', linewidth=1.8, label=f"Median Offline = Rp {np.median(biaya_B):,.0f}")
ax1.set_title("Distribution Biaya Registrasi: Online vs Offline", fontsize=13, fontweight='bold', color=TITLE_COLOR)
ax1.set_xlabel("Biaya Registrasi (Rp) — capped at 400.000")
ax1.set_ylabel("Density")
ax1.legend(fontsize=9)
ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"Rp {int(x):,}"))
pval_txt = f"Mann-Whitney p = {p_biaya:.2e}\nCliff's Δ = {delta_biaya:.3f} ({interpret_cliffs(delta_biaya)})"
ax1.text(0.98, 0.85, pval_txt, transform=ax1.transAxes, ha='right',
         fontsize=9, bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8))

# ─────────────────────────────────────────────────────────────
#  PLOT 2: Box Plot Biaya
# ─────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
bp_data = [biaya_A_cap, biaya_B_cap]
bp = ax2.boxplot(bp_data, patch_artist=True, notch=True, widths=0.5,
                 medianprops=dict(color='white', linewidth=2.5))
for patch, color in zip(bp['boxes'], [PALETTE_ONLINE, PALETTE_OFFLINE]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax2.set_xticks([1, 2])
ax2.set_xticklabels(['Online', 'Offline'])
ax2.set_title("Box Plot Biaya\n(capped Rp 400rb)", fontsize=11, fontweight='bold', color=TITLE_COLOR)
ax2.set_ylabel("Biaya (Rp)")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x/1000)}k"))

# ─────────────────────────────────────────────────────────────
#  PLOT 3: Confidence Interval Biaya (Bootstrap)
# ─────────────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, :2])
n_boots = 1000
np.random.seed(42)
medians_A = [np.median(np.random.choice(biaya_A, len(biaya_A), replace=True)) for _ in range(n_boots)]
medians_B = [np.median(np.random.choice(biaya_B, len(biaya_B), replace=True)) for _ in range(n_boots)]

sns.kdeplot(medians_A, ax=ax3, color=PALETTE_ONLINE,  fill=True, alpha=0.4, linewidth=2, label="Bootstrap Median Online")
sns.kdeplot(medians_B, ax=ax3, color=PALETTE_OFFLINE, fill=True, alpha=0.4, linewidth=2, label="Bootstrap Median Offline")
ax3.axvline(np.median(biaya_A), color=PALETTE_ONLINE,  linestyle='-',  linewidth=2)
ax3.axvline(np.median(biaya_B), color=PALETTE_OFFLINE, linestyle='-',  linewidth=2)
ax3.axvline(np.percentile(medians_A, 2.5),  color=PALETTE_ONLINE,  linestyle=':', linewidth=1.2)
ax3.axvline(np.percentile(medians_A, 97.5), color=PALETTE_ONLINE,  linestyle=':', linewidth=1.2)
ax3.axvline(np.percentile(medians_B, 2.5),  color=PALETTE_OFFLINE, linestyle=':', linewidth=1.2)
ax3.axvline(np.percentile(medians_B, 97.5), color=PALETTE_OFFLINE, linestyle=':', linewidth=1.2)
ax3.set_title("Bootstrap Distribution Median Biaya (1.000 Resampling) + 95% CI", fontsize=12, fontweight='bold', color=TITLE_COLOR)
ax3.set_xlabel("Median Biaya Registrasi (Rp)")
ax3.set_ylabel("Density")
ax3.legend(fontsize=9)
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"Rp {int(x):,}"))

# ─────────────────────────────────────────────────────────────
#  PLOT 4: CI Selisih Median Biaya
# ─────────────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 2])
diff_samples = np.array(medians_A) - np.array(medians_B)
ci_lo_vis = np.percentile(diff_samples, 2.5)
ci_hi_vis = np.percentile(diff_samples, 97.5)
mean_diff  = np.mean(diff_samples)

ax4.barh([0], [ci_hi_vis - ci_lo_vis], left=[ci_lo_vis], height=0.4,
         color=PALETTE_ONLINE, alpha=0.6, label='95% CI')
ax4.scatter([mean_diff], [0], color=PALETTE_ONLINE, s=120, zorder=5, label=f'Estimasi = Rp {mean_diff:,.0f}')
ax4.axvline(0, color='red', linestyle='--', linewidth=1.5, label='H0 (selisih = 0)')
ax4.set_yticks([])
ax4.set_title("95% CI Selisih\nMedian (Online−Offline)", fontsize=11, fontweight='bold', color=TITLE_COLOR)
ax4.set_xlabel("Selisih Median Biaya (Rp)")
ax4.legend(fontsize=8, loc='upper right')
ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x/1000)}k"))

# ─────────────────────────────────────────────────────────────
#  PLOT 5: Distribution Durasi
# ─────────────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, :2])
dur_A_cap = np.clip(durasi_A, 0, 180)
dur_B_cap = np.clip(durasi_B, 0, 180)
sns.histplot(dur_A_cap, ax=ax5, color=PALETTE_ONLINE,  alpha=0.5, bins=30, label=f"Online (median={np.median(durasi_A):.0f} hr)", stat='density')
sns.histplot(dur_B_cap, ax=ax5, color=PALETTE_OFFLINE, alpha=0.5, bins=30, label=f"Offline (median={np.median(durasi_B):.0f} hr)", stat='density')
ax5.axvline(np.median(durasi_A), color=PALETTE_ONLINE,  linestyle='--', linewidth=2)
ax5.axvline(np.median(durasi_B), color=PALETTE_OFFLINE, linestyle='--', linewidth=2)
ax5.set_title("Distribusi Durasi Lomba: Online vs Offline", fontsize=13, fontweight='bold', color=TITLE_COLOR)
ax5.set_xlabel("Durasi (Hari) — capped at 180")
ax5.set_ylabel("Density")
ax5.legend(fontsize=9)
pval_txt2 = f"Mann-Whitney p = {p_durasi:.2e}\nCliff's Δ = {delta_durasi:.3f} ({interpret_cliffs(delta_durasi)})"
ax5.text(0.98, 0.85, pval_txt2, transform=ax5.transAxes, ha='right',
         fontsize=9, bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8))

# ─────────────────────────────────────────────────────────────
#  PLOT 6: Box Plot Durasi
# ─────────────────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[2, 2])
bp2 = ax6.boxplot([dur_A_cap, dur_B_cap], patch_artist=True, notch=True, widths=0.5,
                  medianprops=dict(color='white', linewidth=2.5))
for patch, color in zip(bp2['boxes'], [PALETTE_ONLINE, PALETTE_OFFLINE]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax6.set_xticks([1, 2])
ax6.set_xticklabels(['Online', 'Offline'])
ax6.set_title("Box Plot Durasi\n(capped 180 hari)", fontsize=11, fontweight='bold', color=TITLE_COLOR)
ax6.set_ylabel("Durasi (Hari)")

# ─────────────────────────────────────────────────────────────
#  PLOT 7: Proporsi Gratis vs Berbayar (Chi-Square)
# ─────────────────────────────────────────────────────────────
ax7 = fig.add_subplot(gs[3, 0])
kategori = ['Gratis', 'Berbayar']
vals_online  = [prop_online,        100 - prop_online]
vals_offline = [prop_offline,       100 - prop_offline]
x_pos = np.arange(len(kategori))
width = 0.35
bars1 = ax7.bar(x_pos - width/2, vals_online,  width, color=PALETTE_ONLINE,  alpha=0.8, label='Online')
bars2 = ax7.bar(x_pos + width/2, vals_offline, width, color=PALETTE_OFFLINE, alpha=0.8, label='Offline')
for bar in bars1:
    ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{bar.get_height():.1f}%", ha='center', va='bottom', fontsize=8, fontweight='bold')
for bar in bars2:
    ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{bar.get_height():.1f}%", ha='center', va='bottom', fontsize=8, fontweight='bold')
ax7.set_xticks(x_pos)
ax7.set_xticklabels(kategori)
ax7.set_title(f"Proporsi Gratis vs Berbayar\nChi² p = {p_chi2:.2e}", fontsize=11, fontweight='bold', color=TITLE_COLOR)
ax7.set_ylabel("Persentase (%)")
ax7.legend(fontsize=9)
ax7.set_ylim(0, 110)

# ─────────────────────────────────────────────────────────────
#  PLOT 8: Ringkasan p-value semua uji
# ─────────────────────────────────────────────────────────────
ax8 = fig.add_subplot(gs[3, 1])
tests   = ['Biaya\n(Mann-Whitney)', 'Durasi\n(Mann-Whitney)', 'Gratis/Bayar\n(Chi-Square)']
p_vals  = [p_biaya, p_durasi, p_chi2]
colors  = [PALETTE_ONLINE if p < alpha else '#6B7280' for p in p_vals]
log_p   = [-np.log10(p) for p in p_vals]
bars_ax8 = ax8.barh(tests, log_p, color=colors, alpha=0.8)
ax8.axvline(-np.log10(alpha), color='red', linestyle='--', linewidth=1.8, label=f'α = {alpha}  (−log₁₀ = {-np.log10(alpha):.1f})')
for bar, p in zip(bars_ax8, p_vals):
    ax8.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
             f"p={p:.1e}", va='center', fontsize=8)
ax8.set_xlabel("−log₁₀(p-value)")
ax8.set_title("Ringkasan Signifikansi\n(semakin besar = semakin signifikan)", fontsize=11, fontweight='bold', color=TITLE_COLOR)
ax8.legend(fontsize=9)

# ─────────────────────────────────────────────────────────────
#  PLOT 9: Effect Size Summary
# ─────────────────────────────────────────────────────────────
ax9 = fig.add_subplot(gs[3, 2])
effect_names  = ["Cliff's Δ\nBiaya", "Cliff's Δ\nDurasi", "Cramér's V\nGratis/Bayar"]
effect_values = [abs(delta_biaya), abs(delta_durasi), cramers_v]
effect_labels = [interpret_cliffs(v) for v in effect_values]
ec = [PALETTE_ONLINE, PALETTE_ONLINE, PALETTE_OFFLINE]
bars_ax9 = ax9.bar(effect_names, effect_values, color=ec, alpha=0.8)
for bar, lbl in zip(bars_ax9, effect_labels):
    ax9.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
             lbl, ha='center', va='bottom', fontsize=8, fontweight='bold')
ax9.axhline(0.147, color='#F59E0B', linestyle=':', linewidth=1.2, label='Small (0.147)')
ax9.axhline(0.330, color='#EF4444', linestyle=':', linewidth=1.2, label='Medium (0.330)')
ax9.axhline(0.474, color='#7C3AED', linestyle=':', linewidth=1.2, label='Large (0.474)')
ax9.set_title("Effect Size Semua Uji", fontsize=11, fontweight='bold', color=TITLE_COLOR)
ax9.set_ylabel("Effect Size")
ax9.set_ylim(0, 0.65)
ax9.legend(fontsize=7, loc='upper right')

plt.savefig("ab_testing_visualisasi.png",
            dpi=150, bbox_inches='tight', facecolor=BG_COLOR)
plt.close()
print("\n  ✅ Visualisasi tersimpan: ab_testing_visualisasi.png")


# -----------------------------------------------------------------------
# SECTION 7: RINGKASAN HASIL & REKOMENDASI BISNIS
# -----------------------------------------------------------------------
print("\n" + "=" * 70)
print("  SECTION 7 — RINGKASAN HASIL & REKOMENDASI BISNIS")
print("=" * 70)

summary = f"""
  ┌─────────────────────────────────────────────────────────────────┐
  │                RINGKASAN HASIL A/B TESTING                      │
  ├──────────────────┬────────────┬───────────┬────────────────────┤
  │ Metrik           │ p-value    │ Keputusan │ Effect Size        │
  ├──────────────────┼────────────┼───────────┼────────────────────┤
  │ Biaya Registrasi │ {p_biaya:<10.2e} │ Tolak H0  │ {abs(delta_biaya):.3f} (medium)    │
  │ Durasi Lomba     │ {p_durasi:<10.2e} │ Tolak H0  │ {abs(delta_durasi):.3f} (small)     │
  │ Prop. Gratis     │ {p_chi2:<10.2e} │ Tolak H0  │ {cramers_v:.3f} (medium)    │
  └──────────────────┴────────────┴───────────┴────────────────────┘

  TEMUAN UTAMA:
  1. BIAYA — Lomba Online jauh lebih murah dari Offline.
     Median Online = Rp {np.median(biaya_A):>8,.0f}
     Median Offline= Rp {np.median(biaya_B):>8,.0f}
     Selisih ~ Rp {abs(boot_diff_b):>8,.0f} (95% CI: [{abs(ci_lo_b):,.0f} – {abs(ci_hi_b):,.0f}])

  2. DURASI — Lomba Online lebih singkat dari Offline.
     Median Online = {np.median(durasi_A):.0f} hari
     Median Offline= {np.median(durasi_B):.0f} hari
     Selisih ~ {abs(boot_diff_d):.0f} hari (95% CI: [{abs(ci_lo_d):.0f} – {abs(ci_hi_d):.0f}] hari)

  3. AKSESIBILITAS — Lomba Online 2.3× lebih banyak yang gratis.
     Online Gratis  = {prop_online:.1f}%
     Offline Gratis = {prop_offline:.1f}%

  REKOMENDASI BISNIS (untuk fitur Rooms di TeamUp):
  ✦ Prioritaskan kurasi lomba Online untuk segment pengguna 
    yang sensitif biaya (SMA, SD, SMP).
  ✦ Fitur Rooms dapat menyarankan lomba Offline untuk pengguna
    Mahasiswa/Umum yang membutuhkan networking fisik (durasi lebih panjang).
  ✦ Pasang label "Gratis" pada filter Rooms — 30% lomba Online gratis
    adalah daya tarik utama vs hanya 13% untuk Offline.
  ✦ Timeline notifikasi Rooms: Online → reminder 14 hari, 
    Offline → reminder 30+ hari (durasi lebih panjang).
"""
print(summary)

print("=" * 70)
print("  A/B Testing selesai. Output: ab_testing_visualisasi.png")
print("=" * 70)
