"""
Command Line Interface for CVE Analyst System
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import CVEConfig
from config.settings import ModelTrainerConfig

from scrapers.cve_scraper import CVEScraper
from data.dataset_generator import DatasetGenerator
from training.model_trainer import CVEModelTrainer
from api.cve_analyst_api import CVEAnalystAPI

from api.fastapi_app import create_fastapi_app
from api.gradio_app import create_gradio_interface
from scheduler.cve_scheduler import CVEScheduler
from utils.logging_config import setup_logging

import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server


def create_cli():
    """Create command line interface"""
    parser = argparse.ArgumentParser(description="CVE Analyst LLM System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Initialize system')
    setup_parser.add_argument('--model', default='deepseek-ai/deepseek-coder-1.3b-instruct', help='Model name')
    setup_parser.add_argument('--nvd-api-key', help='NVD API Key')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape CVE data')
    scrape_parser.add_argument('--days', type=int, default=7, help='Days back to scrape')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train model')
    train_parser.add_argument('--dataset', help='Dataset file path')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Start API server')
    api_parser.add_argument('--port', type=int, default=8000, help='Port number')
    api_parser.add_argument('--interface', choices=['fastapi', 'gradio'], default='fastapi', help='Interface type')
    
    # Schedule command
    schedule_parser = subparsers.add_parser('schedule', help='Start scheduler')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze CVE')
    analyze_parser.add_argument('cve_id', help='CVE ID to analyze')
    analyze_parser.add_argument('--instruction', default='Analyze this CVE', help='Analysis instruction')
    
    return parser

async def main():
    """Main function"""
    setup_logging()
    
    parser = create_cli()
    args = parser.parse_args()
    
    # Create CVE config
    config = CVEConfig.from_env()
    if hasattr(args, 'model'):
        config.model_name = args.model
    if hasattr(args, 'nvd_api_key') and args.nvd_api_key:
        config.nvd_api_key = args.nvd_api_key
    
    # Load ModelTrainerConfig if provided
    # trainer_config = None
    # if args.trainer_config:
        # trainer_config = ModelTrainerConfig.from_file(args.trainer_config)
    trainer_config = ModelTrainerConfig.from_env()

    if args.command == 'setup':
        print("Setting up CVE Analyst System...")
        
        # Initialize scrapers and generate initial dataset
        scraper = CVEScraper(config)
        dataset_generator = DatasetGenerator(config)
        
        # Scrape initial data
        print("Scraping initial CVE data...")
        await scraper.scrape_nvd_cves(days_back=30)
        scraper.scrape_exploit_db()
        
        # Generate dataset
        print("Generating training dataset...")
        dataset = dataset_generator.generate_instruction_dataset()
        dataset_generator.save_dataset(dataset, "initial_dataset.json")
        
        print("Setup completed successfully!")
    
    elif args.command == 'scrape':
        scraper = CVEScraper(config)
        print(f"Scraping CVE data for last {args.days} days...")
        await scraper.scrape_nvd_cves(days_back=args.days)
        scraper.scrape_exploit_db()
        print("Scraping completed!")
    
    elif args.command == 'train':
        trainer = CVEModelTrainer(config)
        dataset_generator = DatasetGenerator(config)
        
        if args.dataset:
            dataset = trainer.load_dataset_from_file(args.dataset)
        else:
            dataset = dataset_generator.generate_instruction_dataset()
        
        print("Starting model training...")
        trainer.train_model(dataset)
        print("Training completed!")

    elif args.command == 'api-cve':
        if args.interface == 'fastapi':
            
            app = create_fastapi_app(config)
            print(f"Starting FastAPI server on port {args.port}")
            config = Config(app=app, host="0.0.0.0", port=args.port)
            server = Server(config)
            await server.serve()
            # uvicorn.run(app, host="0.0.0.0", port=args.port)
        else:
            interface = create_gradio_interface(config)
            print(f"Starting Gradio interface on port {args.port}")
            interface.launch(server_name="0.0.0.0", server_port=args.port, share=False)

    elif args.command == 'api':
        if args.interface == 'fastapi':
            
            app = create_fastapi_app(trainer_config)
            print(f"Starting FastAPI server on port {args.port}")
            config = Config(app=app, host="0.0.0.0", port=args.port)
            server = Server(config)
            await server.serve()
            # uvicorn.run(app, host="0.0.0.0", port=args.port)
        else:
            interface = create_gradio_interface(trainer_config)
            print(f"Starting Gradio interface on port {args.port}")
            interface.launch(server_name="0.0.0.0", server_port=args.port, share=True)
    
    elif args.command == 'schedule':
        scheduler = CVEScheduler(config)
        print("Starting background scheduler...")
        scheduler.start_scheduler()
    
    elif args.command == 'analyze':
        api = CVEAnalystAPI(config)
        print(f"Analyzing {args.cve_id}...")
        result = api.analyze_cve(args.cve_id, args.instruction)
        print("\n" + "="*50)
        print("ANALYSIS RESULT:")
        print("="*50)
        print(result)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
