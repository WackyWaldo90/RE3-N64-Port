#!/usr/bin/env python3
"""Correlate captured CPU read events with candidate collision table ranges."""
import argparse,csv,json,collections
from pathlib import Path
def parse_int(v):
    if isinstance(v,int):return v
    return int(v,0)
def correlate(events,candidates,reference,base=0x80000000):
    ranges=[]
    for item in candidates:
        room=item["room"]
        if room not in reference:continue
        start=base+int(item["candidate_sca_header_offset"])
        length=len(bytes.fromhex(reference[room]["table_hex"]))
        ranges.append((room,start,start+length))
    counts=collections.Counter()
    evidence=[]
    for event in events:
        if str(event.get("kind","read")).lower() not in ("read","load","r"):continue
        addr=parse_int(event["address"])
        size=parse_int(event.get("size",1))
        if size<1 or size>16:raise ValueError("invalid read size")
        pc=parse_int(event["pc"])
        for room,lo,hi in ranges:
            if addr<hi and addr+size>lo:
                counts[(room,pc)]+=1
                evidence.append(dict(room=room,pc=hex(pc),address=hex(addr),size=size,table_start=hex(lo)))
    summary=[dict(room=r,pc=hex(pc),reads=n) for (r,pc),n in counts.most_common()]
    return dict(total_read_events=len(events),matched_reads=len(evidence),pc_summary=summary,
                matched_events=evidence,warning="Only captured read events; not proof of stair-specific code. Confirm PC against RE3 Europe executable and reproduce with movement.")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("reads",type=Path,help="JSON array of {pc,address,size,kind} read events")
    p.add_argument("validation",type=Path,help="M107 validation JSON containing candidate_groups")
    p.add_argument("--base",type=lambda x:int(x,0),default=0x80000000)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    root=Path(__file__).resolve().parent
    reference=json.loads((root/"room_sca_reference.json").read_text())
    events=json.loads(a.reads.read_text())
    candidates=json.loads(a.validation.read_text())["candidate_groups"]
    result=correlate(events,candidates,reference,a.base)
    payload=json.dumps(result,indent=2)+"\\n"
    if a.out:a.out.write_text(payload)
    else:print(payload)
if __name__=="__main__":main()
