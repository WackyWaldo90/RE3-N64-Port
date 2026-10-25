#!/usr/bin/env python3
"""Build 16-byte aligned ROM-style asset bank and BE index from validated R3SC rooms."""
import argparse,struct,json,zlib
from pathlib import Path
INDEX=struct.Struct(">4sHHII")
ENTRY=struct.Struct(">16sIII")
def build(source,output):
    files=sorted(source.glob("*.r3sc"));bank=bytearray();entries=[]
    for file in files:
        name=file.stem.encode("ascii")
        if len(name)>15:raise ValueError("room name exceeds 15 ASCII bytes")
        data=file.read_bytes()
        if len(data)<16 or data[:4]!=b"R3SC":raise ValueError("invalid room "+file.name)
        count=struct.unpack_from(">H",data,6)[0]
        size=struct.unpack_from(">I",data,8)[0]
        crc=struct.unpack_from(">I",data,12)[0]
        if size!=count*16 or len(data)!=16+size or zlib.crc32(data[16:])&0xffffffff!=crc:raise ValueError("invalid CRC/size "+file.name)
        bank.extend(b"\0"*((-len(bank))%16))
        entries.append((name.ljust(16,b"\0"),len(bank),len(data),zlib.crc32(data)&0xffffffff))
        bank.extend(data)
    if len(entries)>65535:raise ValueError("too many rooms")
    idx=INDEX.pack(b"R3BK",1,len(entries),len(bank),zlib.crc32(bank)&0xffffffff)+b"".join(ENTRY.pack(*e) for e in entries)
    output.mkdir(parents=True,exist_ok=True)
    (output/"collision_bank.bin").write_bytes(bank)
    (output/"collision_index.bin").write_bytes(idx)
    (output/"manifest.json").write_text(json.dumps([dict(room=e[0].rstrip(b"\0").decode(),offset=e[1],size=e[2],crc32=e[3]) for e in entries],indent=2))
    return len(entries),len(bank)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("source",type=Path);p.add_argument("output",type=Path);a=p.parse_args();print(build(a.source,a.output))
