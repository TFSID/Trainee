import json
import random

# --- KOLAM DATA (BISA DIPERLUAS) ---
# Tambahkan lebih banyak anime, karakter, istilah, dll. untuk dataset yang lebih kaya

ANIME_DB = {
    'Attack on Titan': {'genre': 'Aksi, Fantasi Gelap, Tragedi', 'theme': 'Perang, Kebebasan, Keputusasaan', 'studio': 'Wit Studio / MAPPA'},
    'Jujutsu Kaisen': {'genre': 'Aksi, Fantasi Gelap, Supernatural', 'theme': 'Kutukan, Persahabatan, Pengorbanan', 'studio': 'MAPPA'},
    'Violet Evergarden': {'genre': 'Drama, Slice of Life, Fantasi', 'theme': 'Emosi, Kehilangan, Mencari Makna', 'studio': 'Kyoto Animation'},
    'Steins;Gate': {'genre': 'Sci-Fi, Thriller, Psikologis', 'theme': 'Perjalanan Waktu, Konspirasi, Takdir', 'studio': 'White Fox'},
    'Mushishi': {'genre': 'Slice of Life, Misteri, Supernatural', 'theme': 'Alam, Spiritualitas, Koeksistensi', 'studio': 'Artland'},
    'Code Geass': {'genre': 'Aksi, Mecha, Militer, Sci-Fi', 'theme': 'Pemberontakan, Keadilan, Manipulasi', 'studio': 'Sunrise'},
    'K-On!': {'genre': 'Slice of Life, Komedi, Musik', 'theme': 'Persahabatan, Musik, Kehidupan Sekolah', 'studio': 'Kyoto Animation'},
    'Psycho-Pass': {'genre': 'Sci-Fi, Kriminal, Psikologis', 'theme': 'Distopia, Keadilan, Teknologi', 'studio': 'Production I.G'},
    'Vinland Saga': {'genre': 'Aksi, Petualangan, Sejarah, Drama', 'theme': 'Balas Dendam, Perang, Penebusan', 'studio': 'Wit Studio / MAPPA'},
    'Your Lie in April': {'genre': 'Drama, Musik, Romansa', 'theme': 'Duka, Musik Klasik, Cinta', 'studio': 'A-1 Pictures'},
    'Made in Abyss': {'genre': 'Petualangan, Fantasi Gelap, Misteri', 'theme': 'Eksplorasi, Pengorbanan, Kebrutalan yang Kontras', 'studio': 'Kinema Citrus'},
}

CHARACTERS = {
    'Lelouch vi Britannia': 'Code Geass',
    'Ginko': 'Mushishi',
    'Rintarou Okabe': 'Steins;Gate',
    'Levi Ackerman': 'Attack on Titan',
    'Satoru Gojo': 'Jujutsu Kaisen',
    'Violet': 'Violet Evergarden',
    'Thorfinn': 'Vinland Saga',
    'Akane Tsunemori': 'Psycho-Pass',
}

TERMS_TROPE = {
    'Isekai': 'Subgenre di mana karakter utama dipindahkan dari dunia mereka ke dunia lain (biasanya fantasi). Contoh: Re:Zero, Sword Art Online.',
    'Tsundere': 'Tipe karakter yang awalnya bersikap dingin, kasar, atau jual mahal, tetapi perlahan menunjukkan sisi yang lebih hangat dan lembut.',
    'Sakuga': 'Istilah yang digunakan oleh penggemar anime untuk merujuk pada momen-momen di mana kualitas animasi meningkat secara drastis, biasanya dalam adegan aksi atau emosional.',
    'Seiyuu': 'Aktor atau aktris suara di Jepang. Mereka memiliki basis penggemar yang besar dan sering kali juga menjadi penyanyi.',
    'Deredere': 'Tipe karakter yang sangat manis, energik, dan penuh kasih sayang kepada semua orang, terutama orang yang mereka cintai.'
}

# --- TEMPLAT INSTRUKSI DAN RESPON ---

