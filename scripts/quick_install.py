#!/usr/bin/env python3
"""
CVE Analyst System - Quick Install Script (Python Version)
Cross-platform installer for CVE Analyst System

Usage: python quick_install.py
"""

import os
import sys
import subprocess
import platform
import urllib.request
import urllib.error
import shutil
from pathlib import Path
import getpass

# Colors for cross-platform terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows if not supported"""
        if platform.system() == 'Windows':
            # Try to enable ANSI colors on Windows 10+
            try:
                import colorama
                colorama.init()
            except ImportError:
                # Fallback: disable colors
                cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.NC = ''

Colors.disable_on_windows()

def print_step(message):
    print(f"{Colors.BLUE}[STEP]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.NC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.NC}")

def print_banner():
    """Print installation banner"""
    banner = f"""{Colors.BLUE}
╔══════════════════════════════════════════════════════════════╗
║                    CVE ANALYST SYSTEM                        ║
║                   Quick Install Script                       ║
║                                                              ║
║  🚀 One-command installation                                 ║
║  🔍 AI-powered CVE analysis                                  ║
║  🤖 Ready in minutes                                         ║
╚══════════════════════════════════════════════════════════════╝
{Colors.NC}"""
    print(banner)

def run_command(command, shell=True, check=True):
    """Run system command with error handling"""
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=shell, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, 
                                  capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except FileNotFoundError:
        return False, "", "Command not found"

def check_command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def download_file(url, filename):
    """Download file from URL"""
    try:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filename)
        return True
    except urllib.error.URLError as e:
        print_error(f"Failed to download {filename}: {e}")
        return False

def is_admin():
    """Check if running with admin privileges"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def check_prerequisites():
    """Check system prerequisites"""
    print_step("Checking prerequisites...")
    
    # Check if running as admin/root
    if is_admin():
        print_error("This script should not be run as administrator/root")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print_error("Python 3.7+ is required")
        sys.exit(1)
    print_success(f"Python {sys.version.split()[0]} found")
    
    # Check pip
    if not check_command_exists('pip') and not check_command_exists('pip3'):
        print_error("pip is required but not found")
        sys.exit(1)
    print_success("pip found")
    
    return True

def install_docker():
    """Install Docker based on platform"""
    system = platform.system().lower()
    
    if system == 'linux':
        print_warning("Docker not found. Please install Docker manually:")
        print("curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh")
        print("sudo usermod -aG docker $USER")
        print("Then logout and login again, or run: newgrp docker")
        
    elif system == 'darwin':  # macOS
        print_warning("Docker not found. Please install Docker Desktop for macOS:")
        print("https://docs.docker.com/desktop/install/mac-install/")
        
    elif system == 'windows':
        print_warning("Docker not found. Please install Docker Desktop for Windows:")
        print("https://docs.docker.com/desktop/install/windows-install/")
    
    response = input("Have you installed Docker? Continue? (y/N): ").lower()
    return response.startswith('y')

def check_docker():
    """Check Docker installation"""
    if not check_command_exists('docker'):
        print_warning("Docker not found.")
        return install_docker()
    
    # Test docker command
    success, stdout, stderr = run_command('docker --version')
    if not success:
        print_error("Docker is installed but not working properly")
        print_error(f"Error: {stderr}")
        return False
    
    print_success(f"Docker found: {stdout.strip()}")
    return True

def check_docker_compose():
    """Check Docker Compose installation"""
    # Check for docker-compose command
    if check_command_exists('docker-compose'):
        success, stdout, stderr = run_command('docker-compose --version')
        if success:
            print_success(f"Docker Compose found: {stdout.strip()}")
            return True
    
    # Check for docker compose (v2)
    success, stdout, stderr = run_command('docker compose version')
    if success:
        print_success(f"Docker Compose (v2) found: {stdout.strip()}")
        return True
    
    print_warning("Docker Compose not found or not working")
    print("Please ensure Docker Compose is installed with Docker Desktop")
    return False

def create_project_directory():
    """Create and setup project directory"""
    project_dir = "cve-analyst-system"
    print_step(f"Creating project directory: {project_dir}")
    
    project_path = Path(project_dir)
    
    if project_path.exists():
        print_warning(f"Directory {project_dir} already exists")
        response = input("Do you want to continue? (y/N): ").lower()
        if not response.startswith('y'):
            sys.exit(1)
    
    project_path.mkdir(exist_ok=True)
    os.chdir(project_path)
    print_success(f"Working in directory: {project_path.absolute()}")
    return project_path

def download_project_files():
    """Download essential project files"""
    print_step("Downloading project files...")
    
    base_url = "https://raw.githubusercontent.com/your-repo/cve-analyst/main"
    files = {
        "quickstart.py": f"{base_url}/quickstart.py",
        "docker-compose.yml": f"{base_url}/docker-compose.yml",
        "requirements.txt": f"{base_url}/requirements.txt",
        "Dockerfile": f"{base_url}/Dockerfile"
    }
    
    success_count = 0
    for filename, url in files.items():
        if download_file(url, filename):
            success_count += 1
        else:
            print_warning(f"Failed to download {filename}, continuing...")
    
    if success_count > 0:
        print_success(f"Downloaded {success_count}/{len(files)} files")
        
        # Make quickstart.py executable
        quickstart_path = Path("quickstart.py")
        if quickstart_path.exists():
            quickstart_path.chmod(0o755)
    
    return success_count > 0

def create_env_file():
    """Create .env configuration file"""
    print_step("Creating configuration...")
    
    env_content = """# CVE Analyst System Configuration
