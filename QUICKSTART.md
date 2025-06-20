# CVE Analyst System - Quick Start Guide

Panduan cepat untuk menjalankan CVE Analyst System dalam hitungan menit.

## 🚀 Quick Start Options

### Option 1: Docker Quick Start (Recommended)
```bash
# Clone dan jalankan dengan satu perintah
git clone <repository-url>
cd cve-analyst
python quickstart.py --docker
```

### Option 2: Local Quick Start
\`\`\`bash
# Setup lokal tanpa Docker
python quickstart.py --local
\`\`\`

### Option 3: Manual Setup
\`\`\`bash
# Setup manual step-by-step
python quickstart.py --manual
\`\`\`

## 📋 Prerequisites

### For Docker Setup:
- Docker & Docker Compose
- Python 3.8+ (untuk quickstart script)

### For Local Setup:
- Python 3.8+
- 8GB+ RAM (untuk model training)
- 10GB+ disk space

## ⚡ Super Quick Start (1 Minute)

\`\`\`bash
# Download quickstart script
curl -O https://raw.githubusercontent.com/your-repo/cve-analyst/main/quickstart.py

# Run dengan Docker (otomatis setup semua)
python quickstart.py --docker --auto

# Akses aplikasi:
# - API: http://localhost:8000
# - Web UI: http://localhost:7860
\`\`\`

## 🔧 Configuration

### Environment Variables (Optional)
\`\`\`bash
export NVD_API_KEY="your_nvd_api_key"          # Optional, untuk rate limit lebih tinggi
export MODEL_NAME="deepseek-ai/deepseek-coder-1.3b-instruct"
export OPENAI_API_KEY="your_openai_key"        # Optional, untuk fallback analysis
\`\`\`

### Quick Config File
Buat file `.env`:
\`\`\`bash
NVD_API_KEY=your_nvd_api_key_here
MODEL_NAME=deepseek-ai/deepseek-coder-1.3b-instruct
MAX_LENGTH=2048
BATCH_SIZE=4
UPDATE_INTERVAL_HOURS=6
\`\`\`

## 🎯 Usage Examples

### 1. Analyze CVE via CLI
\`\`\`bash
# Setelah setup selesai
python quickstart.py analyze CVE-2024-1234
\`\`\`

### 2. Analyze CVE via API
\`\`\`bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"cve_id": "CVE-2024-1234", "instruction": "Provide detailed security analysis"}'
\`\`\`

### 3. Web Interface
Buka browser: `http://localhost:7860`

## 📊 What You Get

### Immediate Access:
- ✅ CVE Database dengan 30 hari data terbaru
- ✅ Web interface untuk analisis CVE
- ✅ REST API endpoints
- ✅ Automated data updates (setiap 12 jam)
- ✅ Basic AI model untuk analisis

### After Training (30-60 minutes):
- ✅ Fine-tuned model untuk analisis lebih akurat
- ✅ Custom security recommendations
- ✅ Advanced threat intelligence

## 🔍 Verification

