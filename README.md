
# CVE Analyst LLM System - Modular Version



## Todo List

- Membuat Listener Untuk channel discord menggunakan bots & mengirimkan data chat terbaru kedalam database/file text
- Mengintegrasikan LLM dengan search engine menggunakan MCP (Model Context Protocol) atau dengan CLI Tools (Scraper)  



Sistem analisis CVE berbasis AI yang menggunakan DeepSeek-Coder untuk memberikan rekomendasi keamanan otomatis.

## Struktur Modular

```
cve-analyst/
├── config/
│   └── settings.py          # Konfigurasi sistem
├── database/
│   └── models.py           # Database models dan operasi
├── scrapers/
│   └── cve_scraper.py      # CVE data scraping
├── data/
│   └── dataset_generator.py # Training dataset generation
├── training/
│   └── model_trainer.py    # Model fine-tuning
├── api/
│   ├── cve_analyst_api.py  # Core API logic
│   ├── fastapi_app.py      # FastAPI application
│   └── gradio_app.py       # Gradio interface
├── scheduler/
│   └── cve_scheduler.py    # Automated scheduling
├── utils/
│   └── logging_config.py   # Logging configuration
├── cli/
│   └── main.py            # Command line interface
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Instalasi

1. Clone repository dan install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup sistem:
```bash
python cli/main.py setup --nvd-api-key YOUR_API_KEY
```

3. Scrape data CVE:
```bash
python cli/main.py scrape --days 30
```

4. Train model:
```bash
python cli/main.py train
```

## Penggunaan

### Command Line Interface

```bash
# Analyze CVE
python cli/main.py analyze CVE-2024-1234

# Start API server
python cli/main.py api --port 8000

# Start Gradio interface
python cli/main.py api --interface gradio --port 7860

# Start scheduler
python cli/main.py schedule
```

### Docker Deployment

```bash
# Build dan jalankan dengan docker-compose
docker-compose up -d
```

### API Endpoints

- `POST /analyze` - Analyze CVE
- `GET /cve/{cve_id}` - Get CVE info
- `GET /recent-cves` - Get recent CVEs
- `GET /health` - Health check

## Fitur Utama

1. **Modular Architecture** - Setiap komponen terpisah dan dapat digunakan independen
2. **Auto-updating** - Scraping otomatis data CVE terbaru
3. **Model Fine-tuning** - Training model dengan QLoRA
4. **Multiple Interfaces** - FastAPI dan Gradio
5. **Scheduling** - Update otomatis dan retraining model
6. **Docker Support** - Deployment mudah dengan Docker

## Environment Variables

```bash
export NVD_API_KEY="your_nvd_api_key"
export MODEL_NAME="deepseek-ai/deepseek-coder-1.3b-instruct"
export MAX_LENGTH="2048"
export BATCH_SIZE="4"
```

## Pengembangan

Setiap modul dapat dikembangkan secara independen:

- `config/settings.py` - Tambah konfigurasi baru
- `scrapers/` - Tambah sumber data baru
- `data/` - Modifikasi format dataset
- `training/` - Eksperimen dengan model berbeda
- `api/` - Tambah endpoint baru

## Kontribusi

1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Create Pull Request
