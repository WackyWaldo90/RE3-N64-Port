#!/usr/bin/env python3
"""Deterministic structural audit. Flags are observations, not necessarily defects."""
import argparse,collections,csv
from pathlib import Path
def audit(rows):
 by_room=collections.defaultdict(list)
 for r in rows:by_room[r["room"]].append(r)
 issues=[]
 for room,rs in sorted(by_room.items()):
  counts=collections.Counter(tuple(r[k] for k in ("x1","z1","x2","z2","id","type","floor_mask","unknown")) for r in rs)
  for r in rs:
   x1,z1,x2,z2=(int(r[k]) for k in ("x1","z1","x2","z2"))
   flags=[]
   if x1==x2 or z1==z2:flags.append("zero_axis_span")
   if x2<x1:flags.append("x_descending")
   if z2<z1:flags.append("z_descending")
   key=tuple(r[k] for k in ("x1","z1","x2","z2","id","type","floor_mask","unknown"))
   if counts[key]>1:flags.append("duplicate_exact_record")
   if flags:issues.append(dict(room=room,record=r["record"],shape=r["shape"],flags="|".join(flags)))
 return issues
def main():
 p=argparse.ArgumentParser();p.add_argument("input",type=Path);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 with a.input.open(newline="") as f:rows=list(csv.DictReader(f))
 issues=audit(rows)
 with a.out.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["room","record","shape","flags"]);w.writeheader();w.writerows(issues)
 print(f"Audited {len(rows)} records; {len(issues)} flagged (not necessarily erroneous)")
if __name__=="__main__":main()