### Check System Status:
\`\`\`bash
# Health check
curl http://localhost:8000/health

# Recent CVEs
curl http://localhost:8000/recent-cves

# Database status
python quickstart.py status
\`\`\`

### Expected Output:
\`\`\`json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "model_loaded": true,
  "database_records": 1500,
  "last_update": "2024-01-15T06:00:00"
}
\`\`\`

## 🛠️ Troubleshooting

### Common Issues:

#### 1. Port Already in Use
\`\`\`bash
# Change ports
python quickstart.py --docker --api-port 8001 --ui-port 7861
\`\`\`

#### 2. Memory Issues
\`\`\`bash
# Use smaller model
export MODEL_NAME="deepseek-ai/deepseek-coder-1.3b-instruct"
python quickstart.py --local --light-mode
\`\`\`

#### 3. Network Issues
\`\`\`bash
# Use offline mode (pre-downloaded data)
python quickstart.py --offline
\`\`\`

#### 4. Docker Issues
\`\`\`bash
# Reset Docker environment
python quickstart.py --docker --reset
\`\`\`

## 📈 Next Steps

### 1. Customize Analysis
\`\`\`bash
# Edit analysis templates
nano config/analysis_templates.json

# Restart services
python quickstart.py restart
\`\`\`

### 2. Add Data Sources
\`\`\`bash
# Add custom threat feeds
python quickstart.py add-feed --url "https://your-threat-feed.com/api"
\`\`\`

### 3. Schedule Updates
\`\`\`bash
# Setup cron jobs
python quickstart.py setup-cron
\`\`\`

### 4. Scale Up
\`\`\`bash
# Multi-node deployment
python quickstart.py scale --nodes 3
\`\`\`

## 🔒 Security Notes

- Default setup menggunakan SQLite (development only)
- Untuk production, gunakan PostgreSQL/MySQL
- API tidak memiliki authentication by default
- Aktifkan HTTPS untuk production deployment

## 📚 Advanced Usage

### Custom Model Training
\`\`\`bash
# Train dengan dataset custom
python quickstart.py train --dataset custom_data.json --epochs 5
\`\`\`

### Batch Analysis
\`\`\`bash
# Analyze multiple CVEs
python quickstart.py batch-analyze --file cve_list.txt
\`\`\`

### Export Results
\`\`\`bash
# Export analysis results
python quickstart.py export --format json --output results.json
\`\`\`

## 🆘 Support

### Quick Help:
\`\`\`bash
python quickstart.py --help
\`\`\`

### Logs:
\`\`\`bash
# View logs
python quickstart.py logs

# Debug mode
python quickstart.py --debug
\`\`\`

### Reset Everything:
\`\`\`bash
# Complete reset
python quickstart.py reset --all
\`\`\`

## 📋 Checklist

- [ ] Prerequisites installed
- [ ] Environment variables set (optional)
- [ ] Quickstart script downloaded
- [ ] System running (`python quickstart.py status`)
- [ ] API accessible (`curl http://localhost:8000/health`)
- [ ] Web UI accessible (`http://localhost:7860`)
- [ ] Sample CVE analyzed
- [ ] Scheduled updates configured

## ⏱️ Timeline

| Task | Time | Description |
|------|------|-------------|
| Initial Setup | 2-5 min | Download, install, start services |
| Data Collection | 5-10 min | Scrape initial CVE data |
| Basic Analysis | Immediate | Use pre-trained model |
| Model Training | 30-60 min | Fine-tune for better accuracy |
| Full System | 1-2 hours | Complete setup with all features |

---

**Need help?** Run `python quickstart.py --help` or check the troubleshooting section above.
\`\`\`

```python file="quickstart.py"
#!/usr/bin/env python3
"""
CVE Analyst System - Quick Start Script
Automated setup dan deployment untuk CVE Analyst System
"""

import os
import sys
import json
import time
import argparse
import subprocess
import requests
from pathlib import Path
from typing import Dict, List, Optional
import shutil

class Colors:
    """ANSI color codes untuk output yang menarik"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class QuickStart:
    """Main QuickStart class"""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration dari environment dan file"""
        config = {
            'nvd_api_key': os.getenv('NVD_API_KEY', ''),
            'model_name': os.getenv('MODEL_NAME', 'deepseek-ai/deepseek-coder-1.3b-instruct'),
            'api_port': int(os.getenv('API_PORT', '8000')),
            'ui_port': int(os.getenv('UI_PORT', '7860')),
            'max_length': int(os.getenv('MAX_LENGTH', '2048')),
            'batch_size': int(os.getenv('BATCH_SIZE', '4')),
            'update_interval': int(os.getenv('UPDATE_INTERVAL_HOURS', '6'))
        }
        
        # Load dari .env file jika ada
        env_file = self.project_dir / '.env'
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key.lower()] = value
        
        return config
    
    def print_banner(self):
        """Print welcome banner"""
        banner = f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    CVE ANALYST SYSTEM                        ║
