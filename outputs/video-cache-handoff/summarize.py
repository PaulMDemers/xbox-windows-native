"""Keep a compact reproducible inventory while preserving full private entries."""
import json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=read(k/'alias-scan.json');v=read(k/'verification.json');assert v['passed'] and v['alias_scan_sha256']==sha(k/'alias-scan.json')
keys=['cr3','root','present_pdes','large_pdes','pdes_examined','ptes_examined','directory_sha256','ranges','processes']
rows=[{key:d[key] for key in keys} for d in s['directories']]
for d in s['directories']:
 assert len(d['ranges'])==2 and len(d['matches'])==2048 and all(r['length']==4194304 for r in d['ranges'])
 assert all(r['page_bytes']==4096 and r['pcd'] and r['pwt'] and not r['pat'] and not r['user'] for r in d['matches'])
 assert not any(0x03c00000<=r['virtual']<0x04000000 or 0x83c00000<=r['virtual']<0x84000000 for r in d['matches'])
result=dict(passed=True,private_full_inventory_sha256=sha(k/'alias-scan.json'),verification_sha256=sha(k/'verification.json'),snapshot_sha256=s['snapshot_sha256'],process_count=len(s['processes']),directory_count=len(rows),total_pdes_examined=sum(d['pdes_examined'] for d in rows),total_ptes_examined=sum(d['ptes_examined'] for d in rows),total_matching_entries=sum(len(d['matches']) for d in s['directories']),directories=rows,limits=s['limits'])
p=k/'alias-summary.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print({key:result[key] for key in ['passed','process_count','directory_count','total_pdes_examined','total_ptes_examined','total_matching_entries']})
