# Whisper Real-time Transcription System

Real-time speech-to-text transcription using OpenAI Whisper Large-v3 on AWS GPU.

## 🎯 Features

✅ Real-time audio streaming with live transcription  
✅ Audio file upload (.mp3, .wav, .m4a, .ogg)  
✅ 99 languages support with auto-detection  
✅ WebSocket-based API  
✅ Beautiful web interface  
✅ Word-level timestamps  
✅ GPU-accelerated (25-30x real-time factor)  

## 📋 Requirements

- **AWS EC2**: g4dn.xlarge instance
- **OS**: Ubuntu 22.04
- **GPU**: NVIDIA T4 (16GB VRAM)
- **CUDA**: 12+ with cuDNN 9

## 🚀 Quick Setup (5 Steps)

### Step 1: Launch AWS EC2 Instance

1. Go to **AWS Console → EC2 → Launch Instance**

2. **Configure:**
   ```
   Name: whisper-transcription-server
   AMI: Deep Learning Base OSS Nvidia Driver GPU AMI (Ubuntu 22.04)
   Instance Type: g4dn.xlarge
   Storage: 100 GB gp3
   ```

3. **Security Group - Add Inbound Rules:**
   ```
   SSH         - Port 22   - Your IP
   Custom TCP  - Port 8000 - 0.0.0.0/0 (WebSocket)
   Custom TCP  - Port 8080 - 0.0.0.0/0 (Web Client)
   ```

4. **Launch instance** and note your **Public IP address**

### Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### Step 3: Upload Project Files

```bash
# On your local machine
scp -i your-key.pem whisper-transcription.zip ubuntu@YOUR_EC2_PUBLIC_IP:~

# On EC2 instance
cd ~
unzip whisper-transcription.zip
cd whisper-transcription
```

### Step 4: Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

**What this does:**
- Installs system dependencies (ffmpeg, portaudio, etc.)
- Installs Python packages (faster-whisper, websockets, etc.)
- Downloads Whisper large-v3 model (~3GB)
- Verifies GPU setup

**Time required:** 5-10 minutes

### Step 5: Update Server IP & Start

```bash
# Update WebSocket URL in index.html with your EC2 IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
sed -i "s/YOUR_SERVER_IP/$EC2_IP/g" index.html

# Start WebSocket server (Terminal 1)
python whisper_server.py

# Start web client server (Terminal 2 - open new SSH session)
python serve_client.py
```

### Step 6: Test!

**Web Interface:**
```
http://YOUR_EC2_PUBLIC_IP:8080
```

**Python Client:**
```bash
# Download test audio
wget https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav -O test.wav

# Test file transcription
python test_client.py file test.wav

# Test streaming
python test_client.py stream test.wav
```

## 🎨 Using the Web Interface

### Real-time Recording
1. Click **"Connect to Server"**
2. Click **"Start Recording"**
3. Speak into your microphone
4. See live transcription appear
5. Click **"Stop Recording"** when done

### File Upload
1. Switch to **"File Upload"** tab
2. Drag & drop audio file or click to browse
3. Click **"Upload & Transcribe"**
4. View results with timestamps

## 🔧 Production Deployment (Optional)

### Run as System Service

```bash
sudo ./install_service.sh
sudo systemctl start whisper
sudo systemctl start whisper-web
sudo systemctl status whisper
```

### View Logs
```bash
sudo journalctl -u whisper -f
```

### Auto-start on Boot
```bash
sudo systemctl enable whisper
sudo systemctl enable whisper-web
```

## 📊 Performance Benchmarks

| Metric | Value |
|--------|-------|
| Real-time Factor | 25-30x |
| 1 min audio | ~2-3 seconds |
| 10 min audio | ~20-30 seconds |
| VRAM usage | ~10GB |
| Accuracy (WER) | 2.7% (clean audio) |

## 💰 Cost Optimization

### Use Spot Instances (70% savings)
```
g4dn.xlarge On-Demand: $0.526/hour = $380/month
g4dn.xlarge Spot:      $0.15-0.20/hour = $108-144/month
```

