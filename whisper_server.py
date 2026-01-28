import asyncio
import websockets
import json
import base64
import numpy as np
from faster_whisper import WhisperModel
import tempfile
import os
from datetime import datetime
import wave
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/whisper_server.log'),
        logging.StreamHandler()
    ]
)

class WhisperServer:
    def __init__(self):
        logging.info("Initializing Whisper Server...")
        self.model = WhisperModel(
            "large-v3",
            device="cuda",
            compute_type="float16",
            download_root="/home/ubuntu/.cache/whisper"
        )
        logging.info("✓ Model loaded successfully")
        
        # Audio buffer for real-time streaming
        self.audio_buffers = {}
        
    async def handle_realtime_stream(self, websocket, data):
        """Handle real-time audio streaming"""
        client_id = id(websocket)
        
        # Initialize buffer for this client if needed
        if client_id not in self.audio_buffers:
            self.audio_buffers[client_id] = []
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(data['audio'])
        
        # Convert bytes to numpy array (assuming 16-bit PCM, 16kHz)
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        # Add to buffer
        self.audio_buffers[client_id].extend(audio_float)
        
        # Process if buffer is large enough (e.g., 3 seconds of audio at 16kHz)
        buffer_duration = len(self.audio_buffers[client_id]) / 16000
        
        if buffer_duration >= 3.0:  # Process every 3 seconds
            logging.info(f"Processing {buffer_duration:.2f}s of audio...")
            
            # Convert buffer to numpy array
            audio_array = np.array(self.audio_buffers[client_id], dtype=np.float32)
            
            # Save to temporary file
            temp_path = f"/tmp/audio_{client_id}_{datetime.now().timestamp()}.wav"
            self._save_audio(audio_array, temp_path, sample_rate=16000)
            
            # Transcribe
            try:
                segments, info = self.model.transcribe(
                    temp_path,
                    beam_size=5,
                    vad_filter=True,
                    language=data.get('language', None)
                )
                
                # Collect transcript
                transcript = " ".join([seg.text.strip() for seg in segments])
                
                # Send result back
                await websocket.send(json.dumps({
                    'type': 'transcript',
                    'text': transcript,
                    'is_final': False,
                    'language': info.language,
                    'duration': info.duration
                }))
                
                logging.info(f"✓ Transcribed: {transcript[:50]}...")
                
            except Exception as e:
                logging.error(f"Transcription error: {e}")
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            # Clear buffer (keep last 1 second for context)
            keep_samples = 16000  # 1 second
            self.audio_buffers[client_id] = self.audio_buffers[client_id][-keep_samples:]
    
    async def handle_file_upload(self, websocket, data):
        """Handle uploaded audio file"""
        logging.info("Processing uploaded file...")
        
        # Decode base64 audio file
        audio_bytes = base64.b64decode(data['audio'])
        
        # Save to temporary file
        file_ext = data.get('format', 'wav')
        temp_path = f"/tmp/upload_{datetime.now().timestamp()}.{file_ext}"
        
        with open(temp_path, 'wb') as f:
            f.write(audio_bytes)
        
        try:
            # Transcribe full file
            start_time = datetime.now()
            
            segments, info = self.model.transcribe(
                temp_path,
                beam_size=5,
                vad_filter=True,
                language=data.get('language', None),
                word_timestamps=True
            )
            
            # Collect segments with timestamps
            results = []
            full_transcript = []
            
            for segment in segments:
                results.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })
                full_transcript.append(segment.text.strip())
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Send complete result
            await websocket.send(json.dumps({
                'type': 'file_transcript',
                'text': " ".join(full_transcript),
                'segments': results,
                'language': info.language,
                'duration': info.duration,
                'processing_time': processing_time,
                'real_time_factor': info.duration / processing_time if processing_time > 0 else 0
            }))
            
            logging.info(f"✓ File transcribed in {processing_time:.2f}s (RTF: {info.duration/processing_time:.1f}x)")
            
        except Exception as e:
            logging.error(f"File transcription error: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def handle_stop_stream(self, websocket):
        """Handle stop streaming request"""
        client_id = id(websocket)
        
        # Process any remaining audio in buffer
        if client_id in self.audio_buffers and len(self.audio_buffers[client_id]) > 0:
            logging.info("Processing final buffer...")
            
            audio_array = np.array(self.audio_buffers[client_id], dtype=np.float32)
            temp_path = f"/tmp/audio_final_{client_id}.wav"
            self._save_audio(audio_array, temp_path, sample_rate=16000)
            
            try:
                segments, info = self.model.transcribe(
                    temp_path,
                    beam_size=5,
                    vad_filter=True
                )
                
                transcript = " ".join([seg.text.strip() for seg in segments])
                
                await websocket.send(json.dumps({
                    'type': 'transcript',
                    'text': transcript,
                    'is_final': True,
                    'language': info.language
                }))
                
            except Exception as e:
                logging.error(f"Final transcription error: {e}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        # Clear buffer
        if client_id in self.audio_buffers:
            del self.audio_buffers[client_id]
    
    def _save_audio(self, audio_data, filepath, sample_rate=16000):
        """Save audio data to WAV file"""
        # Convert float32 to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
    
    async def handle_client(self, websocket, path=None):
        """Handle WebSocket client connection"""
        client_id = id(websocket)
        logging.info(f"Client connected: {client_id}")
        
        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'stream':
                    await self.handle_realtime_stream(websocket, data)
                elif msg_type == 'file':
                    await self.handle_file_upload(websocket, data)
                elif msg_type == 'stop':
                    await self.handle_stop_stream(websocket)
                else:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': f'Unknown message type: {msg_type}'
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            logging.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logging.error(f"Error handling client {client_id}: {e}")
        finally:
            if client_id in self.audio_buffers:
                del self.audio_buffers[client_id]
    
    async def start(self, host='0.0.0.0', port=8000):
        """Start WebSocket server"""
        logging.info("="*60)
        logging.info("Whisper WebSocket Server Starting...")
        logging.info(f"Host: {host}")
        logging.info(f"Port: {port}")
        logging.info(f"Model: Whisper large-v3 (FP16)")
        logging.info(f"Device: CUDA")
        logging.info("="*60)
        
        async with websockets.serve(self.handle_client, host, port, max_size=50 * 1024 * 1024):
            logging.info(f"✓ Server is running on ws://{host}:{port}")
            logging.info("✓ Ready to accept connections")
            await asyncio.Future()

if __name__ == "__main__":
    server = WhisperServer()
    asyncio.run(server.start())