NVD_API_KEY=
MODEL_NAME=deepseek-ai/deepseek-coder-1.3b-instruct
API_PORT=8021
UI_PORT=7860
MAX_LENGTH=2048
BATCH_SIZE=4
UPDATE_INTERVAL_HOURS=6
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # Ask for NVD API key
    print()
    nvd_key = getpass.getpass("Enter your NVD API Key (optional, press Enter to skip): ").strip()
    
    if nvd_key:
        # Update .env file
        with open('.env', 'r') as f:
            content = f.read()
        
        content = content.replace('NVD_API_KEY=', f'NVD_API_KEY={nvd_key}')
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print_success("NVD API Key configured")

def install_python_requirements():
    """Install Python requirements if requirements.txt exists"""
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        print_step("Installing Python requirements...")
        pip_cmd = 'pip3' if check_command_exists('pip3') else 'pip'
        success, stdout, stderr = run_command(f'{pip_cmd} install -r requirements.txt')
        
        if success:
            print_success("Python requirements installed")
        else:
            print_warning("Failed to install some Python requirements")
            print_warning("You may need to install them manually")

def start_system():
    """Start the CVE Analyst System"""
    print_step("Starting CVE Analyst System...")
    
    quickstart_file = Path("quickstart.py")
    if quickstart_file.exists():
        # Try to run the quickstart script
        success, stdout, stderr = run_command([sys.executable, "quickstart.py", "--docker", "--auto"], 
                                            check=False)
        if success:
            print_success("CVE Analyst System started successfully!")
        else:
            print_warning("Quickstart script encountered issues")
            print("You can try running it manually: python quickstart.py --docker")
    else:
        print_warning("Quickstart script not found. You'll need to start the system manually.")
        print("Try: docker-compose up -d")

def print_final_message():
    """Print final success message and instructions"""
    print()
    print_success("Installation completed!")
    print(f"{Colors.GREEN}🎉 CVE Analyst System is now running!{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Access your system:{Colors.NC}")
    print(f"📊 Web Interface: {Colors.YELLOW}http://localhost:7860{Colors.NC}")
    print(f"🔌 API Endpoint:  {Colors.YELLOW}http://localhost:8000{Colors.NC}")
    print(f"📚 API Docs:      {Colors.YELLOW}http://localhost:8000/docs{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Quick commands:{Colors.NC}")
    print(f"• Check status:   {Colors.YELLOW}python quickstart.py status{Colors.NC}")
    print(f"• Analyze CVE:    {Colors.YELLOW}python quickstart.py analyze CVE-2024-1234{Colors.NC}")
    print(f"• View logs:      {Colors.YELLOW}python quickstart.py logs{Colors.NC}")
    print(f"• Restart:        {Colors.YELLOW}python quickstart.py restart{Colors.NC}")
    print()
    print(f"{Colors.GREEN}Happy analyzing! 🔍{Colors.NC}")

def main():
    """Main installation function"""
    try:
        print_banner()
        
        # Check prerequisites
        check_prerequisites()
        
        # Check Docker
        if not check_docker():
            print_error("Docker installation required. Please install Docker and try again.")
            sys.exit(1)
        
        # Check Docker Compose
        if not check_docker_compose():
            print_error("Docker Compose is required. Please ensure it's properly installed.")
            sys.exit(1)
        
        # Create project directory
        project_path = create_project_directory()
        
        # Download project files
        if not download_project_files():
            print_warning("Some files failed to download. You may need to download them manually.")
        
        # Create configuration
        create_env_file()
        
        # Install Python requirements
        install_python_requirements()
        
        # Start system
        start_system()
        
        # Print final instructions
        print_final_message()
        
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()