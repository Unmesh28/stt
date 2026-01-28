#!/usr/bin/env python3
"""Python client for testing Whisper WebSocket server"""

import asyncio
import websockets
import json
import base64
import sys
import wave

class WhisperClient:
    def __init__(self, server_url="ws://localhost:8000"):
        self.server_url = server_url
        self.ws = None
    
    async def connect(self):
        print(f"Connecting to {self.server_url}...")
        self.ws = await websockets.connect(self.server_url)
        print("✓ Connected successfully")
    
    async def transcribe_file(self, audio_file):
        print(f"\nTranscribing file: {audio_file}")
        
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        file_ext = audio_file.split('.')[-1]
        
        message = {
            'type': 'file',
            'audio': audio_base64,
            'format': file_ext,
            'language': None
        }
        
        print("Sending file to server...")
        await self.ws.send(json.dumps(message))
        
        print("Waiting for transcription...")
        response = await self.ws.recv()
        data = json.loads(response)
        
        if data['type'] == 'file_transcript':
            self.print_file_result(data)
        elif data['type'] == 'error':
            print(f"❌ Error: {data['message']}")
    
    def print_file_result(self, data):
        print("\n" + "="*70)
        print("TRANSCRIPTION RESULT")
        print("="*70)
        print(f"Language: {data['language'].upper()}")
        print(f"Duration: {data['duration']:.2f}s")
        print(f"Processing Time: {data['processing_time']:.2f}s")
        print(f"Real-time Factor: {data['real_time_factor']:.1f}x")
        print("="*70)
        
        if 'segments' in data and data['segments']:
            print("\nTRANSCRIPT WITH TIMESTAMPS:")
            print("-"*70)
            for segment in data['segments']:
                start = self.format_time(segment['start'])
                end = self.format_time(segment['end'])
                print(f"[{start} → {end}] {segment['text']}")
        else:
            print("\nFULL TRANSCRIPT:")
            print("-"*70)
            print(data['text'])
        
        print("="*70)
    
    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    async def stream_audio_chunks(self, audio_file, chunk_duration=3):
        print(f"\nStreaming file: {audio_file}")
        
        with wave.open(audio_file, 'rb') as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            
            print(f"Sample rate: {sample_rate}Hz")
            print(f"Channels: {n_channels}")
            
            chunk_size = int(sample_rate * chunk_duration)
            chunk_num = 0
            
            while True:
                frames = wf.readframes(chunk_size)
                if not frames:
                    break
                
                chunk_num += 1
                print(f"Sending chunk {chunk_num}...")
                
                audio_base64 = base64.b64encode(frames).decode('utf-8')
                
                message = {
                    'type': 'stream',
                    'audio': audio_base64,
                    'language': None
                }
                await self.ws.send(json.dumps(message))
                
                await asyncio.sleep(chunk_duration)
                
                try:
                    response = await asyncio.wait_for(self.ws.recv(), timeout=0.1)
                    data = json.loads(response)
                    if data['type'] == 'transcript':
                        print(f"✓ Transcript: {data['text'][:80]}...")
                except asyncio.TimeoutError:
                    pass
            
            print("\nSending stop signal...")
            await self.ws.send(json.dumps({'type': 'stop'}))
            
            response = await self.ws.recv()
            data = json.loads(response)
            if data['type'] == 'transcript' and data.get('is_final'):
                print(f"\n✓ Final transcript: {data['text']}")
    
    async def close(self):
        if self.ws:
            await self.ws.close()
            print("\n✓ Connection closed")

async def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  File mode:   python test_client.py file <audio_file> [server_url]")
        print("  Stream mode: python test_client.py stream <audio_file> [server_url]")
        print("\nExample:")
        print("  python test_client.py file test.mp3")
        print("  python test_client.py stream test.wav ws://192.168.1.100:8000")
        return
    
    mode = sys.argv[1]
    audio_file = sys.argv[2]
    server_url = sys.argv[3] if len(sys.argv) > 3 else "ws://localhost:8000"
    
    client = WhisperClient(server_url)
    
    try:
        await client.connect()
        
        if mode == 'file':
            await client.transcribe_file(audio_file)
        elif mode == 'stream':
            await client.stream_audio_chunks(audio_file)
        else:
            print(f"Unknown mode: {mode}")
        
        await client.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
