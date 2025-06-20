"""
Scheduler module for automated CVE updates and model retraining
"""
import schedule
import time
import asyncio
import logging
from datetime import datetime

from config.settings import CVEConfig
from scrapers.cve_scraper import CVEScraper
from data.dataset_generator import DatasetGenerator
from training.model_trainer import CVEModelTrainer

logger = logging.getLogger(__name__)

class CVEScheduler:
    """Scheduler untuk auto-update sistem"""
    
    def __init__(self, config: CVEConfig):
        self.config = config
        self.scraper = CVEScraper(config)
        self.dataset_generator = DatasetGenerator(config)
        self.trainer = CVEModelTrainer(config)
    
    def update_cve_data(self):
        """Update CVE data dari semua sumber"""
        logger.info("Starting scheduled CVE data update")
        
        try:
            # Scrape new CVEs
            asyncio.run(self.scraper.scrape_nvd_cves(days_back=1))
            
            # Scrape exploits
            self.scraper.scrape_exploit_db()
            
            # Generate new training data
            dataset = self.dataset_generator.generate_instruction_dataset()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.dataset_generator.save_dataset(dataset, f"dataset_{timestamp}.json")
            
            logger.info("CVE data update completed successfully")
            
        except Exception as e:
            logger.error(f"Error during scheduled update: {e}")
    
    def retrain_model_weekly(self):
        """Retrain model weekly dengan data terbaru"""
        logger.info("Starting weekly model retraining")
        
        try:
            # Generate fresh dataset
            dataset = self.dataset_generator.generate_instruction_dataset()
            
            # Retrain model
            self.trainer.train_model(dataset)
            
            logger.info("Weekly model retraining completed")
            
        except Exception as e:
            logger.error(f"Error during model retraining: {e}")
    
    def start_scheduler(self):
        """Start scheduled tasks"""
        # Daily CVE updates
        schedule.every().day.at("06:00").do(self.update_cve_data)
        schedule.every().day.at("18:00").do(self.update_cve_data)
        
        # Weekly model retraining
        schedule.every().sunday.at("02:00").do(self.retrain_model_weekly)
        
        logger.info("Scheduler started - CVE updates every 12 hours, model retraining weekly")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
