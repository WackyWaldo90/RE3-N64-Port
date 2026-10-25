#!/usr/bin/env python3
"""Losslessly split a complete SDK/toolchain tarball into <=24 MiB pieces."""
import argparse, hashlib, json, pathlib
CHUNK=24*1024*1024
p=argparse.ArgumentParser();p.add_argument('archive',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,default=pathlib.Path('n64-toolchain-parts'));a=p.parse_args()
if not a.archive.is_file(): p.error('archive not found')
a.output.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256();parts=[];total=0
with a.archive.open('rb') as src:
 for n in iter(int,1):
  data=src.read(CHUNK)
  if not data:break
  sha.update(data);total+=len(data)
  name=f'{a.archive.name}.part{n:03d}';(a.output/name).write_bytes(data)
  parts.append({'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
manifest={'archive_name':a.archive.name,'archive_bytes':total,'archive_sha256':sha.hexdigest(),'chunk_bytes':CHUNK,'parts':parts}
(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'{len(parts)} parts, {total} bytes, sha256={sha.hexdigest()}')
