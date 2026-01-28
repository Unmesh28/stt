# Testing Guide

## 🚀 Quick Start Tests

### 1. Start Servers

```bash
# Terminal 1: WebSocket server
python whisper_server.py

# Terminal 2: Web client server  
python serve_client.py
```

**Expected output:**
```
Whisper WebSocket Server Starting...
✓ Server is running on ws://0.0.0.0:8000
✓ Ready to accept connections
```

---

## 🌐 Test Web Interface

1. Open browser: `http://YOUR_EC2_IP:8080`

2. **Test Real-time Recording:**
   - Click "Connect to Server"
   - Click "Start Recording"
   - Speak into microphone
   - See live transcription
   - Click "Stop Recording"

3. **Test File Upload:**
   - Switch to "File Upload" tab
   - Drag & drop audio file
   - Click "Upload & Transcribe"
   - View results with timestamps

---

## 🐍 Test Python Client

### Download Sample Audio
```bash
wget https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav -O test.wav
```

### Test File Mode
```bash
python test_client.py file test.wav
```

**Expected output:**
```
Connecting to ws://localhost:8000...
✓ Connected successfully
Transcribing file: test.wav
Sending file to server...
Waiting for transcription...

======================================================================
TRANSCRIPTION RESULT
======================================================================
Language: EN
Duration: 10.50s
Processing Time: 0.42s
Real-time Factor: 25.0x
======================================================================
```

### Test Stream Mode
```bash
python test_client.py stream test.wav
```

---

## 📊 Performance Testing

```bash
python performance_test.py test.wav 10
```

**Expected output:**
```
Running 10 performance tests with test.wav...
============================================================
Test  1:   2.15s ✓
Test  2:   2.08s ✓
Test  3:   2.12s ✓
...
============================================================
Average: 2.11s
Min:     2.05s
Max:     2.20s
Median:  2.10s
```

---

## 🖥️ Monitor GPU Usage

```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# Expected:
# - GPU utilization: 50-70% during transcription
# - Memory usage: ~10GB
# - Temperature: 60-75°C
```

---

## 📝 Check Logs

```bash
# Server logs
tail -f /tmp/whisper_server.log

# System logs
sudo journalctl -u whisper -f

# Error logs
tail -f /var/log/whisper-error.log
```

---

## ✅ Expected Results

### Real-time Streaming
- Latency: 2-4 seconds
- Accuracy: High for clear speech
- GPU Usage: 50-70%

### File Upload
- 1 minute audio: ~2-3 seconds
- 10 minute audio: ~20-30 seconds
- Real-time Factor: 25-30x

---

## 🐛 Troubleshooting

### No audio in browser
```bash
# Check microphone permissions
# Try different browser (Chrome/Firefox)
# Check browser console for errors
```

### Slow transcription
```bash
# Verify GPU is being used
nvidia-smi

# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Monitor system resources
htop
```

### Connection refused
```bash
# Verify server is running
ps aux | grep whisper_server

# Check firewall
sudo ufw allow 8000
sudo ufw allow 8080

# Test connection
telnet YOUR_IP 8000
```

### Poor quality transcription
- Ensure 16kHz audio
- Reduce background noise
- Speak clearly
- Try manual language selection

---

## 🔄 Full Test Sequence

```bash
# 1. Start servers
python whisper_server.py &
python serve_client.py &

# 2. Download test file
wget https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav -O test.wav

# 3. Run all tests
python test_client.py file test.wav
python test_client.py stream test.wav
python performance_test.py test.wav 5

# 4. Open web interface
echo "Open: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080"
```

---

## 📈 Benchmark Your Setup

Create `benchmark.sh`:
```bash
#!/bin/bash
echo "Benchmarking Whisper Setup..."
echo "=============================="

# Test 1: Short audio (30s)
echo "Test 1: Short audio"
time python test_client.py file test.wav

# Test 2: Performance test
echo "Test 2: Performance test"
python performance_test.py test.wav 5

# Test 3: GPU check
echo "Test 3: GPU status"
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv

echo "=============================="
echo "Benchmark complete!"
```

Run with:
```bash
chmod +x benchmark.sh
./benchmark.sh
```

---

See **README.md** for setup instructions.
See **API_DOCUMENTATION.md** for API details.
