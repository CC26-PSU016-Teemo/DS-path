import pandas as pd
import numpy as np
import random

def buat_data_kotor():
    # 1. Load data yang bersih
    file_bersih = 'data_lomba_full.csv'
    try:
        df = pd.read_csv(file_bersih)
        print(f"Data bersih berhasil di-load! Total baris awal: {len(df)}")
    except FileNotFoundError:
        print(f"File {file_bersih} tidak ditemukan. Pastikan namanya sudah benar.")
        return

    # 2. BIKIN DUPLICATES (Data Ganda)
    # Ambil acak 20 - 30 baris
    jumlah_duplicate = random.randint(20, 30)
    baris_duplicate = df.sample(n=jumlah_duplicate, replace=True)
    df = pd.concat([df, baris_duplicate], ignore_index=True)
    
    # Acak urutan barisnya biar duplicatenya nyebar, nggak numpuk di bawah
    df = df.sample(frac=1).reset_index(drop=True)
    print(f"[+] Menambahkan {jumlah_duplicate} baris duplikat.")

    total_baris_baru = len(df)

    # 3. BIKIN MISSING VALUES (NaN / Null)
    # Bikin 20 - 30 sel kosong secara acak
    kolom_sasaran_nan = ['Biaya Registrasi', 'Penyelenggara', 'Tema/Kategori', 'Jenjang']
    jumlah_nan = random.randint(20, 30)
    
    for _ in range(jumlah_nan):
        baris_acak = random.randint(0, total_baris_baru - 1)
        kolom_acak = random.choice(kolom_sasaran_nan)
        df.loc[baris_acak, kolom_acak] = np.nan
        
    print(f"[+] Membuat {jumlah_nan} sel menjadi kosong (NaN).")

    # 4. Export Data Kotor
    nama_file_kotor = 'data_lomba_mentah.csv'
    df.to_csv(nama_file_kotor, index=False, encoding='utf-8')
    
    print(f"\n✅ Selesai! Data mentah berhasil disimpan sebagai '{nama_file_kotor}'")
    print(f"Total baris sekarang: {len(df)}")

if __name__ == "__main__":
    buat_data_kotor()