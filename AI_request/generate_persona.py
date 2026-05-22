import pandas as pd
import numpy as np

# Set seed agar hasil bisa direproduksi (konsisten) jika dijalankan berulang
np.random.seed(42)

# Konfigurasi jumlah data
num_users_per_persona = 300
total_users = num_users_per_persona * 5 # Total 1000 baris

# 1. Definisi Base Personas beserta baseline nilainya
personas = [
    {
        "name": "Tech Mahasiswa Online",
        "Domain_Akademik": 0, "Domain_Bisnis_Karir": 1, "Domain_Olahraga_E-Sport": 0,
        "Domain_Seni_Kreatif": 0, "Domain_Teknologi": 1, "Domain_Umum_Lainnya": 0,
        "Jenjang_Encoded": 4, "Is_Online": 1, "Is_Offline": 0,
        "Biaya_Rata_Rata_min": 0, "Biaya_Rata_Rata_max": 100000
    },
    {
        "name": "Kreator Seni SMA Offline",
        "Domain_Akademik": 0, "Domain_Bisnis_Karir": 0, "Domain_Olahraga_E-Sport": 0,
        "Domain_Seni_Kreatif": 1, "Domain_Teknologi": 0, "Domain_Umum_Lainnya": 0,
        "Jenjang_Encoded": 3, "Is_Online": 0, "Is_Offline": 1,
        "Biaya_Rata_Rata_min": 50000, "Biaya_Rata_Rata_max": 200000
    },
    {
        "name": "Atlet SMP/SMA",
        "Domain_Akademik": 0, "Domain_Bisnis_Karir": 0, "Domain_Olahraga_E-Sport": 1,
        "Domain_Seni_Kreatif": 0, "Domain_Teknologi": 0, "Domain_Umum_Lainnya": 0,
        "Jenjang_Encoded": [2, 3], "Is_Online": [0, 1], "Is_Offline": [0, 1],
        "Biaya_Rata_Rata_min": 0, "Biaya_Rata_Rata_max": 150000
    },
    {
        "name": "Akademisi Mahasiswa",
        "Domain_Akademik": 1, "Domain_Bisnis_Karir": 0, "Domain_Olahraga_E-Sport": 0,
        "Domain_Seni_Kreatif": 0, "Domain_Teknologi": 0, "Domain_Umum_Lainnya": 0,
        "Jenjang_Encoded": 4, "Is_Online": 1, "Is_Offline": 0,
        "Biaya_Rata_Rata_min": 0, "Biaya_Rata_Rata_max": 300000
    },
    {
        "name": "Bisnis/Karir Umum",
        "Domain_Akademik": 0, "Domain_Bisnis_Karir": 1, "Domain_Olahraga_E-Sport": 0,
        "Domain_Seni_Kreatif": 0, "Domain_Teknologi": 0, "Domain_Umum_Lainnya": 0,
        "Jenjang_Encoded": 5, "Is_Online": [0, 1], "Is_Offline": [0, 1],
        "Biaya_Rata_Rata_min": 50000, "Biaya_Rata_Rata_max": 500000
    }
]

users = []
user_id_counter = 1

# 2. Proses Generate Data dengan Noise (~5%)
for persona in personas:
    for _ in range(num_users_per_persona):
        user = {"user_id": f"user_{user_id_counter:04d}"}
        
        # Randomisasi Biaya dalam rentang persona
        user["Biaya_Rata_Rata"] = np.random.randint(persona["Biaya_Rata_Rata_min"], persona["Biaya_Rata_Rata_max"] + 1)
        
        # Tambahkan Noise pada Domains (5% kemungkinan flip bit 0 ke 1 atau 1 ke 0)
        for domain in ["Domain_Akademik", "Domain_Bisnis_Karir", "Domain_Olahraga_E-Sport", 
                       "Domain_Seni_Kreatif", "Domain_Teknologi", "Domain_Umum_Lainnya"]:
            val = persona[domain]
            if np.random.rand() < 0.05:  # 5% Noise
                val = 1 - val
            user[domain] = val
            
        # Tambahkan Noise pada Jenjang (Shift ke atas/bawah 1 tingkat)
        if isinstance(persona["Jenjang_Encoded"], list):
            jenjang = np.random.choice(persona["Jenjang_Encoded"])
        else:
            jenjang = persona["Jenjang_Encoded"]
            if np.random.rand() < 0.05:
                jenjang = max(1, min(5, jenjang + np.random.choice([-1, 1]))) # Batasi 1-5
        user["Jenjang_Encoded"] = jenjang
        
        # Tambahkan Noise pada preferensi Online/Offline
        if isinstance(persona["Is_Online"], list):
            online = np.random.choice(persona["Is_Online"])
        else:
            online = persona["Is_Online"]
            if np.random.rand() < 0.05: online = 1 - online
            
        if isinstance(persona["Is_Offline"], list):
            offline = np.random.choice(persona["Is_Offline"])
        else:
            offline = persona["Is_Offline"]
            if np.random.rand() < 0.05: offline = 1 - offline
            
        # Mencegah edge case dimana user tidak mau online dan offline (keduanya 0)
        if online == 0 and offline == 0:
            if np.random.rand() > 0.5:
                online = 1
            else:
                offline = 1
                
        user["Is_Online"] = online
        user["Is_Offline"] = offline
        
        # Menyimpan label Persona_Name untuk mempermudah AI team saat matching
        user["Persona_Name"] = persona["name"] 
        
        users.append(user)
        user_id_counter += 1

# 3. Masukkan ke DataFrame dan rapikan kolom
df = pd.DataFrame(users)

columns_order = [
    "user_id", "Biaya_Rata_Rata", "Domain_Akademik", "Domain_Bisnis_Karir", 
    "Domain_Olahraga_E-Sport", "Domain_Seni_Kreatif", "Domain_Teknologi", 
    "Domain_Umum_Lainnya", "Jenjang_Encoded", "Is_Online", "Is_Offline", "Persona_Name"
]
df = df[columns_order]

# 4. Simpan ke CSV
output_filename = "synthetic_users.csv"
df.to_csv(output_filename, index=False)

print(f"✅ File '{output_filename}' berhasil dibuat!")
print(f"📊 Dimensi Data: {df.shape[0]} baris, {df.shape[1]} kolom")
print("📌 Preview Data:")
print(df.head())