## 🎯 Latar Belakang Masalah

Dataset ini dibuat oleh tim Data Science untuk mengatasi anomali kritis pada model rekomendasi Two-Tower TensorFlow milik tim AI Engineering. Sebelumnya, tim AI membuat data pelatihan dengan cara mengambil data lomba (item), menyuntikkan sedikit *noise*, lalu mengasumsikannya sebagai data preferensi user.

Akibatnya, model mengalami kegagalan generalisasi dan hanya belajar bahwa **"vektor yang mirip dengan dirinya sendiri = cocok"**. Hal ini dibuktikan dari output inference di mana **semua skor keluar identik (`0.534875`)**, tidak peduli kombinasi user dan lomba apa yang diuji.

Untuk mengatasinya, dataset `synthetic_users.csv` ini dirancang dengan menyajikan karakteristik *user* sesungguhnya yang bervariasi dan kontras, lengkap dengan panduan **Aturan Matching** untuk membentuk pasangan data pelatihan (user-item pairs) yang sehat dengan label `1` (positif) dan `0` (negatif).

---

## 📁 Struktur File & Aturan Kolom

File yang dihasilkan adalah **`synthetic_users.csv`** (Berisi **1.500 baris data**, hasil dari 5 persona dasar × 300 variasi *user*).

Nama dan urutan kolom pada file ini telah disesuaikan secara **identik (persis)** dengan urutan `feature_cols` pada model AI Anda (`hasil_feature.csv`), sehingga tim AI bisa langsung menggunakannya tanpa perlu melakukan konversi/pemetaan ulang:

| Nama Kolom | Tipe | Keterangan |
| --- | --- | --- |
| `user_id` | string | ID Unik User (format: `user_0001` s.d `user_1500`) |
| `Biaya_Rata_Rata` | int | Batas biaya maksimal yang sanggup dikeluarkan user |
| `Domain_Akademik` | 0 / 1 | Minat user pada kompetisi ilmiah/akademik |
| `Domain_Bisnis_Karir` | 0 / 1 | Minat user pada kompetisi bisnis, startup, atau karir |
| `Domain_Olahraga_E-Sport` | 0 / 1 | Minat user pada kompetisi olahraga fisik atau game |
| `Domain_Seni_Kreatif` | 0 / 1 | Minat user pada kompetisi desain, seni, fotografi, musik |
| `Domain_Teknologi` | 0 / 1 | Minat user pada kompetisi koding, data science, cyber security, IT |
| `Domain_Umum_Lainnya` | 0 / 1 | Minat user pada kompetisi kategori umum |
| `Jenjang_Encoded` | int (1–5) | Kategori tingkat pendidikan (1=SD, 2=SMP, 3=SMA, 4=Mahasiswa, 5=Umum) |
| `Is_Online` | 0 / 1 | Preferensi user mengikuti lomba secara daring |
| `Is_Offline` | 0 / 1 | Preferensi user mengikuti lomba secara luring |
| **`Persona_Name`** | string | **[Kolom Bantuan DS]** Identitas kelompok persona untuk mempermudah *matching logic* |

> ⚠️ **PENTING UNTUK TIM AI:** Kolom `Persona_Name` diletakkan di paling kanan hanya sebagai jangkar pembantu untuk membuat label data. **Wajib lakukan `.drop(columns=['Persona_Name'])**` sebelum data dimasukkan ke dalam *input layer* model TensorFlow Anda.

---

## 👤 Profil 5 Persona Kontras

Untuk memastikan model Two-Tower bisa belajar membedakan preferensi lintas fitur secara optimal, kami membuat 5 kelompok persona yang saling bertolak belakang:

1. **Tech Mahasiswa Online**
* Karakteristik utama: Mahasiswa IT/Sistem Informasi yang berburu kompetisi koding atau ide bisnis digital secara online dengan budget gratis hingga murah.


2. **Kreator Seni SMA Offline**
* Karakteristik utama: Siswa SMA kreatif yang menyukai pameran, lomba lukis, poster, atau fotografi langsung di lapangan (luring/offline).


