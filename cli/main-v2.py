"""
Command Line Interface for CVE Analyst System
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# from config.settings import CVEConfig
from config.settings import ModelTrainerConfig

# from scrapers.cve_scraper import CVEScraper
# from data.dataset_generator import DatasetGenerator
# from training.model_trainer import CVEModelTrainer
# from api.cve_analyst_api import CVEAnalystAPI

# from api.fastapi_app import create_fastapi_app
from api.gradio_app import create_gradio_interface
# from scheduler.cve_scheduler import CVEScheduler
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
    
    # Create config
    config = ModelTrainerConfig
    # if hasattr(args, 'model'):
    #     config.model_name = args.model
    # if hasattr(args, 'nvd_api_key') and args.nvd_api_key:
    #     config.nvd_api_key = args.nvd_api_key
    
    if args.command == 'api':
        interface = create_gradio_interface(config)
        print(f"Starting Gradio interface on port {args.port}")
        interface.launch(server_name="0.0.0.0", server_port=args.port, share=False)
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
