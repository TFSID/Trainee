#!/bin/bash

# CVE Analyst System - Quick Install Script
# Usage: curl -sSL https://raw.githubusercontent.com/your-repo/cve-analyst/main/scripts/quick-install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo -e "${BLUE}"
cat &lt;&lt; "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    CVE ANALYST SYSTEM                        ║
║                   Quick Install Script                       ║
║                                                              ║
║  🚀 One-command installation                                 ║
║  🔍 AI-powered CVE analysis                                  ║
║  🤖 Ready in minutes                                         ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check prerequisites
print_step "Checking prerequisites..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi
print_success "Python 3 found"

# Check Docker
if ! command -v docker &> /dev/null; then
    print_warning "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    print_success "Docker installed"
else
    print_success "Docker found"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    if ! docker compose version &> /dev/null; then
        print_warning "Docker Compose not found. Installing..."
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        print_success "Docker Compose installed"
    else
        print_success "Docker Compose (v2) found"
    fi
else
    print_success "Docker Compose found"
fi

# Create project directory
PROJECT_DIR="cve-analyst-system"
print_step "Creating project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    print_warning "Directory $PROJECT_DIR already exists"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Download quickstart script
print_step "Downloading quickstart script..."
curl -sSL https://raw.githubusercontent.com/your-repo/cve-analyst/main/quickstart.py -o quickstart.py
chmod +x quickstart.py
print_success "Quickstart script downloaded"

# Download essential files
print_step "Downloading project files..."
curl -sSL https://raw.githubusercontent.com/your-repo/cve-analyst/main/docker-compose.yml -o docker-compose.yml
curl -sSL https://raw.githubusercontent.com/your-repo/cve-analyst/main/requirements.txt -o requirements.txt
curl -sSL https://raw.githubusercontent.com/your-repo/cve-analyst/main/Dockerfile -o Dockerfile

# Create .env file
print_step "Creating configuration..."
cat > .env &lt;&lt; EOF
# CVE Analyst System Configuration
NVD_API_KEY=
MODEL_NAME=deepseek-ai/deepseek-coder-1.3b-instruct
API_PORT=8021
UI_PORT=7860
MAX_LENGTH=2048
BATCH_SIZE=4
UPDATE_INTERVAL_HOURS=6
LOG_LEVEL=INFO
EOF

# Ask for NVD API key
echo
read -p "Enter your NVD API Key (optional, press Enter to skip): " nvd_key
if [ ! -z "$nvd_key" ]; then
    sed -i "s/NVD_API_KEY=/NVD_API_KEY=$nvd_key/" .env
    print_success "NVD API Key configured"
fi

# Run quickstart
print_step "Starting CVE Analyst System..."
python3 quickstart.py --docker --auto

# Final message
echo
print_success "Installation completed!"
echo -e "${GREEN}🎉 CVE Analyst System is now running!${NC}"
echo
echo -e "${BLUE}Access your system:${NC}"
echo -e "📊 Web Interface: ${YELLOW}http://localhost:7860${NC}"
echo -e "🔌 API Endpoint:  ${YELLOW}http://localhost:8000${NC}"
echo -e "📚 API Docs:      ${YELLOW}http://localhost:8000/docs${NC}"
echo
echo -e "${BLUE}Quick commands:${NC}"
echo -e "• Check status:   ${YELLOW}python3 quickstart.py status${NC}"
echo -e "• Analyze CVE:    ${YELLOW}python3 quickstart.py analyze CVE-2024-1234${NC}"
echo -e "• View logs:      ${YELLOW}python3 quickstart.py logs${NC}"
echo -e "• Restart:        ${YELLOW}python3 quickstart.py restart${NC}"
echo
echo -e "${GREEN}Happy analyzing! 🔍${NC}"
