"""Read-only cold capacity audit; one record per closed attempt."""
import json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'video-text-oracle206'))
from common import ColdIO,readers,m,sha
case=sys.argv[1];assert case in ('capacity-emu003',)
out=K/case;dest=out/'cold-audit003.json';assert not dest.exists()
run=Path('/mnt/e/xwn333/runs/nt5-'+case.replace('capacity-','capacity333-'))
assert (run/'cleanup.json').exists()
f=json.loads((K/'capacity-emu003/fixture.json').read_text());base=Path(f['fixture_path_linux'])
assert sha(base)==f['fixture_sha256']
disk=run/'hdd.qcow2';q=subprocess.run(['qemu-img','check','--output=json',str(disk)],capture_output=True,text=True)
r=dict(physical_access=False,closed=True,qcow_check=json.loads(q.stdout),qcow_exit=q.returncode,
       host_exit=json.loads((run/'host-exit.json').read_text()),base_sha256=f['fixture_sha256'])
with ColdIO(disk) as io:
    rr=readers(io,disk);r['xbe_exact']=m.sha(rr['E'].read('Applications/XWNCapacity333/default.xbe'))==f['file']['sha256']
    try:b=rr['E'].read('Applications/XWNCapacity333/capacity.txt')
    except KeyError:b=None
    r['report_present']=b is not None
    if b is not None:
        (out/'capacity.txt').write_bytes(b);r['report']=b.decode('ascii');r['report_sha256']=m.sha(b)
        rows=b.decode('ascii').splitlines();assert rows[0]=='XWN-CAPACITY-333' and rows[-1]=='COMPLETE 333'
        r['queries']=[]
        for row,v in zip(rows[1:-1],['E','F']):
            fields=row.split();assert fields[0]=='SPACE' and len(fields)==7
            ident,start,length,unit,total,free=map(int,fields[1:]);expected=f['before_geometry'][v]
            r['queries'].append(dict(volume=v,partition=ident,start=start,length=length,unit=unit,total=total,free=free,
                geometry_exact=(start,length,unit,total)==tuple(expected[x] for x in ('start','length','unit','total')),
                free_exact_before_report=free==expected['free']))
    # Read-only full allocation ownership, independently across both partitions.
    r['allocation']={}
    for v,w in rr.items():
        owners={};todo=[('',1)];dirs=files=0;errors=[]
        while todo:
            path,first=todo.pop();dirs+=1
            if not first:continue
            chain=list(w.chain(first))
            for c in chain:
                if c in owners:errors.append(['shared',c,path,owners[c]])
                owners[c]=path
            ended=False
            for c in chain:
                data=w.read_cluster(c)
                for off in range(0,len(data),64):
                    e=data[off:off+64];n=e[0]
                    if n in (0,255):ended=True
                    if ended or n==229:continue
                    assert 1<=n<=42
                    name=e[2:2+n].decode('ascii');p=path+'/'+name;start=int.from_bytes(e[44:48],'little')
                    if e[1]&16:todo.append((p,start));continue
                    files+=1
                    for cluster in w.chain(start) if start else []:
                        if cluster in owners:errors.append(['shared',cluster,p,owners[cluster]])
                        owners[cluster]=p
        orphans=[i for i in range(1,w.limit) if w.fat[i] not in (0,0xfffffff7) and i not in owners]
        r['allocation'][v]=dict(directories=dirs,files=files,owned_clusters=len(owners),bad_marked_clusters=sum(x==0xfffffff7 for x in w.fat[1:w.limit]),errors=errors,orphan_count=len(orphans),orphan_sample=orphans[:32])
r['probe_passed']=bool(r['report_present'] and len(r.get('queries',[]))==2 and all(x['geometry_exact'] and x['free_exact_before_report'] for x in r['queries']))
r['passed']=r['probe_passed'] and r['host_exit']['passed'] and r['qcow_exit']==0 and all(not x['errors'] and not x['orphan_count'] for x in r['allocation'].values())
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
