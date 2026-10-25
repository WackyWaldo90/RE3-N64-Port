#!/usr/bin/env python3
"""Safe, read-only inventory and deterministic sub-25MB chunk packaging."""
import argparse,hashlib,json,os,pathlib,re,zipfile
MAX=24_000_000
EXTS={'.md','.txt','.json','.csv','.yaml','.yml','.py','.js','.ts','.c','.h','.cpp','.hpp','.xml','.ini','.toml'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def inventory(root,out):
 root=root.resolve(); out.mkdir(parents=True,exist_ok=True); rows=[]
 for p in sorted(root.rglob('*')):
  if not p.is_file() or p.is_symlink() or out in p.parents:continue
  rows.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'codex_text_candidate':p.suffix.lower() in EXTS})
 (out/'inventory.json').write_text(json.dumps(rows,indent=2)+'\n')
 print('Inventoried',len(rows),'files')
def chunks(path,out):
 out.mkdir(parents=True,exist_ok=True); manifest={'source_name':path.name,'source_bytes':path.stat().st_size,'source_sha256':sha(path),'chunk_size':MAX,'parts':[]}
 with path.open('rb') as src:
  i=0
  while (data:=src.read(MAX)):
   name=f'{path.name}.part{i:04d}'; p=out/name;p.write_bytes(data)
   manifest['parts'].append({'file':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});i+=1
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Created',i,'parts')
def restore(folder,dest):
 m=json.loads((folder/'manifest.json').read_text());h=hashlib.sha256();n=0
 with dest.open('wb') as f:
  for entry in m['parts']:
   p=folder/entry['file'];b=p.read_bytes()
   if len(b)!=entry['bytes'] or hashlib.sha256(b).hexdigest()!=entry['sha256']:raise ValueError('Corrupt chunk '+str(p))
   f.write(b);h.update(b);n+=len(b)
 if n!=m['source_bytes'] or h.hexdigest()!=m['source_sha256']:
  dest.unlink(missing_ok=True);raise ValueError('Reassembled file checksum mismatch')
 print('Verified',dest)
def main():
 a=argparse.ArgumentParser();s=a.add_subparsers(dest='cmd',required=True)
 for name in ('inventory','split','restore'):
  p=s.add_parser(name);p.add_argument('source',type=pathlib.Path);p.add_argument('output',type=pathlib.Path)
 args=a.parse_args();{'inventory':inventory,'split':chunks,'restore':restore}[args.cmd](args.source,args.output)
if __name__=='__main__':main()
