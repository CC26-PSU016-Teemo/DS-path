import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="TeamUp Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. CUSTOM CSS & HEADER
# ==========================================
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: 800; color: #1E3A8A; margin-bottom: 5px; font-family: 'Helvetica Neue', sans-serif; }
    .subtitle { font-size: 15px; color: #4B5563; margin-bottom: 30px; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #1E40AF; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 Dashboard Analisis Ekosistem Kompetisi — TeamUp</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Visualisasi interaktif berbasis data untuk optimasi fitur Rooms, segmentasi user, pemetaan harga pasar, dan durasi kompetisi.</div>', unsafe_allow_html=True)

# ==========================================
# 2. LOAD DATA & AUTO-PREPROCESSING
# ==========================================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data_clean.csv')
    df = pd.read_csv(file_path)
    
    if 'Tanggal_Mulai' in df.columns:
        df['Tanggal_Mulai'] = pd.to_datetime(df['Tanggal_Mulai'], errors='coerce')
        df['Bulan_Num'] = df['Tanggal_Mulai'].dt.month
        nama_bulan = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun', 7:'Jul', 8:'Agu', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'}
        df['Bulan'] = df['Bulan_Num'].map(nama_bulan)
        
    if 'Tanggal_Selesai' in df.columns:
        df['Tanggal_Selesai'] = pd.to_datetime(df['Tanggal_Selesai'], errors='coerce')
        df['Durasi_Hari'] = (df['Tanggal_Selesai'] - df['Tanggal_Mulai']).dt.days
        df['Durasi_Hari'] = df['Durasi_Hari'].apply(lambda x: x if x >= 0 else None)
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error("⚠️ File 'data_clean.csv' tidak ditemukan atau gagal dimuat. Letakkan file CSV di folder yang sama dengan dashboard.py.")
    st.stop()

# ==========================================
# 3. ADVANCED SIDEBAR FILTER INTERAKTIF
# ==========================================
st.sidebar.header("🎛️ Filter Panel Utama")

if st.sidebar.button("🔄 Reset Semua Filter"):
    st.rerun()

st.sidebar.markdown("---")

# ---------------------------------------------------------
# A. KELOMPOK FILTER TAB 1 (Demografi & Kategori)
# ---------------------------------------------------------
st.sidebar.markdown("### 👥 1. Demografi & Kategori")

df_jenjang_temp = df.copy()
df_jenjang_temp['Jenjang'] = df_jenjang_temp['Jenjang'].fillna("").astype(str).str.split(',')
df_jenjang_temp = df_jenjang_temp.explode('Jenjang')
df_jenjang_temp['Jenjang'] = df_jenjang_temp['Jenjang'].str.strip()
opsi_jenjang = [j for j in df_jenjang_temp['Jenjang'].unique() if j and j != 'nan']

df_kat_temp = df.copy()
df_kat_temp['Tema/Kategori'] = df_kat_temp['Tema/Kategori'].fillna("").astype(str).str.split(',')
df_kat_temp = df_kat_temp.explode('Tema/Kategori')
df_kat_temp['Tema/Kategori'] = df_kat_temp['Tema/Kategori'].str.strip()
opsi_kategori = [k for k in df_kat_temp['Tema/Kategori'].unique() if k and k not in ['nan', '', '~Lainnya']]

pilihan_jenjang = st.sidebar.multiselect("Target Jenjang Pendidikan:", options=opsi_jenjang, placeholder="Pilih Jenjang...")
pilihan_kategori = st.sidebar.multiselect("Rumpun Kategori Lomba:", options=opsi_kategori, placeholder="Pilih Kategori...")

st.sidebar.markdown("---")

# ---------------------------------------------------------
# B. KELOMPOK FILTER TAB 2 (Momentum & Siklus)
# ---------------------------------------------------------
st.sidebar.markdown("### 🚀 2. Momentum & Durasi")

opsi_bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
pilihan_bulan = st.sidebar.multiselect("Bulan Pelaksanaan:", options=opsi_bulan, placeholder="Pilih Bulan...")

