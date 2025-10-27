#!/usr/bin/env python3
"""
Wrapper script to run verification tests with guaranteed output.
Created: 2025-10-28
"""

import sys
import os
import subprocess
from pathlib import Path

# Ensure unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

print("=" * 80, flush=True)
print("VERIFICATION TEST WRAPPER", flush=True)
print("=" * 80, flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Working directory: {os.getcwd()}", flush=True)
print(f"Script location: {__file__}", flush=True)
print("=" * 80, flush=True)

# Run the actual test
test_script = Path(__file__).parent / "test_integration_real_upload.py"
print(f"\nRunning test script: {test_script}", flush=True)
print("=" * 80, flush=True)

try:
    result = subprocess.run(
        [sys.executable, str(test_script)],
        capture_output=True,
        text=True,
        timeout=180
    )

    # Save output to file
    output_file = Path(__file__).parent / "test_files" / "verification_test_output.txt"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("VERIFICATION TEST OUTPUT\n")
        f.write("=" * 80 + "\n\n")
        f.write("STDOUT:\n")
        f.write("=" * 80 + "\n")
        f.write(result.stdout)
        f.write("\n\n")

        if result.stderr:
            f.write("STDERR:\n")
            f.write("=" * 80 + "\n")
            f.write(result.stderr)
            f.write("\n\n")

        f.write("=" * 80 + "\n")
        f.write(f"Exit code: {result.returncode}\n")
        f.write("=" * 80 + "\n")

    print(f"\n[OK] Output saved to: {output_file}", flush=True)

    print("\n" + "=" * 80, flush=True)
    print("STDOUT:", flush=True)
    print("=" * 80, flush=True)
    print(result.stdout, flush=True)

    if result.stderr:
        print("\n" + "=" * 80, flush=True)
        print("STDERR:", flush=True)
        print("=" * 80, flush=True)
        print(result.stderr, flush=True)

    print("\n" + "=" * 80, flush=True)
    print(f"Exit code: {result.returncode}", flush=True)
    print("=" * 80, flush=True)

    sys.exit(result.returncode)
    
except subprocess.TimeoutExpired:
    print("\n❌ Test timed out after 180 seconds", flush=True)
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error running test: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

