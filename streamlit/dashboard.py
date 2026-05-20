import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Teemo Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: 800; color: #1E3A8A; margin-bottom: 5px; font-family: 'Helvetica Neue', sans-serif; }
    .subtitle { font-size: 15px; color: #4B5563; margin-bottom: 30px; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #1E40AF; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📈 Dashboard Analisis Ekosistem Kompetisi — Teemo</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Visualisasi interaktif berbasis data untuk optimasi fitur Rooms, segmentasi user, dan pemetaan harga pasar.</div>', unsafe_allow_html=True)

# 2. LOAD DATA & AUTO-PREPROCESSING
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'data_clean.csv')
    df = pd.read_csv(file_path)
    
    # Konversi tanggal dan ekstraksi bulan ke nama teks short-month
    if 'Tanggal_Mulai' in df.columns:
        df['Tanggal_Mulai'] = pd.to_datetime(df['Tanggal_Mulai'], errors='coerce')
        df['Bulan_Num'] = df['Tanggal_Mulai'].dt.month
        # Mapping angka ke nama bulan
        nama_bulan = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'Mei', 6:'Jun', 7:'Jul', 8:'Agu', 9:'Sep', 10:'Okt', 11:'Nov', 12:'Des'}
        df['Bulan'] = df['Bulan_Num'].map(nama_bulan)
        
    return df

try:
    df = load_data()
except Exception as e:
    st.error("⚠️ File 'data_clean.csv' tidak ditemukan atau gagal dimuat. Letakkan file CSV di folder yang sama dengan dashboard.py.")
    st.stop()

# 3. SIDEBAR FILTER INTERAKTIF
st.sidebar.header("🎛️ Filter Panel")

# Proses pemisahan jenjang jika ada koma (e.g. "Mahasiswa, Umum")
df_jenjang_clean = df.copy()
df_jenjang_clean['Jenjang'] = df_jenjang_clean['Jenjang'].str.split(', ')
df_jenjang_exploded = df_jenjang_clean.explode('Jenjang')

opsi_jenjang = df_jenjang_exploded['Jenjang'].dropna().unique()
pilihan_jenjang = st.sidebar.multiselect("Target Jenjang Pendidikan:", options=opsi_jenjang, default=opsi_jenjang)

# Filter Data Utama Berdasarkan Pilihan Sidebar
if pilihan_jenjang:
    # Memastikan baris yang mengandung salah satu pilihan filter tetap lolos
    pattern = '|'.join(pilihan_jenjang)
    df_filtered = df[df['Jenjang'].str.contains(pattern, na=False, regex=True)]
else:
    df_filtered = df.copy()

# 4. HIGHLIGHTS METRICS (KPI CARDS)
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("Total Event Teranalisis", f"{len(df_filtered)} Kompetisi")
with kpi2:
    if 'Biaya_Rata_Rata' in df_filtered.columns:
        rata_biaya = df_filtered['Biaya_Rata_Rata'].mean()
        st.metric("Rata-Rata Biaya Masuk", f"Rp {rata_biaya:,.0f}")
with kpi3:
    if 'Tipe (Online/Offline)' in df_filtered.columns:
        total_online = df_filtered['Tipe (Online/Offline)'].str.contains('Online', na=False).sum()
        persen_online = (total_online / len(df_filtered)) * 100 if len(df_filtered) > 0 else 0
        st.metric("Akses Online/Hybrid", f"{persen_online:.1f}%")

st.markdown("---")

# 5. NAVIGASI TABS VISUALISASI MODERN
tab1, tab2, tab3 = st.tabs([
    "👥 Pola Pasar & Segmentasi", 
    "🚀 Strategi Kampanye 'Rooms'", 
    "📊 Pemetaan Kategori & Finansial"
])

