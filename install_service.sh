#!/bin/bash

echo "Installing Whisper as systemd service..."

# Create service file
sudo tee /etc/systemd/system/whisper.service > /dev/null << SERVICEEOF
[Unit]
Description=Whisper WebSocket Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/whisper_server.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/whisper.log
StandardError=append:/var/log/whisper-error.log

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Create web client service
sudo tee /etc/systemd/system/whisper-web.service > /dev/null << WEBEOF
[Unit]
Description=Whisper Web Client Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/serve_client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
WEBEOF

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable whisper.service
sudo systemctl enable whisper-web.service

echo "✓ Services installed"
echo ""
echo "Start services with:"
echo "  sudo systemctl start whisper"
echo "  sudo systemctl start whisper-web"
echo ""
echo "Check status with:"
echo "  sudo systemctl status whisper"
echo "  sudo systemctl status whisper-web"
echo ""
echo "View logs with:"
echo "  sudo journalctl -u whisper -f"
