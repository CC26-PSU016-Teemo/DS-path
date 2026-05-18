from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

def scrape_infolomba_final():
    base_url = 'https://infolomba.id/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') 
    
    print("Membuka browser dan mengakses halaman utama...")
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    driver.maximize_window()

    klik_count = 0
    batas_maksimal_klik = 200  # <--- Ubah angka ini sesuai kebutuhan
    
    print(f"\nMemuat data lomba (Maksimal {batas_maksimal_klik} kali klik Load More)...")

    while klik_count < batas_maksimal_klik:
        try:
            btn_load_more = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "btnLoadMore"))
            )
            if not btn_load_more.is_displayed():
                break
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_load_more)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", btn_load_more)
            klik_count += 1
            print(f"Klik Load More ke-{klik_count} dari {batas_maksimal_klik}")
            time.sleep(3)
        except Exception as e:
            break

    print("\nMengekstrak data dari halaman utama...")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit() 

    data_lomba = []
    cards = soup.find_all('div', class_='event-container') 

    for card in cards:
        try:
            judul_elem = card.find('h4', class_='event-title')
            judul = judul_elem.text.strip() if judul_elem else "Tidak ada judul"
            
            if judul_elem and judul_elem.find('a'):
                link_detail = base_url + judul_elem.find('a')['href']
            else:
                link_detail = None

            img_container = card.find('a', class_='img-container')
            poster_url = base_url + img_container.find('img')['src'] if img_container and img_container.find('img') else "Tidak ada gambar"

            jenjang_elem = card.find('div', class_='target')
            jenjang = jenjang_elem.text.strip() if jenjang_elem else "Umum"

            biaya_elem = card.find('div', class_='biaya')
            biaya = biaya_elem.text.strip() if biaya_elem else "Gratis"

            tipe_elem = card.find('div', class_='lokasi')
            tipe = tipe_elem.text.strip() if tipe_elem else "Tidak disebutkan"

            tanggal_elem = card.find('div', class_='tanggal')
            tanggal = tanggal_elem.text.strip() if tanggal_elem else "Tidak disebutkan"

            penyelenggara_div = card.find('div', class_='penyelenggara')
            penyelenggara = penyelenggara_div.find_all('span')[-1].text.strip() if penyelenggara_div else "Tidak disebutkan"
            
            if link_detail:
                data_lomba.append({
                    'Judul': judul,
                    'Jenjang': jenjang,
                    'Biaya Registrasi': biaya,
                    'Tipe (Online/Offline)': tipe,
                    'Tanggal Pelaksanaan': tanggal,
                    'Penyelenggara': penyelenggara,
                    'Tema/Kategori': "Memproses...", 
                    'Link Poster': poster_url,
                    'Link Detail': link_detail 
                })

        except Exception as e:
            continue

    total_data = len(data_lomba)
    print(f"\nBerhasil mengumpulkan {total_data} lomba.")
    print("Masuk ke halaman detail untuk mengambil kata kategori (Maks. 3 kategori unik)...")

    for i, lomba in enumerate(data_lomba):
        print(f"Scraping kategori [{i+1}/{total_data}] - {lomba['Judul'][:30]}...") 
        try:
            res = requests.get(lomba['Link Detail'], headers=headers)
            if res.status_code == 200:
                detail_soup = BeautifulSoup(res.content, 'html.parser')
                kategori_items = detail_soup.find_all('div', class_='kategori-item')
                
                if kategori_items:
                    list_kategori_unik = []
                    for item in kategori_items:
                        teks_kategori = item.text.strip()
                        
                        # Cek agar teks tidak kosong dan tidak duplikat
                        if teks_kategori and teks_kategori not in list_kategori_unik:
                            list_kategori_unik.append(teks_kategori)
                        
                        # Kalau sudah dapet 3 kategori unik, langsung berhenti nyari
                        if len(list_kategori_unik) == 3:
                            break
                            
                    lomba['Tema/Kategori'] = ', '.join(list_kategori_unik) 
                else:
                    lomba['Tema/Kategori'] = "Tidak ada kategori"
            else:
                lomba['Tema/Kategori'] = f"Gagal akses link"
        except Exception as e:
            lomba['Tema/Kategori'] = "Error jaringan"

    if data_lomba:
        df = pd.DataFrame(data_lomba)
        
        # Menghapus kolom Link Detail agar tidak masuk ke CSV
        df = df.drop(columns=['Link Detail']) 
        
        df.to_csv('data_lomba_full.csv', index=False, encoding='utf-8')
        print(f"\n✅ Scraping selesai! Data bersih tersimpan ke 'data_lomba_full.csv'")
    else:
        print("Tidak ada data yang berhasil di-scrape.")

if __name__ == "__main__":
    scrape_infolomba_final()