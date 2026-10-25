#!/usr/bin/env python3
"""Minimal PS1 MIPS R3000A disassembly of captured CPU read PCs.
Unknown instructions remain raw; this is not a complete MIPS disassembler.
"""
import argparse,json,struct
from pathlib import Path
REG=['zero','at','v0','v1','a0','a1','a2','a3','t0','t1','t2','t3','t4','t5','t6','t7','s0','s1','s2','s3','s4','s5','s6','s7','t8','t9','k0','k1','gp','sp','fp','ra']
LOAD={0x20:'lb',0x21:'lh',0x23:'lw',0x24:'lbu',0x25:'lhu',0x22:'lwl',0x26:'lwr'}
STORE={0x28:'sb',0x29:'sh',0x2b:'sw',0x2a:'swl',0x2e:'swr'}
def signed(v):return v-65536 if v&0x8000 else v
def decode(word,pc):
 op=word>>26;rs=(word>>21)&31;rt=(word>>16)&31;rd=(word>>11)&31;fun=word&63;imm=word&65535
 if op in LOAD:return f"{LOAD[op]} ${REG[rt]},{signed(imm)}(${REG[rs]})"
 if op in STORE:return f"{STORE[op]} ${REG[rt]},{signed(imm)}(${REG[rs]})"
 if op==0:
  if word==0:return 'nop'
  if fun==8:return f"jr ${REG[rs]}"
  if fun==9:return f"jalr ${REG[rd]},${REG[rs]}"
  if fun==0:return f"sll ${REG[rd]},${REG[rt]},{(word>>6)&31}"
  if fun==2:return f"srl ${REG[rd]},${REG[rt]},{(word>>6)&31}"
  if fun==3:return f"sra ${REG[rd]},${REG[rt]},{(word>>6)&31}"
  for k,v in {0x20:'add',0x21:'addu',0x22:'sub',0x23:'subu',0x24:'and',0x25:'or',0x26:'xor',0x2a:'slt',0x2b:'sltu'}.items():
   if fun==k:return f"{v} ${REG[rd]},${REG[rs]},${REG[rt]}"
 if op in (2,3):
  target=((pc+4)&0xf0000000)|((word&0x3ffffff)<<2)
  return f"{'j' if op==2 else 'jal'} 0x{target:08x}"
 if op in (4,5):
  dest=(pc+4+(signed(imm)<<2))&0xffffffff
  return f"{'beq' if op==4 else 'bne'} ${REG[rs]},${REG[rt]},0x{dest:08x}"
 if op in (8,9,10,11,12,13,14,15):
  names={8:'addi',9:'addiu',10:'slti',11:'sltiu',12:'andi',13:'ori',14:'xori',15:'lui'}
  if op==15:return f"lui ${REG[rt]},0x{imm:x}"
  return f"{names[op]} ${REG[rt]},${REG[rs]},{imm if op in (12,13,14) else signed(imm)}"
 return f".word 0x{word:08x}  # undecoded"
def disassemble(data,pcs,base):
 out=[]
 for pc in sorted(set(pcs)):
  offset=pc-base
  if offset<0 or offset+4>len(data) or offset%4:
   out.append(dict(pc=f"0x{pc:08x}",error="outside dump or unaligned"))
   continue
  word=struct.unpack_from('<I',data,offset)[0]
  out.append(dict(pc=f"0x{pc:08x}",raw=f"0x{word:08x}",instruction=decode(word,pc)))
 return out
def main():
 p=argparse.ArgumentParser()
 p.add_argument("memory",type=Path,help="Raw executable memory capture or PS-X EXE payload")
 p.add_argument("cpu_evidence",type=Path,help="M110 CPU evidence JSON")
 p.add_argument("--base",type=lambda x:int(x,0),required=True,help="Actual address mapped to file offset zero")
 p.add_argument("--out",type=Path)
 a=p.parse_args()
 evidence=json.loads(a.cpu_evidence.read_text())
 pcs=[int(x["pc"],0) for x in evidence["pc_summary"]]
 result={"base":hex(a.base),"instructions":disassemble(a.memory.read_bytes(),pcs,a.base),
         "warning":"Address mapping must be verified. Decoded instructions alone do not identify RE3 collision semantics."}
 payload=json.dumps(result,indent=2)+"\\n"
 if a.out:a.out.write_text(payload)
 else:print(payload)
if __name__=="__main__":main()
