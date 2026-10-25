#!/usr/bin/env python3
"""Verify all parts and reconstruct the exact original archive."""
import argparse,hashlib,json,pathlib,sys
p=argparse.ArgumentParser();p.add_argument('directory',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path);a=p.parse_args()
m=json.loads((a.directory/'manifest.json').read_text());dest=a.output or (a.directory/m['archive_name'])
if dest.exists():sys.exit(f'Refusing to overwrite {dest}')
sha=hashlib.sha256();total=0
try:
 with dest.open('wb') as out:
  for item in m['parts']:
   name=item['name']
   if pathlib.PurePath(name).name!=name:raise ValueError('unsafe part name')
   part=a.directory/name;digest=hashlib.sha256();size=0
   with part.open('rb') as f:
    while True:
     chunk=f.read(1024*1024)
     if not chunk:break
     digest.update(chunk);sha.update(chunk);size+=len(chunk);total+=len(chunk);out.write(chunk)
   if size!=item['bytes'] or digest.hexdigest()!=item['sha256']:raise ValueError(f'Invalid part: {name}')
 if total!=m['archive_bytes'] or sha.hexdigest()!=m['archive_sha256']:raise ValueError('Reassembled checksum mismatch')
except Exception:
 dest.unlink(missing_ok=True);raise
print(f'Verified: {dest} ({total} bytes, SHA256 {sha.hexdigest()})')
