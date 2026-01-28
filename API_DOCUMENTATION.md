# Whisper WebSocket API Documentation

## 🔌 Connection

**Endpoint:** `ws://your-server-ip:8000`

**Protocol:** WebSocket

---

## 📨 Message Types

### 1. Real-time Audio Streaming

**Client → Server:**
```json
{
    "type": "stream",
    "audio": "base64_encoded_audio_data",
    "language": "en"  // optional, null for auto-detect
}
```

**Audio Format Requirements:**
- Sample Rate: 16000 Hz
- Channels: 1 (mono)
- Encoding: 16-bit PCM
- Format: Base64-encoded raw audio bytes

**Server → Client:**
```json
{
    "type": "transcript",
    "text": "transcribed text",
    "is_final": false,
    "language": "en",
    "duration": 3.5
}
```

---

### 2. File Upload

**Client → Server:**
```json
{
    "type": "file",
    "audio": "base64_encoded_file_content",
    "format": "mp3",  // or "wav", "m4a", "ogg"
    "language": null  // optional, null for auto-detect
}
```

**Server → Client:**
```json
{
    "type": "file_transcript",
    "text": "full transcription",
    "segments": [
        {
            "start": 0.0,
            "end": 2.5,
            "text": "Hello world"
        }
    ],
    "language": "en",
    "duration": 120.5,
    "processing_time": 4.2,
    "real_time_factor": 28.7
}
```

---

### 3. Stop Streaming

**Client → Server:**
```json
{
    "type": "stop"
}
```

**Server → Client:**
```json
{
    "type": "transcript",
    "text": "final transcribed text",
    "is_final": true,
    "language": "en"
}
```

---

### 4. Error Response

**Server → Client:**
```json
{
    "type": "error",
    "message": "error description"
}
```

---

## 🌍 Supported Languages

99 languages with auto-detection. Use ISO 639-1 codes or null for auto-detect.

**Common language codes:**
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `ru` - Russian
- `ja` - Japanese
- `ko` - Korean
- `zh` - Chinese
- `ar` - Arabic
- `hi` - Hindi

---

## 🚀 Performance

- **Real-time Factor:** 25-30x
- **Latency:** 2-4 seconds for 3-second chunks
- **Max file size:** Limited by WebSocket message size
- **Concurrent requests:** 1 per instance

---

## 💻 Code Examples

### JavaScript (Browser)

```javascript
const ws = new WebSocket('ws://your-server:8000');

ws.onopen = () => {
    console.log('Connected');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Transcript:', data.text);
};

// Send file
const file = document.getElementById('fileInput').files[0];
const reader = new FileReader();
reader.onload = (e) => {
    const base64Audio = e.target.result.split(',')[1];
    ws.send(JSON.stringify({
        type: 'file',
        audio: base64Audio,
        format: 'mp3'
    }));
};
reader.readAsDataURL(file);
```

### Python

```python
import asyncio
import websockets
import json
import base64

async def transcribe():
    uri = "ws://your-server:8000"
    async with websockets.connect(uri) as ws:
        # Read audio file
        with open('audio.mp3', 'rb') as f:
            audio_data = base64.b64encode(f.read()).decode()
        
        # Send for transcription
        await ws.send(json.dumps({
            'type': 'file',
            'audio': audio_data,
            'format': 'mp3'
        }))
        
        # Get result
        response = await ws.recv()
        result = json.loads(response)
        print(result['text'])

asyncio.run(transcribe())
```

---

## ⚠️ Error Handling

Common errors:

1. **Connection Failed**
   - Check server is running
   - Verify firewall allows port 8000

2. **Transcription Failed**
   - Invalid audio format
   - Corrupted audio data
   - Unsupported codec

3. **Out of Memory**
   - Audio file too large
   - Too many concurrent connections

---

## 🔒 Security Considerations

**⚠️ Not implemented (add for production):**
- Authentication (JWT/API keys)
- Rate limiting
- HTTPS/WSS encryption
- Input validation

---

## 🐛 Troubleshooting

### Client can't connect
```bash
# Check server is running
ps aux | grep whisper_server

# Check port is open
netstat -tuln | grep 8000

# Check firewall
sudo ufw status
```

### Poor transcription quality
- Ensure audio is 16kHz sample rate
- Use proper microphone
- Reduce background noise
- Check audio encoding

### High latency
- Reduce chunk size for real-time
- Check network bandwidth
- Verify GPU is being used
