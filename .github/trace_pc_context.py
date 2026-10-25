#!/usr/bin/env python3
"""Decode instruction windows around observed PS1 MIPS PCs, annotate delay slots."""
import argparse,json,struct
from pathlib import Path
from disassemble_trace_pcs import decode
def context(blob,pcs,base,before=6,after=6):
    out=[]
    for pc in sorted(set(pcs)):
        lines=[]
        for address in range(pc-before*4,pc+(after+1)*4,4):
            off=address-base
            if off<0 or off+4>len(blob) or off%4:continue
            word=struct.unpack_from("<I",blob,off)[0]
            ins=decode(word,address)
            previous=struct.unpack_from("<I",blob,off-4)[0] if off>=4 else 0
            prev_op=previous>>26
            prev_fun=previous&63
            delay=(prev_op in (2,3,4,5,6,7,1)) or (prev_op==0 and prev_fun in (8,9))
            lines.append(dict(pc=hex(address),raw=hex(word),instruction=ins,
                              observed_pc=address==pc,branch_delay_slot=delay))
        out.append(dict(observed_pc=hex(pc),instructions=lines))
    return out
def main():
 p=argparse.ArgumentParser()
 p.add_argument("memory",type=Path)
 p.add_argument("cpu_evidence",type=Path)
 p.add_argument("--base",type=lambda x:int(x,0),required=True)
 p.add_argument("--before",type=int,default=6)
 p.add_argument("--after",type=int,default=6)
 p.add_argument("--out",type=Path)
 a=p.parse_args()
 if not (0<=a.before<=100 and 0<=a.after<=100):p.error("window must be 0..100")
 pcs=[int(row["pc"],0) for row in json.loads(a.cpu_evidence.read_text())["pc_summary"]]
 result=dict(windows=context(a.memory.read_bytes(),pcs,a.base,a.before,a.after),
             warning="Branch delay annotation is partial; not a CFG reconstruction or proof of RE3 engine semantics.")
 payload=json.dumps(result,indent=2)+"\\n"
 if a.out:a.out.write_text(payload)
 else:print(payload)
if __name__=="__main__":main()
