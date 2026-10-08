"""Read ONLY Run/RunOnce branches in already preserved hives; no guest/NBD."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
k=Path(__file__).resolve().parent;dest=k/'startup-inventory.json';assert not dest.exists()
roots=[r'Microsoft\Windows\CurrentVersion\Run',r'Microsoft\Windows\CurrentVersion\RunOnce',r'Microsoft\Windows\CurrentVersion\RunOnceEx']
results=[]
for label,filename in [('emulator-before','candidate001/artifacts/before-software'),('emulator-after','candidate001/artifacts/after-software'),
                       ('physical-before','candidate001/artifacts/physical/before-software'),('physical-after','candidate001/artifacts/physical/after-software')]:
    p=k/filename;h=hivex.Hivex(str(p));branches=[]
    for key in roots:
        n=h.root()
        for part in key.split('\\'):
            n=h.node_get_child(n,part)
            if not n:break
        values=[]
        if n:
            todo=[(key,n)];seen=set()
            while todo:
                path,node=todo.pop();assert node not in seen;seen.add(node)
                for value in h.node_values(node):
                    typ,data=h.value_value(value)
                    values.append(dict(path=path,name=h.value_key(value),type=typ,hex=data.hex(),
                        text=data.decode('utf-16le',errors='backslashreplace').rstrip('\0') if typ in [1,2,7] else None))
                todo.extend((path+'\\'+h.node_name(child),child) for child in h.node_children(node))
        branches.append(dict(key=key,present=bool(n),values=values))
    results.append(dict(label=label,hive_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),branches=branches))
r=dict(read_only_preserved_hives=True,physical_access=False,guest_or_nbd_access=False,results=results,
    causal_lifecycle_proven=False,limits='Static Run/RunOnce branches are leads only; no running parent/command/frame captured.')
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({v['label']:{b['key']:[row['text'] for row in b['values']] for b in v['branches']} for v in results},indent=2))