min_durasi = 0
max_durasi = int(df['Durasi_Hari'].max()) if 'Durasi_Hari' in df.columns and pd.notna(df['Durasi_Hari'].max()) else 365
rentang_durasi = st.sidebar.slider("⏳ Rentang Durasi (Hari):", min_value=min_durasi, max_value=max_durasi, value=(min_durasi, max_durasi))

st.sidebar.markdown("---")

# ---------------------------------------------------------
# C. KELOMPOK FILTER TAB 3 (Finansial & Akses)
# ---------------------------------------------------------
st.sidebar.markdown("### 📊 3. Finansial & Aksesibilitas")

st.sidebar.markdown("**💰 Rentang Biaya Masuk (Rp)**")
min_biaya_data = 0
max_biaya_data = int(df['Biaya_Rata_Rata'].max()) if 'Biaya_Rata_Rata' in df.columns else 1000000

col1_sidebar, col2_sidebar = st.sidebar.columns(2)
with col1_sidebar:
    input_min_biaya = st.number_input("Minimal", min_value=min_biaya_data, max_value=max_biaya_data, value=min_biaya_data, step=5000)
with col2_sidebar:
    input_max_biaya = st.number_input("Maksimal", min_value=min_biaya_data, max_value=max_biaya_data, value=max_biaya_data, step=5000)

opsi_tipe = []
if 'Tipe (Online/Offline)' in df.columns:
    opsi_tipe = [t for t in df['Tipe (Online/Offline)'].dropna().unique()]
pilihan_tipe = st.sidebar.multiselect("Metode Pelaksanaan:", options=opsi_tipe, placeholder="Pilih Metode...")

if input_min_biaya > input_max_biaya:
    st.sidebar.error("⚠️ Nilai minimal tidak boleh melebihi maksimal.")


# ==========================================
# --- PROSES LOGIKA PENGGABUNGAN FILTER ---
# ==========================================
df_filtered = df.copy()

# Filter Tab 1
if pilihan_jenjang:
    pattern_j = '|'.join(pilihan_jenjang)
    df_filtered = df_filtered[df_filtered['Jenjang'].str.contains(pattern_j, na=False, regex=True)]

if pilihan_kategori:
    pattern_k = '|'.join(pilihan_kategori)
    df_filtered = df_filtered[df_filtered['Tema/Kategori'].str.contains(pattern_k, na=False, regex=True)]

# Filter Tab 2
if pilihan_bulan:
    df_filtered = df_filtered[df_filtered['Bulan'].isin(pilihan_bulan)]

if 'Durasi_Hari' in df_filtered.columns:
    df_filtered = df_filtered[(df_filtered['Durasi_Hari'] >= rentang_durasi[0]) & (df_filtered['Durasi_Hari'] <= rentang_durasi[1])]

# Filter Tab 3
if 'Biaya_Rata_Rata' in df_filtered.columns:
    df_filtered = df_filtered[(df_filtered['Biaya_Rata_Rata'] >= input_min_biaya) & (df_filtered['Biaya_Rata_Rata'] <= input_max_biaya)]

if pilihan_tipe:
    df_filtered = df_filtered[df_filtered['Tipe (Online/Offline)'].isin(pilihan_tipe)]


# ==========================================
# 4. HIGHLIGHTS METRICS (KPI CARDS)
# ==========================================
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Event Terfilter", f"{len(df_filtered)} / {len(df)} Lomba")
with kpi2:
    if 'Biaya_Rata_Rata' in df_filtered.columns and len(df_filtered) > 0:
        rata_biaya = df_filtered['Biaya_Rata_Rata'].mean()
        st.metric("Rata-Rata Biaya", f"Rp {rata_biaya:,.0f}")
    else:
        st.metric("Rata-Rata Biaya", "Rp 0")