def generate_recommendation():
    anime_keys = list(ANIME_DB.keys())
    seed_count = random.randint(1, 2)
    seed_animes = random.sample(anime_keys, seed_count)
    
    instruction = "Anda adalah ahli anime. Berikan rekomendasi anime yang relevan berdasarkan preferensi pengguna. Jelaskan mengapa anime itu cocok."
    
    input_text = f"Tolong rekomendasikan anime. Aku suka {seed_animes[0]} karena tema {ANIME_DB[seed_animes[0]]['theme'].split(', ')[0].lower()}."
    if len(seed_animes) > 1:
        input_text += f" Aku juga menikmati {seed_animes[1]}."

    # Cari rekomendasi yang cocok
    seed_genres = set()
    for anime in seed_animes:
        seed_genres.update(ANIME_DB[anime]['genre'].split(', '))

    recommendations = []
    for anime, details in ANIME_DB.items():
        if anime in seed_animes:
            continue
        anime_genres = set(details['genre'].split(', '))
        if len(seed_genres.intersection(anime_genres)) > 0:
            recommendations.append(anime)
    
    if not recommendations:
        return None # Coba lagi jika tidak ada rekomendasi yang cocok

    final_recs = random.sample(recommendations, min(len(recommendations), 2))
    
    response_text = "Tentu, berdasarkan anime yang kamu suka, berikut adalah beberapa rekomendasi:\n\n"
    for rec in final_recs:
        response_text += f"**1. {rec}**\n"
        response_text += f"*Alasan:* Mirip dengan '{seed_animes[0]}', anime ini memiliki genre '{ANIME_DB[rec]['genre']}' dan mengangkat tema tentang {ANIME_DB[rec]['theme'].split(', ')[0].lower()}.\n\n"

    return {"Instruction": instruction, "Input": input_text, "Response": response_text}

def generate_explanation():
    term, explanation = random.choice(list(TERMS_TROPE.items()))
    
    instruction = "Jelaskan istilah atau trope umum dalam dunia anime dan budaya pop Jepang."
    input_text = f"Apa itu '{term}'?"
    response_text = f"'{term}' adalah sebuah istilah dalam dunia anime yang berarti: {explanation}"
    
    return {"Instruction": instruction, "Input": input_text, "Response": response_text}

def generate_character_analysis():
    char, anime = random.choice(list(CHARACTERS.items()))
    
    instruction = f"Berikan analisis singkat tentang karakter dari anime."
    input_text = f"Bisa tolong analisis karakter {char} dari anime {anime}?"
    response_text = (f"Tentu. {char} dari anime '{anime}' adalah karakter yang kompleks. "
                     f"Dia dikenal karena perannya dalam cerita yang berpusat pada tema {ANIME_DB[anime]['theme'].lower()}. "
                     f"Sifat utamanya sering kali didorong oleh tujuannya yang kuat, menjadikannya salah satu karakter paling ikonik dalam genre '{ANIME_DB[anime]['genre']}'. "
                     "Analisis lebih dalam akan mengungkap motivasi dan perkembangan karakternya sepanjang seri.")
                     
    return {"Instruction": instruction, "Input": input_text, "Response": response_text}

def generate_comparison():
    try:
        anime1, anime2 = random.sample(list(ANIME_DB.keys()), 2)
    except ValueError:
        return None

    instruction = "Bandingkan dua anime dari segi tema, genre, dan studio yang memproduksinya."
    input_text = f"Apa perbedaan utama antara {anime1} dan {anime2}?"
    
    details1 = ANIME_DB[anime1]
    details2 = ANIME_DB[anime2]

    response_text = (f"Berikut perbandingan antara '{anime1}' dan '{anime2}':\n\n"
                     f"**{anime1}:**\n"
                     f"- Genre: {details1['genre']}\n"
                     f"- Tema Utama: {details1['theme']}\n"
                     f"- Studio: {details1['studio']}\n\n"
                     f"**{anime2}:**\n"
                     f"- Genre: {details2['genre']}\n"
                     f"- Tema Utama: {details2['theme']}\n"
                     f"- Studio: {details2['studio']}\n\n"
                     f"Secara singkat, sementara {anime1} berfokus pada narasi {details1['genre'].split(', ')[0].lower()}, {anime2} lebih menonjol dalam aspek {details2['genre'].split(', ')[0].lower()}.")

    return {"Instruction": instruction, "Input": input_text, "Response": response_text}

# --- FUNGSI UTAMA ---

def main():
    dataset = []
    task_generators = [
        generate_recommendation,
        generate_explanation,
        generate_character_analysis,
        generate_comparison
    ]

    while len(dataset) < 1000:
        generator = random.choice(task_generators)
        data_entry = generator()
        if data_entry: # Memastikan generator berhasil membuat data
            dataset.append({f"dataset_example_{len(dataset)+1:04}": data_entry})

    # Menyimpan dataset ke file JSON
    with open('anime_dataset_1000.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print("Dataset berhasil dibuat! Cek file 'anime_dataset_1000.json'")

if __name__ == '__main__':
    main()