#!/usr/bin/env python3
"""Read ISO9660 from PS1 2352-byte BIN (Mode1/Mode2 Form1) or 2048 ISO.

Extract SYSTEM.CNF boot target without guessing game executable names.
"""
import argparse, hashlib, json, re, struct
from pathlib import Path

class Disc:
    def __init__(self, path):
        self.file = open(path, 'rb')
        self.length = Path(path).stat().st_size
        try:
            self.sector_size, self.payload_offset = self.detect()
        except Exception:
            self.file.close()
            raise
    def close(self): self.file.close()
    def detect(self):
        for stride,offset in ((2352,24),(2352,16),(2048,0)):
            self.file.seek(16*stride+offset)
            p=self.file.read(7)
            if p[1:6]==b'CD001' and p[0] in (1,2): return stride,offset
        raise ValueError('No ISO9660 PVD at LBA 16; check BIN track layout/CUE')
    def sector(self,lba):
        if lba<0 or lba*self.sector_size+self.payload_offset+2048>self.length:
            raise ValueError('Sector outside image')
        self.file.seek(lba*self.sector_size+self.payload_offset)
        data=self.file.read(2048)
        if len(data)!=2048: raise ValueError('Truncated sector')
        return data
    def extent(self,lba,size):
        if size<0 or size>100*1024*1024: raise ValueError('Invalid/oversized file extent')
        return b''.join(self.sector(lba+i) for i in range((size+2047)//2048))[:size]
    def entries(self,lba,size):
        raw=self.extent(lba,size)
        pos=0
        while pos<len(raw):
            length=raw[pos]
            if not length:
                pos=(pos//2048+1)*2048;continue
            if length<34 or pos+length>len(raw):raise ValueError('Invalid directory record')
            rec=raw[pos:pos+length]
            n=rec[32]
            if 33+n>len(rec):raise ValueError('Invalid filename length')
            name=rec[33:33+n].decode('ascii',errors='replace')
            if name not in ('\x00','\x01'):
                yield dict(name=name,lba=struct.unpack_from('<I',rec,2)[0],size=struct.unpack_from('<I',rec,10)[0],directory=bool(rec[25]&2))
            pos+=length
    def list_root(self):
        pvd=self.sector(16)
        if pvd[:7]!=b'\x01CD001\x01':raise ValueError('Invalid primary volume descriptor')
        root=pvd[156:190]
        return list(self.entries(struct.unpack_from('<I',root,2)[0],struct.unpack_from('<I',root,10)[0]))

def boot_target(cnf):
    text=cnf.decode('ascii',errors='replace')
    match=re.search(r'^\s*BOOT\s*=\s*cdrom\s*:\s*\\?\s*([^\r\n]+)',text,re.I|re.M)
    if not match:raise ValueError('SYSTEM.CNF lacks a recognizable BOOT=cdrom: entry')
    target=match.group(1).strip().strip('"').replace('\\','/').lstrip('/')
    if not target or '..' in target.split('/'):raise ValueError('Unsafe boot path')
    return target

def run(path,out):
    d=Disc(path)
    try:
        root=d.list_root()
        cnf=next((e for e in root if e['name'].upper().split(';')[0]=='SYSTEM.CNF' and not e['directory']),None)
        if not cnf:raise ValueError('SYSTEM.CNF not found in root')
        target=boot_target(d.extent(cnf['lba'],cnf['size']))
        parts=target.upper().split('/')
        entries=root
        chosen=None
        for idx,part in enumerate(parts):
            chosen=next((e for e in entries if e['name'].upper().split(';')[0]==part.split(';')[0]),None)
            if not chosen:raise ValueError('BOOT target not found in ISO9660 filesystem: '+target)
            if idx<len(parts)-1:
                if not chosen['directory']:raise ValueError('BOOT parent not a directory')
                entries=list(d.entries(chosen['lba'],chosen['size']))
        if chosen['directory']:raise ValueError('BOOT target is a directory')
        data=d.extent(chosen['lba'],chosen['size'])
        out.mkdir(parents=True,exist_ok=True)
        (out/'boot_executable.bin').write_bytes(data)
        manifest=dict(source_size=d.length,sector_size=d.sector_size,payload_offset=d.payload_offset,
            root_entries=root,boot_path=target,boot_lba=chosen['lba'],boot_size=len(data),
            boot_sha256=hashlib.sha256(data).hexdigest(),psx_exe_magic=data[:8]==b'PS-X EXE')
        (out/'disc_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        return manifest
    finally:d.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('disc',type=Path);p.add_argument('--out',type=Path,default=Path('extracted_boot'))
    a=p.parse_args();print(json.dumps(run(a.disc,a.out),indent=2))