with kpi3:
    if 'Biaya_Rata_Rata' in df_filtered.columns and len(df_filtered) > 0:
        persen_gratis = (df_filtered['Biaya_Rata_Rata'] == 0).sum() / len(df_filtered) * 100
        st.metric("Akses Lomba Gratis", f"{persen_gratis:.1f}%")
    else:
        st.metric("Akses Lomba Gratis", "0.0%")
with kpi4:
    if 'Durasi_Hari' in df_filtered.columns and len(df_filtered) > 0:
        rata_durasi = df_filtered['Durasi_Hari'].mean()
        st.metric("Rata-Rata Siklus Event", f"{rata_durasi:.0f} Hari")
    else:
        st.metric("Rata-Rata Siklus Event", "-")

st.markdown("---")


# ==========================================
# 5. NAVIGASI TABS VISUALISASI MODERN
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "👥 Demografi & Kategori", 
    "🚀 Analisis Momentum (Rooms)", 
    "📊 Pemetaan Harga & Aksesibilitas"
])

# TAB 1: DEMOGRAFI & KATEGORI
with tab1:
    st.subheader("Karakteristik Segmentasi dan Preferensi Kategori Lomba")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### **Top Target Distribusi Pendidikan**")
        if len(df_filtered) > 0:
            df_j_plot = df_filtered.copy()
            df_j_plot['Jenjang'] = df_j_plot['Jenjang'].fillna("").astype(str).str.split(',')
            df_j_plot = df_j_plot.explode('Jenjang')
            df_j_plot['Jenjang'] = df_j_plot['Jenjang'].str.strip()
            df_j_plot = df_j_plot[df_j_plot['Jenjang'] != '']
            
            data_j = df_j_plot['Jenjang'].value_counts().reset_index()
            data_j.columns = ['Jenjang Pendidikan', 'Jumlah Event']
            
            fig1 = px.bar(data_j.head(6), x='Jumlah Event', y='Jenjang Pendidikan', orientation='h', color='Jumlah Event', color_continuous_scale='Blugrn', text_auto=True)
            fig1.update_layout(showlegend=False, height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Tidak ada data untuk filter saat ini.")
        
    with col2:
        st.markdown("##### **Top Kategori Lomba Terbanyak**")
        if 'Tema/Kategori' in df_filtered.columns and len(df_filtered) > 0:
            df_k_plot = df_filtered.copy()
            df_k_plot['Tema/Kategori'] = df_k_plot['Tema/Kategori'].fillna("").astype(str).str.split(',')
            df_k_plot = df_k_plot.explode('Tema/Kategori')
            df_k_plot['Tema/Kategori'] = df_k_plot['Tema/Kategori'].str.strip()
            df_k_plot = df_k_plot[~df_k_plot['Tema/Kategori'].isin(['', 'nan', '~Lainnya'])]
            
            data_k = df_k_plot['Tema/Kategori'].value_counts().reset_index()
            data_k.columns = ['Kategori', 'Jumlah']
            
            fig_k = px.bar(data_k.head(10), x='Kategori', y='Jumlah', color='Jumlah', color_continuous_scale='Sunset', text_auto=True)
            fig_k.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_k, use_container_width=True)
        else:
            st.info("Tidak ada data untuk filter saat ini.")

    st.success("**💡 Insight Produk TeamUp:** Segmentasi **Mahasiswa** dan ranah kompetisi **Desain/Bisnis/Karya Tulis** mendominasi pasar. Kehadiran filter dinamis ini memvalidasi kebutuhan fitur koordinasi tim jarak jauh di fitur 'Rooms' TeamUp guna mendukung pengerjaan karya kolaboratif secara real-time.")