║                     Quick Start Script                       ║
║                                                              ║
║  🚀 Automated setup untuk CVE analysis dengan AI            ║
║  🔍 Real-time vulnerability intelligence                     ║
║  🤖 DeepSeek-Coder powered analysis                         ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}
        """
        print(banner)
    
    def print_step(self, step: str, description: str = ""):
        """Print step dengan formatting"""
        print(f"{Colors.OKBLUE}[STEP]{Colors.ENDC} {Colors.BOLD}{step}{Colors.ENDC}")
        if description:
            print(f"       {description}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
    
    def check_prerequisites(self, mode: str = "docker") -> bool:
        """Check system prerequisites"""
        self.print_step("Checking Prerequisites")
        
        # Check Python
        python_version = sys.version_info
        if python_version.major &lt; 3 or python_version.minor &lt; 8:
            self.print_error("Python 3.8+ required")
            return False
        self.print_success(f"Python {python_version.major}.{python_version.minor} ✓")
        
        if mode == "docker":
            # Check Docker
            try:
                result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.print_success("Docker ✓")
                else:
                    self.print_error("Docker not found")
                    return False
            except FileNotFoundError:
                self.print_error("Docker not installed")
                return False
            
            # Check Docker Compose
            try:
                result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.print_success("Docker Compose ✓")
                else:
                    # Try docker compose (newer version)
                    result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        self.print_success("Docker Compose (v2) ✓")
                    else:
                        self.print_error("Docker Compose not found")
                        return False
            except FileNotFoundError:
                self.print_error("Docker Compose not installed")
                return False
        
        return True
    
    def create_project_structure(self):
        """Create project directory structure"""
        self.print_step("Creating Project Structure")
        
        directories = [
            'config', 'database', 'scrapers', 'data', 'training',
            'api', 'scheduler', 'utils', 'cli', 'logs', 'cve_data', 'models'
        ]
        
        for directory in directories:
            dir_path = self.project_dir / directory
            dir_path.mkdir(exist_ok=True)
            
        self.print_success("Project structure created")
    
    def create_env_file(self):
        """Create .env file dengan konfigurasi"""
        self.print_step("Creating Environment Configuration")
        
        env_content = f"""# CVE Analyst System Configuration
NVD_API_KEY={self.config.get('nvd_api_key', '')}
MODEL_NAME={self.config['model_name']}
API_PORT={self.config['api_port']}
UI_PORT={self.config['ui_port']}
MAX_LENGTH={self.config['max_length']}
BATCH_SIZE={self.config['batch_size']}
UPDATE_INTERVAL_HOURS={self.config['update_interval']}

# Optional configurations
# OPENAI_API_KEY=your_openai_key_here
# DATABASE_URL=sqlite:///cve_database.db
# LOG_LEVEL=INFO
"""
        
        env_file = self.project_dir / '.env'
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        self.print_success("Environment file created")
    
    def setup_docker(self, auto_mode: bool = False):
        """Setup dengan Docker"""
        self.print_step("Setting up with Docker", "This may take 5-10 minutes...")
        
        # Create docker-compose.override.yml untuk custom ports
        override_content = f"""version: '3.8'
services:
  cve-analyst-api:
    ports:
      - "{self.config['api_port']}:8000"
    environment:
      - NVD_API_KEY={self.config.get('nvd_api_key', '')}
  
  cve-analyst-gradio:
    ports:
      - "{self.config['ui_port']}:7860"
