#!/usr/bin/env python3
"""Lossless N64 big-endian container for extracted RE3 SCA records.
No claim of native N64 engine compatibility.
"""
import argparse,csv,struct,zlib,json
from pathlib import Path
MAGIC=b"R3SC"
HEADER=struct.Struct(">4sHHII")
RECORD=struct.Struct(">hhhhHHHH")
def pack(rows):
 if len(rows)>65535:raise ValueError("too many records")
 payload=bytearray()
 for r in rows:
  v=[int(r[k]) for k in ("x1","z1","x2","z2","id","type","floor_mask","unknown")]
  payload+=RECORD.pack(*v)
 crc=zlib.crc32(payload)&0xffffffff
 return HEADER.pack(MAGIC,1,len(rows),len(payload),crc)+payload
def unpack(data):
 if len(data)<HEADER.size:raise ValueError("truncated header")
 magic,version,count,size,crc=HEADER.unpack_from(data)
 if magic!=MAGIC or version!=1:raise ValueError("invalid header")
 if size!=count*RECORD.size or len(data)!=HEADER.size+size:raise ValueError("size mismatch")
 payload=data[HEADER.size:]
 if zlib.crc32(payload)&0xffffffff!=crc:raise ValueError("CRC mismatch")
 return [RECORD.unpack_from(payload,i*RECORD.size) for i in range(count)]
def main():
 p=argparse.ArgumentParser();p.add_argument("csv",type=Path);p.add_argument("output",type=Path)
 a=p.parse_args()
 with a.csv.open(newline="") as f:rows=list(csv.DictReader(f))
 byroom={}
 for r in rows:byroom.setdefault(r["room"],[]).append(r)
 a.output.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for room,records in sorted(byroom.items()):
  name=Path(room).stem+".r3sc"
  b=pack(records)
  assert len(unpack(b))==len(records)
  (a.output/name).write_bytes(b)
  manifest.append(dict(room=room,file=name,records=len(records),bytes=len(b)))
 (a.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\\n")
 print("Packed",len(manifest),"nonempty rooms;",sum(x["records"] for x in manifest),"records")
if __name__=="__main__":main()
