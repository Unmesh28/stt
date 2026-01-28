#!/usr/bin/env python3
import time
import subprocess
import sys

if len(sys.argv) < 2:
    print("Usage: python performance_test.py <audio_file> [num_tests]")
    sys.exit(1)

audio_file = sys.argv[1]
num_tests = int(sys.argv[2]) if len(sys.argv) > 2 else 10

print(f"Running {num_tests} performance tests with {audio_file}...")
print("="*60)

times = []
for i in range(num_tests):
    start = time.time()
    result = subprocess.run(
        ['python', 'test_client.py', 'file', audio_file],
        capture_output=True,
        text=True
    )
    elapsed = time.time() - start
    times.append(elapsed)
    
    status = "✓" if result.returncode == 0 else "✗"
    print(f"Test {i+1:2d}: {elapsed:6.2f}s {status}")

print("="*60)
print(f"Average: {sum(times)/len(times):.2f}s")
print(f"Min:     {min(times):.2f}s")
print(f"Max:     {max(times):.2f}s")
print(f"Median:  {sorted(times)[len(times)//2]:.2f}s")