"""
        
        with open(self.project_dir / 'docker-compose.override.yml', 'w') as f:
            f.write(override_content)
        
        # Build dan start services
        try:
            self.print_step("Building Docker images...")
            subprocess.run(['docker-compose', 'build'], check=True, cwd=self.project_dir)
            
            self.print_step("Starting services...")
            subprocess.run(['docker-compose', 'up', '-d'], check=True, cwd=self.project_dir)
            
            # Wait for services to be ready
            self.wait_for_services()
            
            if auto_mode:
                # Auto setup data
                self.setup_initial_data_docker()
            
            self.print_success("Docker setup completed!")
            self.print_service_urls()
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Docker setup failed: {e}")
            return False
        
        return True
    
    def setup_local(self, light_mode: bool = False):
        """Setup lokal tanpa Docker"""
        self.print_step("Setting up Local Environment")
        
        # Install requirements
        self.print_step("Installing Python dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                         check=True, cwd=self.project_dir)
            self.print_success("Dependencies installed")
        except subprocess.CalledProcessError:
            self.print_error("Failed to install dependencies")
            return False
        
        # Setup database
        self.print_step("Initializing database...")
        self.setup_database()
        
        # Initial data scraping
        if not light_mode:
            self.setup_initial_data_local()
        
        self.print_success("Local setup completed!")
        return True
    
    def setup_database(self):
        """Initialize database"""
        try:
            # Import dan initialize database
            sys.path.append(str(self.project_dir))
            from database.models import CVEDatabase
            
            db = CVEDatabase()
            self.print_success("Database initialized")
            
        except Exception as e:
            self.print_error(f"Database setup failed: {e}")
    
    def setup_initial_data_docker(self):
        """Setup initial data via Docker"""
        self.print_step("Setting up initial CVE data...")
        
        try:
            # Run scraper dalam container
            subprocess.run([
                'docker-compose', 'exec', '-T', 'cve-analyst-api',
                'python', 'cli/main.py', 'scrape', '--days', '7'
            ], check=True, cwd=self.project_dir)
            
            self.print_success("Initial data setup completed")
            
        except subprocess.CalledProcessError:
            self.print_warning("Initial data setup failed, but system is still functional")
    
    def setup_initial_data_local(self):
        """Setup initial data locally"""
        self.print_step("Scraping initial CVE data...")
        
        try:
            subprocess.run([
                sys.executable, 'cli/main.py', 'scrape', '--days', '7'
            ], check=True, cwd=self.project_dir)
            
            self.print_success("Initial data scraped")
            
        except subprocess.CalledProcessError:
            self.print_warning("Data scraping failed, but system is still functional")
    
    def wait_for_services(self, timeout: int = 120):
        """Wait for services to be ready"""
        self.print_step("Waiting for services to start...")
        
        api_url = f"http://localhost:{self.config['api_port']}/health"
        ui_url = f"http://localhost:{self.config['ui_port']}"
        
        start_time = time.time()
        while time.time() - start_time &lt; timeout:
            try:
                # Check API
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    self.print_success("API service ready")
                    break
            except requests.RequestException:
                pass
            
            print(".", end="", flush=True)
            time.sleep(2)
        else:
            self.print_warning("Services may still be starting...")
    
    def print_service_urls(self):
        """Print service URLs"""
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Services are running!{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📊 Web Interface: http://localhost:{self.config['ui_port']}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🔌 API Endpoint:  http://localhost:{self.config['api_port']}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}📚 API Docs:      http://localhost:{self.config['api_port']}/docs{Colors.ENDC}")
    
    def analyze_cve(self, cve_id: str, instruction: str = "Analyze this CVE"):
        """Analyze CVE via API"""
        self.print_step(f"Analyzing {cve_id}")
        
        api_url = f"http://localhost:{self.config['api_port']}/analyze"
        
        try:
            response = requests.post(api_url, json={
                "cve_id": cve_id,
                "instruction": instruction
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n{Colors.BOLD}Analysis Result:{Colors.ENDC}")
                print("=" * 60)
                print(result['analysis'])
                print("=" * 60)
            else:
                self.print_error(f"Analysis failed: {response.text}")
                
        except requests.RequestException as e:
            self.print_error(f"Failed to connect to API: {e}")
    
    def check_status(self):
        """Check system status"""
        self.print_step("Checking System Status")
        
        api_url = f"http://localhost:{self.config['api_port']}/health"
        
        try:
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                status = response.json()
                
                print(f"{Colors.OKGREEN}System Status: {status['status']}{Colors.ENDC}")
                print(f"Model Loaded: {'✅' if status.get('model_loaded') else '❌'}")
                print(f"Timestamp: {status['timestamp']}")
                
                # Check recent CVEs
                recent_url = f"http://localhost:{self.config['api_port']}/recent-cves?limit=5"
                recent_response = requests.get(recent_url, timeout=10)
                if recent_response.status_code == 200:
                    recent_cves = recent_response.json()
                    print(f"Recent CVEs: {len(recent_cves)} found")
                
                return True
            else:
                self.print_error("API not responding properly")
                return False
                
        except requests.RequestException:
            self.print_error("Cannot connect to API")
            return False
    
    def show_logs(self, service: str = "api"):
        """Show service logs"""
        try:
            if service == "api":
                subprocess.run(['docker-compose', 'logs', '-f', 'cve-analyst-api'], 
                             cwd=self.project_dir)
            elif service == "ui":
                subprocess.run(['docker-compose', 'logs', '-f', 'cve-analyst-gradio'], 
                             cwd=self.project_dir)
            else:
                subprocess.run(['docker-compose', 'logs', '-f'], cwd=self.project_dir)
        except KeyboardInterrupt:
            print("\nLog viewing stopped")
    
    def reset_system(self, full_reset: bool = False):
        """Reset system"""
        self.print_step("Resetting System")
        
        try:
            # Stop services
            subprocess.run(['docker-compose', 'down'], cwd=self.project_dir)
            
            if full_reset:
                # Remove volumes
                subprocess.run(['docker-compose', 'down', '-v'], cwd=self.project_dir)
                
                # Remove data directories
                for dir_name in ['cve_data', 'models', 'logs']:
                    dir_path = self.project_dir / dir_name
                    if dir_path.exists():
                        shutil.rmtree(dir_path)
                
                self.print_success("Full reset completed")
            else:
                self.print_success("System reset completed")
                
        except subprocess.CalledProcessError as e:
            self.print_error(f"Reset failed: {e}")
    
    def restart_services(self):
        """Restart services"""
        self.print_step("Restarting Services")
        
        try:
            subprocess.run(['docker-compose', 'restart'], cwd=self.project_dir)
            self.wait_for_services()
            self.print_success("Services restarted")
            self.print_service_urls()
        except subprocess.CalledProcessError as e:
            self.print_error(f"Restart failed: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="CVE Analyst System Quick Start")
    
    # Setup modes
    parser.add_argument('--docker', action='store_true', help='Setup dengan Docker')
    parser.add_argument('--local', action='store_true', help='Setup lokal')
    parser.add_argument('--manual', action='store_true', help='Manual step-by-step setup')
    
    # Options
    parser.add_argument('--auto', action='store_true', help='Automated setup dengan sample data')
    parser.add_argument('--light-mode', action='store_true', help='Setup ringan tanpa model training')
    parser.add_argument('--offline', action='store_true', help='Offline mode')
    parser.add_argument('--reset', action='store_true', help='Reset system')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    
    # Ports
    parser.add_argument('--api-port', type=int, default=8000, help='API port')
    parser.add_argument('--ui-port', type=int, default=7860, help='UI port')
    
    # Commands
    parser.add_argument('analyze', nargs='?', help='Analyze CVE')
    parser.add_argument('status', nargs='?', help='Check system status')
    parser.add_argument('logs', nargs='?', help='Show logs')
    parser.add_argument('restart', nargs='?', help='Restart services')
    
    args = parser.parse_args()
    
    # Initialize QuickStart
    qs = QuickStart()
    qs.config['api_port'] = args.api_port
    qs.config['ui_port'] = args.ui_port
    
    # Print banner
    qs.print_banner()
    
    # Handle commands
    if args.analyze:
        qs.analyze_cve(args.analyze)
        return
    
    if args.status:
        qs.check_status()
        return
    
    if args.logs:
        qs.show_logs()
        return
    
    if args.restart:
        qs.restart_services()
        return
    
    if args.reset:
        qs.reset_system(full_reset=True)
        return
    
    # Setup modes
    if args.docker:
        if not qs.check_prerequisites("docker"):
            sys.exit(1)
        
        qs.create_project_structure()
        qs.create_env_file()
        
        if qs.setup_docker(auto_mode=args.auto):
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Docker setup completed successfully!{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}Next steps:{Colors.ENDC}")
            print(f"1. Visit http://localhost:{qs.config['ui_port']} for web interface")
            print(f"2. Try: python quickstart.py analyze CVE-2024-1234")
            print(f"3. Check status: python quickstart.py status")
        
    elif args.local:
        if not qs.check_prerequisites("local"):
            sys.exit(1)
        
        qs.create_project_structure()
        qs.create_env_file()
        
        if qs.setup_local(light_mode=args.light_mode):
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Local setup completed!{Colors.ENDC}")
            print(f"\n{Colors.OKCYAN}To start services:{Colors.ENDC}")
            print(f"python cli/main.py api --port {qs.config['api_port']}")
    
    elif args.manual:
        print(f"{Colors.OKCYAN}Manual Setup Steps:{Colors.ENDC}")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Setup database: python cli/main.py setup")
        print("3. Scrape data: python cli/main.py scrape --days 7")
        print("4. Start API: python cli/main.py api")
        print("5. Start UI: python cli/main.py api --interface gradio")
    
    else:
        # Interactive mode
        print(f"{Colors.OKCYAN}Choose setup method:{Colors.ENDC}")
        print("1. Docker (Recommended)")
        print("2. Local Python")
        print("3. Manual")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            args.docker = True
            args.auto = True
            main()
        elif choice == "2":
            args.local = True
            main()
        elif choice == "3":
            args.manual = True
            main()
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
