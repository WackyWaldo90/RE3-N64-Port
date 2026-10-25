#!/usr/bin/env python3
"""Parse PS-X EXE header and emit mapped executable payload (not a disc ripper)."""
import argparse,hashlib,json,struct
from pathlib import Path
def inspect(data):
    if len(data)<2048:raise ValueError("PS-X EXE header must be at least 2048 bytes")
    if data[:8]!=b"PS-X EXE":raise ValueError("missing PS-X EXE magic")
    fields={"initial_pc":0x10,"initial_gp":0x14,"load_address":0x18,
            "text_size":0x1c,"data_address":0x20,"data_size":0x24,
            "bss_address":0x28,"bss_size":0x2c,"stack_address":0x30,
            "stack_offset":0x34}
    info={k:struct.unpack_from("<I",data,off)[0] for k,off in fields.items()}
    size=info["text_size"]
    if size==0 or size>len(data)-2048:raise ValueError("invalid text size or truncated executable")
    info.update(format="PS-X EXE",payload_offset=2048,
                payload_sha256=hashlib.sha256(data[2048:2048+size]).hexdigest(),
                file_sha256=hashlib.sha256(data).hexdigest(),
                payload_bytes=size,
                note="load_address is file-payload mapping base, not a proven runtime collision PC")
    return info
def main():
    p=argparse.ArgumentParser()
    p.add_argument("exe",type=Path)
    p.add_argument("--payload",type=Path,help="Optional mapped payload output")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    data=a.exe.read_bytes()
    info=inspect(data)
    if a.payload:a.payload.write_bytes(data[2048:2048+info["text_size"]])
    payload=json.dumps(info,indent=2)+"\\n"
    if a.out:a.out.write_text(payload)
    else:print(payload)
if __name__=="__main__":main()
