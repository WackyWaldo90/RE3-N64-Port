#!/usr/bin/env python3
"""Verify extracted RDT SCA records against exported CSV without storing game binaries."""
import argparse,csv,io,struct,zipfile
from pathlib import Path
def validate(archive,csv_path):
 with zipfile.ZipFile(archive) as outer:
  with zipfile.ZipFile(io.BytesIO(outer.read("embedded_room_data.zip"))) as inner:
   by_room={}
   with open(csv_path,newline="") as f:
    for r in csv.DictReader(f):by_room.setdefault(r["room"],[]).append(r)
   checked=0
   for name,rs in by_room.items():
    data=inner.read(name);off=struct.unpack_from("<I",data,32)[0]
    count=struct.unpack_from("<I",data,off)[0]-1
    if len(rs)!=count:raise ValueError(f"{name}: count mismatch")
    for i,r in enumerate(rs):
     v=struct.unpack_from("<hhhhHHHH",data,off+16*(i+1))
     expect=(int(r["x1"]),int(r["z1"]),int(r["x2"]),int(r["z2"]),int(r["id"]),int(r["type"]),int(r["floor_mask"]),int(r["unknown"]))
     if v!=expect:raise ValueError(f"{name} record {i}: mismatch")
     checked+=1
   return len(by_room),checked
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("m93_zip",type=Path);p.add_argument("--csv",type=Path,default=Path("collision_records.csv"))
 a=p.parse_args();print("Validated rooms, records:",validate(a.m93_zip,a.csv))