3. **Atlet SMP/SMA**
* Karakteristik utama: Pelajar sekolah menengah yang aktif mencari turnamen olahraga fisik lokal atau kompetisi E-Sport regional.


4. **Akademisi Mahasiswa**
* Karakteristik utama: Mahasiswa berprestasi yang fokus pada pengerjaan karya tulis ilmiah (KTI), esai nasional, dan konferensi akademik dengan budget fleksibel.


5. **Bisnis/Karir Umum**
* Karakteristik utama: Masyarakat umum atau profesional muda yang mencari kompetisi *business plan*, studi kasus perusahaan, atau sertifikasi pengembangan karir.



*Catatan: Setiap baris user pada persona di atas telah disuntikkan keacakan acak (~5% noise) agar nilai fiturnya tidak seragam (kembar identik), meniru distribusi perilaku manusia di dunia nyata.*

---

## 🧩 Logika Pemasangan (Matching & Labeling Logic)

Tim AI Engineering dapat menggunakan kolom kunci `Persona_Name` pada `synthetic_users.csv` untuk dipasangkan dengan baris kompetisi di `hasil_feature.csv` menggunakan aturan kondisional berikut:

| Nama Persona | Kriteria Lomba Positif (Label = 1) | Kriteria Lomba Negatif (Label = 0) |
| --- | --- | --- |
| **Tech Mahasiswa Online** | Lomba yang memiliki `Domain_Teknologi` == 1 ATAU `Domain_Bisnis_Karir` == 1. Utamakan yang `Is_Online` == 1. | Lomba seni murni atau olahraga fisik luar ruangan yang mewajibkan hadir langsung (`Is_Offline` == 1). |
| **Kreator Seni SMA Offline** | Lomba dengan `Domain_Seni_Kreatif` == 1 dan diselenggarakan secara `Is_Offline` == 1. | Lomba koding intensif (`Domain_Teknologi` == 1) atau turnamen game virtual (`Is_Online` == 1). |
| **Atlet SMP/SMA** | Lomba dengan `Domain_Olahraga_E-Sport` == 1 dengan jenjang sekolah menengah (`Jenjang_Encoded` $\le$ 3). | Lomba esai/paper teoretis tingkat universitas (`Domain_Akademik` == 1 dan `Jenjang_Encoded` == 4). |
| **Akademisi Mahasiswa** | Lomba riset/ilmiah (`Domain_Akademik` == 1) yang ditargetkan untuk Mahasiswa/Umum (`Jenjang_Encoded` $\ge$ 4). | Turnamen game/olahraga fisik anak sekolah menengah atau dasar (`Jenjang_Encoded` $\le$ 2). |
| **Bisnis/Karir Umum** | Lomba manajemen, startup, dan profesional (`Domain_Bisnis_Karir` == 1). | Lomba kesenian sekolah dasar atau lomba internal universitas yang tidak terbuka untuk umum. |

---

## 💡 Contoh Implementasi Skrip Pipeline Data (Python)

Gunakan potongan kode di bawah ini di dalam Jupyter Notebook tim AI untuk mengawinkan kedua data menjadi dataset *training* baru yang siap pakai:

```python
import pandas as pd
import numpy as np

# 1. Load Data
df_user = pd.read_csv('synthetic_users.csv')
df_lomba = pd.read_csv('hasil_feature.csv')

training_pairs = []

# 2. Contoh Ekstraksi Pasangan untuk Persona: Tech Mahasiswa Online
tech_users = df_user[df_user['Persona_Name'] == 'Tech Mahasiswa Online']

# Ambil kumpulan lomba yang cocok (Positif) dan tidak cocok (Negatif)
lomba_positif = df_lomba[(df_lomba['Domain_Teknologi'] == 1) | (df_lomba['Domain_Bisnis_Karir'] == 1)]
lomba_negatif = df_lomba[((df_lomba['Domain_Seni_Kreatif'] == 1) | (df_lomba['Domain_Olahraga_E-Sport'] == 1)) & (df_lomba['Is_Offline'] == 1)]

# lakukan perulangan atau sampling untuk membuat pair data (User_Features, Item_Features, Label)
# ... kerjakan juga logika yang sama untuk 4 persona lainnya ...

# 3. Finalisasi Sebelum Training
# Jangan lupa menghapus kolom string bantuan agar bentuk matriks TensorFlow pas
# df_final.drop(columns=['Persona_Name'], inplace=True)

```
📝 Dokumentasi Aturan Matching (Labeling Logic)
Aturan ini menentukan bagaimana setiap Persona_Name dipasangkan dengan fitur lomba di hasil_feature.csv untuk menghasilkan label 1 (memiliki domain yang sesuai/relevan) dan label 0 (memiliki domain yang bertolak belakang/tidak relevan).