### Auto-shutdown During Idle
```bash
# Add to crontab - shutdown at 10 PM daily
crontab -e
0 22 * * * sudo shutdown -h now
```

## 🐛 Troubleshooting

### Server Won't Start

```bash
# Check Python version (need 3.8+)
python3 --version

# Check CUDA/GPU
nvidia-smi

# Check dependencies
pip list | grep faster-whisper

# View detailed logs
tail -f /tmp/whisper_server.log
```

### Can't Connect from Browser

```bash
# Check server is running
ps aux | grep whisper_server

# Check ports are open
netstat -tuln | grep 8000
netstat -tuln | grep 8080

# Check firewall
sudo ufw status

# Allow ports if needed
sudo ufw allow 8000
sudo ufw allow 8080
```

### Poor Transcription Quality

- Ensure audio is **16kHz sample rate**
- Reduce background noise
- Speak clearly and at moderate pace
- Check microphone permissions in browser
- Try selecting language manually (don't use auto-detect)

### High GPU Memory Usage

```bash
# Monitor GPU in real-time
watch -n 1 nvidia-smi

# Restart server to clear memory
sudo systemctl restart whisper
```

### Model Download Fails

```bash
# Manually download model
python3 -c "from faster_whisper import WhisperModel; WhisperModel('large-v3')"

# Or set cache directory
export HF_HOME=/home/ubuntu/.cache
python whisper_server.py
```

## 📁 Project Structure

```
whisper-transcription/
├── README.md                  # This file
├── setup.sh                   # One-command setup script
├── whisper_server.py          # Main WebSocket server
├── serve_client.py            # Web client HTTP server
├── test_client.py             # Python test client
├── test_model.py              # Model verification script
├── index.html                 # Web interface
├── install_service.sh         # Systemd service installer
├── performance_test.py        # Performance benchmarking
├── API_DOCUMENTATION.md       # Complete API reference
└── TESTING_GUIDE.md          # Detailed testing instructions
```

## 🔌 API Integration

### WebSocket Protocol

**Connect:**
```javascript
const ws = new WebSocket('ws://your-server:8000');
```

**Send Audio File:**
```javascript
ws.send(JSON.stringify({
    type: 'file',
    audio: base64_encoded_audio,
    format: 'mp3',
    language: null  // auto-detect
}));
```

**Receive Transcript:**
```javascript
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.text);  // transcribed text
    console.log(data.language);  // detected language
};
```

See **API_DOCUMENTATION.md** for complete details.

## 🧪 Testing

### Quick Test
```bash
python test_client.py file test.wav
```

### Performance Test
```bash
python performance_test.py test.wav 10
```

### Full Test Suite
See **TESTING_GUIDE.md** for comprehensive testing instructions.

## 🌍 Supported Languages (99 total)

English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi, Dutch, Turkish, Polish, Swedish, Finnish, Czech, Greek, Hebrew, Indonesian, Thai, Vietnamese, and 76 more...

## 📚 Additional Documentation

- **API_DOCUMENTATION.md** - Complete WebSocket API reference
- **TESTING_GUIDE.md** - Testing procedures and examples
- **Faster-Whisper Docs**: https://github.com/SYSTRAN/faster-whisper
- **OpenAI Whisper**: https://github.com/openai/whisper

## ⚖️ License

This project uses:
- **OpenAI Whisper** - MIT License
- **faster-whisper** - MIT License

Free for commercial use with no restrictions.

## 🆘 Support

**Issues?**
1. Check troubleshooting section above
2. Review logs: `tail -f /tmp/whisper_server.log`
3. Verify GPU: `nvidia-smi`
4. Test connection: `telnet YOUR_IP 8000`

## 📝 Changelog

### v1.0.0 (2025-01-28)
- Initial release
- Real-time transcription via WebSocket
- File upload support
- Web interface
- Python client
- Complete documentation

## 🙏 Acknowledgments

- OpenAI for the Whisper model
- SYSTRAN for faster-whisper optimization
- AWS for GPU infrastructure

---

**Ready to transcribe!** 🎤→📝
