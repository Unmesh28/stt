#!/bin/bash

set -e

echo "============================================================"
echo "Whisper Real-time Transcription - Setup Script"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Update system
echo -e "${YELLOW}[1/7] Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo -e "${YELLOW}[2/7] Installing system dependencies...${NC}"
sudo apt install -y \
    ffmpeg \
    portaudio19-dev \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    unzip \
    htop

# Upgrade pip
echo -e "${YELLOW}[3/7] Upgrading pip...${NC}"
pip install --upgrade pip

# Install Python packages
echo -e "${YELLOW}[4/7] Installing Python packages...${NC}"
pip install faster-whisper
pip install websockets
pip install numpy
pip install soundfile
pip install aiofiles

# Verify CUDA
echo -e "${YELLOW}[5/7] Verifying CUDA installation...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU detected:${NC}"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv
else
    echo -e "${YELLOW}⚠ Warning: NVIDIA GPU not detected. CPU mode will be very slow.${NC}"
fi

# Download and cache model
echo -e "${YELLOW}[6/7] Downloading Whisper large-v3 model (~3GB)...${NC}"
echo "This may take 5-10 minutes depending on your connection..."
python3 << 'PYEOF'
from faster_whisper import WhisperModel
print("Downloading model...")
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
print("✓ Model downloaded and cached successfully")
PYEOF

# Test installation
echo -e "${YELLOW}[7/7] Testing installation...${NC}"
python3 test_model.py

echo ""
echo "============================================================"
echo -e "${GREEN}✓ Setup completed successfully!${NC}"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Update server IP: sed -i 's/YOUR_SERVER_IP/YOUR_EC2_IP/g' index.html"
echo "2. Start server: python whisper_server.py"
echo "3. Start web client: python serve_client.py"
echo "4. Open browser: http://YOUR_EC2_IP:8080"
echo ""
