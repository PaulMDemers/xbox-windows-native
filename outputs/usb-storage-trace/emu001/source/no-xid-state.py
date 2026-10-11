"""Verify no XID service/image references in both captured SYSTEM hives."""
import hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages');import hivex
k=Path(__file__).resolve().parent;case=sys.argv[1];assert re.fullmatch('emu[0-9]{3}',case)
run=k.parents[1]/('work/runs/nt5stortrace-'+case);assert (run/'cleanup.json').exists()
result=dict(physical_access=False,phases={})
for phase in ['before','after']:
    p=run/(phase+'-system');h=hivex.Hivex(str(p));todo=[('',h.root())];seen=set();hits=[]
    while todo:
        path,node=todo.pop();assert node not in seen;seen.add(node)
        if path.lower().endswith('/services/xwnxid'):hits.append(dict(path=path,kind='service'))
        for v in h.node_values(node):
            kind,data=h.value_value(v)
            if kind in [1,2,7] and 'xwnxid' in data.decode('utf-16le',errors='replace').lower():
                hits.append(dict(path=path,key=h.value_key(v),kind='string-reference'))
        todo.extend((path+'/'+h.node_name(c),c) for c in h.node_children(node))
    result['phases'][phase]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),keys=len(seen),xid_references=hits,absent=not hits)
result['xid_registry_absent']=all(v['absent'] for v in result['phases'].values())
(k/case/'no-xid-state.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