# TAB 2: ANALISIS MOMENTUM & LIFECYCLE
with tab2:
    st.subheader("Momentum Kompetisi & Siklus Keterikatan (Retention) Pengguna")
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("##### **Tren Bulan Pembukaan Kompetisi Baru**")
        if 'Bulan' in df_filtered.columns and len(df_filtered) > 0:
            urutan_bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
            df_bulan = df_filtered.groupby('Bulan').size().reindex(urutan_bulan, fill_value=0).reset_index()
            df_bulan.columns = ['Bulan', 'Jumlah Kompetisi Baru']
            
            fig3 = px.area(df_bulan, x='Bulan', y='Jumlah Kompetisi Baru', markers=True, color_discrete_sequence=['#DC2626'])
            fig3.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Tidak ada data untuk tren bulanan.")
            
    with col4:
        st.markdown("##### **Distribusi Durasi Kompetisi (Preparation to End)**")
        if 'Durasi_Hari' in df_filtered.columns and len(df_filtered) > 0:
            fig_dur = px.histogram(df_filtered, x='Durasi_Hari', nbins=20, color_discrete_sequence=['#8B5CF6'])
            fig_dur.update_layout(xaxis_title="Durasi (Hari)", yaxis_title="Frekuensi", height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_dur, use_container_width=True)
        else:
            st.info("Data durasi tidak tersedia untuk filter saat ini.")

    st.info("**🎯 Insight Momentum & Retensi:** Siklus hidup kompetisi rata-rata bergerak di kisaran 25–40 hari. Agar kelompok pendaftar tidak keluar dari platform TeamUp pasca menemukan rekan di 'Rooms', platform wajib menyediakan tools pelacak progress (timeline tracker) terintegrasi selama masa persiapan lomba tersebut berlangsung.")

# TAB 3: PEMETAAN HARGA & AKSESIBILITAS
with tab3:
    st.subheader("Analisis Finansial & Aksesibilitas Lomba")
    col5, col6 = st.columns([1, 1.5])
    
    with col5:
        st.markdown("##### **Metode Pelaksanaan Kompetisi**")
        if 'Tipe (Online/Offline)' in df_filtered.columns and len(df_filtered) > 0:
            data_t = df_filtered['Tipe (Online/Offline)'].value_counts().reset_index()
            data_t.columns = ['Tipe Pelaksanaan', 'Total']
            
            fig2 = px.pie(data_t, names='Tipe Pelaksanaan', values='Total', hole=0.45, color_discrete_sequence=['#1E40AF', '#3B82F6', '#93C5FD'])
            fig2.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Tidak ada data pelaksanaan.")
            
    with col6:
        st.markdown("##### **Sebaran Biaya Pendaftaran Berdasarkan Kategori**")
        if 'Tema/Kategori' in df_filtered.columns and 'Biaya_Rata_Rata' in df_filtered.columns and len(df_filtered) > 0:
            df_box_plot = df_filtered.copy()
            df_box_plot['Tema/Kategori'] = df_box_plot['Tema/Kategori'].fillna("").astype(str).str.split(',')
            df_box_plot = df_box_plot.explode('Tema/Kategori')
            df_box_plot['Tema/Kategori'] = df_box_plot['Tema/Kategori'].str.strip()
            df_box_plot = df_box_plot[~df_box_plot['Tema/Kategori'].isin(['', 'nan', '~Lainnya'])]
            
            top_categories = df_box_plot['Tema/Kategori'].value_counts().head(8).index
            df_box_plot = df_box_plot[df_box_plot['Tema/Kategori'].isin(top_categories)]
            
            fig4 = px.box(df_box_plot, x='Biaya_Rata_Rata', y='Tema/Kategori', color='Tema/Kategori', labels={'Biaya_Rata_Rata': 'Biaya (Rp)', 'Tema/Kategori': ''})
            fig4.update_layout(showlegend=False, height=400, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Tidak ada data finansial yang dapat dimuat.")

    st.warning("**🛠️ Implementasi Arsitektur Machine Learning:** Rentang biaya dan metode pelaksanaan (Online/Offline) berkolerasi dengan preferensi daya beli pengguna. Pola segmentasi dari kombinasi filter biaya dan tipe lomba ini sangat valid dikembangkan sebagai matriks bobot (*feature scaling*) dalam algoritma *Collaborative Filtering* pencarian tim TeamUp.")