1. Persona: "Tech Mahasiswa Online"

➔ Positif (label=1): Dipasangkan dengan lomba yang memiliki Domain_Teknologi == 1 ATAU Domain_Bisnis_Karir == 1.

➔ Negatif (label=0): Dipasangkan dengan lomba yang memiliki Domain_Seni_Kreatif == 1 ATAU Domain_Olahraga_E-Sport == 1.

2. Persona: "Kreator Seni SMA Offline"

➔ Positif (label=1): Dipasangkan dengan lomba yang memiliki Domain_Seni_Kreatif == 1.

➔ Negatif (label=0): Dipasangkan dengan lomba yang memiliki Domain_Teknologi == 1 ATAU Domain_Bisnis_Karir == 1.

3. Persona: "Atlet SMP/SMA"

➔ Positif (label=1): Dipasangkan dengan lomba yang memiliki Domain_Olahraga_E-Sport == 1.

➔ Negatif (label=0): Dipasangkan dengan lomba yang memiliki Domain_Akademik == 1 ATAU Domain_Seni_Kreatif == 1.

4. Persona: "Akademisi Mahasiswa"

➔ Positif (label=1): Dipasangkan dengan lomba yang memiliki Domain_Akademik == 1.

➔ Negatif (label=0): Dipasangkan dengan lomba yang memiliki Domain_Olahraga_E-Sport == 1 ATAU Domain_Seni_Kreatif == 1.

5. Persona: "Bisnis/Karir Umum"

➔ Positif (label=1): Dipasangkan dengan lomba yang memiliki Domain_Bisnis_Karir == 1.

➔ Negatif (label=0): Dipasangkan dengan lomba yang memiliki Domain_Seni_Kreatif == 1 ATAU Domain_Olahraga_E-Sport == 1.

💻 Format Komentar Kode (Python Docstring)
Jika tim AI membutuhkan format ini untuk langsung diletakkan di dalam script ekstraksi data mereka, silakan gunakan blok ini:

Python
"""
=======================================================================
ATURAN MATCHING TRAINING PAIRS (USER SINTETIK -> LOMBA)
=======================================================================
Gunakan `Persona_Name` sebagai acuan untuk memfilter `hasil_feature.csv`.

1. Tech Mahasiswa Online
   - Positif (1) : Domain_Teknologi == 1 | Domain_Bisnis_Karir == 1
   - Negatif (0) : Domain_Seni_Kreatif == 1 | Domain_Olahraga_E-Sport == 1

2. Kreator Seni SMA Offline
   - Positif (1) : Domain_Seni_Kreatif == 1
   - Negatif (0) : Domain_Teknologi == 1 | Domain_Bisnis_Karir == 1

3. Atlet SMP/SMA
   - Positif (1) : Domain_Olahraga_E-Sport == 1
   - Negatif (0) : Domain_Akademik == 1 | Domain_Seni_Kreatif == 1

4. Akademisi Mahasiswa
   - Positif (1) : Domain_Akademik == 1
   - Negatif (0) : Domain_Olahraga_E-Sport == 1 | Domain_Seni_Kreatif == 1

5. Bisnis/Karir Umum
   - Positif (1) : Domain_Bisnis_Karir == 1
   - Negatif (0) : Domain_Seni_Kreatif == 1 | Domain_Olahraga_E-Sport == 1

Catatan: Buang (drop) kolom `Persona_Name` sebelum masuk layer model.
=======================================================================
"""