# TAB 1: POLA PASAR & SEGMENTASI
with tab1:
    st.subheader("Analisis Karakteristik dan Segmentasi Target Pasar")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### **Top Target Distribusi Pendidikan**")
        # Menggunakan data exploded agar hitungan per kriteria akurat
        df_j_filtered = df_filtered.copy()
        df_j_filtered['Jenjang'] = df_j_filtered['Jenjang'].str.split(', ')
        df_j_exploded = df_j_filtered.explode('Jenjang')
        data_j = df_j_exploded['Jenjang'].value_counts().reset_index()
        data_j.columns = ['Jenjang Pendidikan', 'Jumlah Event']
        
        fig1 = px.bar(
            data_j.head(5), x='Jumlah Event', y='Jenjang Pendidikan', orientation='h',
            color='Jumlah Event', color_continuous_scale='Blugrn',
            text_auto=True
        )
        fig1.update_layout(showlegend=False, height=350, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.markdown("##### **Metode Pelaksanaan Kompetisi (Donut Chart)**")
        if 'Tipe (Online/Offline)' in df_filtered.columns:
            data_t = df_filtered['Tipe (Online/Offline)'].value_counts().reset_index()
            data_t.columns = ['Tipe Pelaksanaan', 'Total']
            
            fig2 = px.pie(
                data_t, names='Tipe Pelaksanaan', values='Total', hole=0.45,
                color_discrete_sequence=['#1E40AF', '#3B82F6', '#F59E0B']
            )
            fig2.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)

    st.success("**💡 Kesimpulan Target Pasar:** Mayoritas ekosistem kompetisi didominasi kuat oleh segmen **Mahasiswa** dan **SMA/Sederajat**. Karena aksesibilitas pendaftaran didominasi metode digital (Online & Hybrid), disarankan desain antarmuka Teemo menonjolkan fitur koordinasi tim jarak jauh langsung di halaman utama.")

# TAB 2: STRATEGI KAMPANYE FITUR 'ROOMS'
with tab2:
    st.subheader("Prediksi Siklus Waktu Lonjakan Urgensi Partner Tim (Peak Season)")
    
    if 'Bulan' in df_filtered.columns:
        # Mengelompokkan berdasarkan bulan dan mengurutkan secara kronologis (Jan-Des)
        urutan_bulan = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
        df_bulan = df_filtered.groupby('Bulan').size().reindex(urutan_bulan, fill_value=0).reset_index()
        df_bulan.columns = ['Bulan', 'Jumlah Kompetisi Baru']
        
        fig3 = px.area(
            df_bulan, x='Bulan', y='Jumlah Kompetisi Baru', markers=True,
            color_discrete_sequence=['#DC2626']
        )
        fig3.update_layout(
            xaxis_title="Periode Bulan", yaxis_title="Jumlah Acara Baru Dimulai",
            height=380, margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        fig3.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E7EB')
        fig3.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E7EB')
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("Kolom Tanggal_Mulai tidak valid untuk memproses konversi tren bulanan.")

    st.info("**🎯 Strategi Go-To-Market Fitur Rooms:** Grafik tren menunjukkan pembukaan kompetisi baru melonjak drastis di bulan **Maret** dan **April**. Mengingat pembentukan tim memerlukan waktu diskusi (pra-registrasi), kampanye pemasaran fitur **Rooms** sebaiknya diledakkan pada **Januari dan Februari** untuk mencuri start momentum urgensi user.")

# TAB 3: PEMETAAN KATEGORI & FINANSIAL
with tab3:
    st.subheader("Sebaran Finansial Daya Beli Berdasarkan Rumpun Kategori")
    
    if 'Tema/Kategori' in df_filtered.columns and 'Biaya_Rata_Rata' in df_filtered.columns:
        # Pisahkan kategori majemuk agar rapi (e.g. "Musik, Seni" -> dihitung di masing-masing)
        df_c = df_filtered.copy()
        df_c['Tema/Kategori'] = df_c['Tema/Kategori'].str.split(', ')
        df_c_exploded = df_c.explode('Tema/Kategori')
        
        # Ambil Top 10 Kategori Terbanyak untuk Boxplot yang bersih
        top_categories = df_c_exploded['Tema/Kategori'].value_counts().head(10).index
        df_boxplot = df_c_exploded[df_c_exploded['Tema/Kategori'].isin(top_categories)]
        
        fig4 = px.box(
            df_boxplot, x='Biaya_Rata_Rata', y='Tema/Kategori',
            color='Tema/Kategori', color_discrete_sequence=px.colors.qualitative.Safe,
            labels={'Biaya_Rata_Rata': 'Biaya Pendaftaran (Rp)', 'Tema/Kategori': 'Rumpun Kategori'}
        )
        fig4.update_layout(showlegend=False, height=450, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig4.update_xaxes(showgrid=True, gridcolor='#E5E7EB')
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("Data finansial atau rumpun kategori tidak lengkap.")
        
    st.warning("**🛠️ Implementasi ke Arsitektur Machine Learning:** Variasi sebaran harga pada boxplot di atas menunjukkan perbedaan signifikan terhadap daya beli (*purchasing power*) antar domain bidang. Matriks rentang harga per kategori ini sangat valid diaplikasikan sebagai bobot preferensi ekonomi dalam algoritma rekomendasi rekan satu tim (*Collaborative Filtering*).")