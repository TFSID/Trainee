"""
Configuration module for CVE Analyst System
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from typing import Optional, List, Dict, Any


@dataclass
class CVEConfig:
    """Konfigurasi sistem CVE Analyst"""
    # Data Sources
    nvd_api_key: str = ""
    mitre_cve_url: str = "https://cve.mitre.org/data/downloads/allitems.csv"
    nvd_base_url: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    exploit_db_url: str = "https://gitlab.com/exploit-database/exploitdb/-/raw/main/files_exploits.csv"
    
    # Model Config
    model_name: str = "deepseek-ai/deepseek-coder-1.3b-instruct"
    max_length: int = 2048
    batch_size: int = 4
    learning_rate: float = 2e-4
    
    # Paths
    data_dir: Path = Path("./cve_data")
    model_dir: Path = Path("./models")
    logs_dir: Path = Path("./logs")
    
    # Schedule
    update_interval_hours: int = 6
    
    def __post_init__(self):
        for path in [self.data_dir, self.model_dir, self.logs_dir]:
            path.mkdir(exist_ok=True, parents=True)

    @classmethod
    def from_env(cls) -> 'CVEConfig':
        """Load configuration from environment variables"""
        return cls(
            nvd_api_key=os.getenv('NVD_API_KEY', ''),
            model_name=os.getenv('MODEL_NAME', 'deepseek-ai/deepseek-coder-1.3b-instruct'),
            max_length=int(os.getenv('MAX_LENGTH', '2048')),
            batch_size=int(os.getenv('BATCH_SIZE', '4')),
            learning_rate=float(os.getenv('LEARNING_RATE', '2e-4')),
            update_interval_hours=int(os.getenv('UPDATE_INTERVAL_HOURS', '6'))
        )
@dataclass
class ModelTrainerConfig:
    """Konfigurasi sistem pelatihan model AI"""

    # Pengaturan unggahan file
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    supported_formats: List[str] = None
    upload_directory: Path = Path("./uploads")

    # Pengaturan model
    base_models: List[str] = None
    default_learning_rate: float = 0.001
    default_batch_size: int = 4
    default_epochs: int = 3
    max_sequence_length: int = 2048

    # Pengaturan pelatihan
    max_concurrent_jobs: int = 5
    training_timeout: int = 3600  # 1 jam
    checkpoint_interval: int = 100

    # Pengaturan API
    api_timeout: int = 30
    max_retries: int = 3

    # Direktori penyimpanan
    models_directory: Path = Path("./models")
    logs_directory: Path = Path("./logs")

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ['.json', '.jsonl', '.csv', '.txt', '.parquet']

        if self.base_models is None:
            self.base_models = [
                'gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo',
                'llama-2-7b', 'llama-2-13b',
                'mistral-7b', 'mistral-8x7b',
                'bert-base-uncased', 'bert-large-uncased',
                'roberta-base', 'distilbert-base-uncased'
            ]

        for path in [self.upload_directory, self.models_directory, self.logs_directory]:
            path.mkdir(exist_ok=True, parents=True)

    @classmethod
    def from_env(cls) -> 'ModelTrainerConfig':
        """Muat konfigurasi dari variabel lingkungan"""
        return cls(
            max_file_size=int(os.getenv('MAX_FILE_SIZE', str(100 * 1024 * 1024))),
            default_learning_rate=float(os.getenv('LEARNING_RATE', '0.001')),
            default_batch_size=int(os.getenv('BATCH_SIZE', '4')),
            default_epochs=int(os.getenv('EPOCHS', '3')),
            max_sequence_length=int(os.getenv('MAX_SEQ_LENGTH', '2048')),
            max_concurrent_jobs=int(os.getenv('MAX_JOBS', '5')),
            training_timeout=int(os.getenv('TRAINING_TIMEOUT', '3600')),
            checkpoint_interval=int(os.getenv('CHECKPOINT_INTERVAL', '100')),
            api_timeout=int(os.getenv('API_TIMEOUT', '30')),
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            upload_directory=Path(os.getenv('UPLOAD_DIR', './uploads')),
            models_directory=Path(os.getenv('MODELS_DIR', './models')),
            logs_directory=Path(os.getenv('LOGS_DIR', './logs'))
        )


# @dataclass
# class BrandConfig:
#     """Konfigurasi tampilan merek untuk penyesuaian white-label"""

#     company_name: str = "AI Model Trainer"
#     logo_url: str = ""
#     primary_color: str = "#3b82f6"
#     secondary_color: str = "#1e40af"
#     accent_color: str = "#10b981"
#     background_color: str = "#f8fafc"
#     text_color: str = "#1f2937"

#     # Kustomisasi CSS
#     custom_css: str = ""

#     # Penyesuaian footer dan header
#     show_footer: bool = True
#     footer_text: str = "Powered by AI Model Trainer"
#     header_title: str = ""
#     header_subtitle: str = "Train custom AI models with your data"

#     def to_dict(self) -> Dict[str, Any]:
#         """Konversi ke dict untuk serialisasi JSON"""
#         return {
#             'company_name': self.company_name,
#             'logo_url': self.logo_url,
#             'primary_color': self.primary_color,
#             'secondary_color': self.secondary_color,
#             'accent_color': self.accent_color,
#             'background_color': self.background_color,
#             'text_color': self.text_color,
#             'custom_css': self.custom_css,
#             'show_footer': self.show_footer,
#             'footer_text': self.footer_text,
#             'header_title': self.header_title,
#             'header_subtitle': self.header_subtitle
#         }