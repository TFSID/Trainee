import json
import csv
import os

# --- KONFIGURASI NAMA FILE ---
JSON_FILE_PATH = 'anime_dataset_1000.json'
CSV_FILE_PATH = 'anime_dataset_1000.csv'

def convert_json_to_csv():
    """
    Membaca data dari file JSON, mengekstrak informasi yang relevan,
    dan menuliskannya ke dalam file CSV.
    """
    # 1. Periksa apakah file JSON sumber ada
    if not os.path.exists(JSON_FILE_PATH):
        print(f"Error: File '{JSON_FILE_PATH}' tidak ditemukan.")
        print("Pastikan Anda sudah menjalankan skrip 'generate_dataset.py' terlebih dahulu.")
        return

    # 2. Baca file JSON
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Berhasil membaca {len(data)} data dari '{JSON_FILE_PATH}'.")
    except json.JSONDecodeError:
        print(f"Error: Gagal mem-parsing file '{JSON_FILE_PATH}'. Pastikan formatnya benar.")
        return
    except Exception as e:
        print(f"Terjadi error saat membaca file: {e}")
        return

    # 3. Tulis ke file CSV
    try:
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            # Tentukan nama kolom untuk header CSV
            header = ['Instruction', 'Input', 'Response']
            writer = csv.DictWriter(f, fieldnames=header)

            # Tulis header ke file CSV
            writer.writeheader()

            # Proses setiap entri dalam data JSON
            for entry in data:
                # Karena setiap entri adalah dict dengan satu kunci (mis: "dataset_example_0001"),
                # kita ambil nilainya (value) yang berisi data sebenarnya.
                # list(entry.values())[0] adalah cara cepat untuk mendapatkan value tersebut.
                actual_data = list(entry.values())[0]
                
                # Tulis baris data ke file CSV
                writer.writerow({
                    'Instruction': actual_data.get('Instruction', ''),
                    'Input': actual_data.get('Input', ''),
                    'Response': actual_data.get('Response', '')
                })
        
        print(f"\nKonversi berhasil!")
        print(f"Data telah disimpan ke '{CSV_FILE_PATH}'.")

    except Exception as e:
        print(f"Terjadi error saat menulis file CSV: {e}")

# --- JALANKAN FUNGSI UTAMA ---
if __name__ == '__main__':
    convert_json_to_csv()