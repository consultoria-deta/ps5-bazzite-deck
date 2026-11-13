#!/usr/bin/python3 -I
# Start buffer for the AC-3 pipe: hold N bytes before letting anything through, then pass everything as is.
import sys, os
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6144*4
fi, fo = sys.stdin.buffer.fileno(), sys.stdout.buffer.fileno()
buf = b""
while len(buf) < N:
    d = os.read(fi, 65536)
    if not d: break
    buf += d
os.write(fo, buf)
while True:
    d = os.read(fi, 65536)
    if not d: break
    os.write(fo, d)
