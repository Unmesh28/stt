from faster_whisper import WhisperModel
import time

print("Loading Whisper large-v3 model...")
start = time.time()

model = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",
    download_root="/home/ubuntu/.cache/whisper"
)

print(f"✓ Model loaded in {time.time() - start:.2f}s")
print(f"✓ Model is ready for inference!")
print(f"\nModel info:")
print(f"  - Device: cuda")
print(f"  - Compute type: float16")
print(f"  - Status: Ready ✓")
