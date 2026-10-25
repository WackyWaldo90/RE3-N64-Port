#!/usr/bin/env python3
"""Search PS1 RAM dumps for exact RE3 SCA bytes; a match is NOT a verified runtime address."""
import argparse,csv,json,hashlib
from pathlib import Path

def find_hits(blob, targets, base=0, min_signature_bytes=32):
    hits=[]
    for target in targets:
        sig=bytes.fromhex(target['pair_hex'] if min_signature_bytes==32 else target['record_hex'])
        if len(sig)<min_signature_bytes:continue
        pos=blob.find(sig)
        while pos!=-1:
            hits.append(dict(room=target['room'],record=int(target['index']),shape=int(target['shape']),dump_offset=pos,ps1_address_hex=hex(base+pos),signature_bytes=len(sig),rdt_sha256=target['rdt_sha256']))
            pos=blob.find(sig,pos+1)
    return hits

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('ram_dump',type=Path)
    p.add_argument('--targets',type=Path,default=Path(__file__).with_name('ram_search_targets.csv'))
    p.add_argument('--base',type=lambda s:int(s,0),default=0x80000000,help='Address represented by first dump byte; default 0x80000000 for a raw 2 MiB PS1 RAM dump')
    p.add_argument('--single',action='store_true',help='Allow weak 16-byte signatures (default requires two adjacent records / 32 bytes)')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    blob=args.ram_dump.read_bytes()
    with args.targets.open(newline='') as f:targets=list(csv.DictReader(f))
    hits=find_hits(blob,targets,args.base,16 if args.single else 32)
    result={'dump_bytes':len(blob),'dump_sha256':hashlib.sha256(blob).hexdigest(),'base':hex(args.base),'signature_length':16 if args.single else 32,'hits':hits,'caution':'Addresses are candidates only; verify room loaded and runtime read watchpoints. A dump offset may be mapped differently in emulator memory.'}
    out=json.dumps(result,indent=2)
    if args.output:args.output.write_text(out+'\n')
    else:print(out)
if __name__=='__main__':main()
