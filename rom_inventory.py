#!/usr/bin/env python3
"""Non-extracting N64 ROM inventory: header, SHA-256, and per-MiB entropy."""
import hashlib
import json
import math
import pathlib
import sys
from collections import Counter

def entropy(data):
    counts = Counter(data)
    size = len(data)
    return -sum((count / size) * math.log2(count / size) for count in counts.values()) if size else 0.0

def main(path):
    p = pathlib.Path(path)
    with p.open('rb') as f:
        head = f.read(0x40)
        f.seek(0)
        sha = hashlib.sha256()
        blocks = []
        index = 0
        while chunk := f.read(1024 * 1024):
            sha.update(chunk)
            blocks.append({'block': index, 'offset': index * 1024 * 1024, 'size': len(chunk), 'entropy': round(entropy(chunk), 5)})
            index += 1
    if len(head) < 0x40:
        raise ValueError('File too small for N64 header')
    magic = head[:4].hex()
    if magic not in ('80371240', '37804012', '40123780'):
        raise ValueError(f'Unrecognized N64 ROM byte order: {magic}')
    print(json.dumps({'filename': p.name, 'bytes': p.stat().st_size, 'byte_order_magic': magic,
                      'sha256': sha.hexdigest(), 'header_title_raw': head[0x20:0x34].decode('ascii', 'replace').strip(),
                      'entrypoint_raw_hex': head[8:12].hex(), 'mib_blocks': blocks}, indent=2))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: rom_inventory.py /path/to/rom.z64')
    main(sys.argv[1])
