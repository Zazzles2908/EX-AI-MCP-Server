#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

SUITES = [
    "tests/phase4", "tests/phase5", "tests/phase6", "tests/phase7", "tests/phase8",
]

def run(cmd):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def main():
    root = Path(__file__).resolve().parents[2]
    results = []
    for suite in SUITES:
        cmd = [sys.executable, "-m", "pytest", "-q", str(root / suite), "-q"]
        res = run(cmd)
        print(res.stdout)
        results.append((suite, res.returncode))
    failed = [s for s, code in results if code != 0]
    if failed:
        print("FAILED suites:", failed)
        sys.exit(2)
    print("All health suites passed.")

if __name__ == "__main__":
    main()

