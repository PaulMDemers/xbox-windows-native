"""Unique matched children of the never-executed339 prepared E seed; no hive edits."""

import json,os,shutil,subprocess,sys,struct

from pathlib import Path

K=Path(__file__).resolve().parent;W=K.parents[1];case=sys.argv[1];assert case in ['candidate002'] and os.environ.get('XWN_BUILD_LEASE')=='held'

out=K/case;P=Path('/mnt/e/xwn358')/case;assert not out.exists() and not P.exists()

sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,m,sha,STARTUP

from stock_io002 import readers,scan

old=json.loads((K.parent/'stock-repeat339/emu001/fixture.json').read_text());parent=Path(old['fixture_path_linux']);assert sha(parent)==old['fixture_sha256']

assert json.loads((K.parent/'stock-repeat339/emu001/audit.json').read_text())['scoped_combined_passed']

assert json.loads((K.parent/'memory-warm357/binary-review001.json').read_text())['passed']

image=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(parent)]));assert image['virtual-size']==10000000000 and 'backing-filename' not in image

mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(parent)]))

data_bytes=sum(v['length'] for v in mapping if v['data'])

reserve=data_bytes+512*1024**2

assert shutil.disk_usage('/mnt/e').free-reserve>=20*1024**3,'Projected allocated extents plus512MiB metadata/new payload reserve'

rawroot=Path('/home/paul/xbox-windows-native/build/memory358-staging002-'+case)

assert not rawroot.exists()

sys.path.insert(0,str(W/'tools'));from build_space import require_space

rawspace=require_space(rawroot);assert all(v['free_bytes']-image['virtual-size']-512*1024**2>=20*1024**3 for v in rawspace['checks'])

rawroot.mkdir(parents=True)

out.mkdir();(out/'artifacts').mkdir();P.mkdir(parents=True);raw=rawroot/'staging.raw';target=P/'source.qcow2';ns='xwnmemory358'

r=dict(prepared=False,physical_access=False,parent=str(parent),parent_sha256=sha(parent),registry_edited=False,trace_reseeded=False,changes=[],same_never_executed_parent=True,projected_reserve_bytes=reserve,parent_data_bytes=data_bytes,raw_staging_space=rawspace,raw_staging_root=str(rawroot))

def save():(out/'preparation.json').write_text(json.dumps(r,indent=2)+'\n')

save()

try:

    subprocess.run(['qemu-img','check',str(parent)],check=True);subprocess.run(['qemu-img','convert','-O','raw',str(parent),str(raw)],check=True)

    with raw.open('r+b') as fp:

        wr=m.Writer(fp,m.fatx.open_partition(fp,raw,'E'));assert ns not in wr.directory(1)['entries']

        for name in ['runner.exe','wizard.exe','state.exe','probe.exe','replay.exe']:

            data=wr.read('xwnstock339/'+name)

            if name=='replay.exe':

                data=Path('/mnt/e/xwn357/probe/build001/replay.exe').read_bytes();assert m.sha(data)==json.loads((K.parent/'memory-warm357/probe/build-review001.json').read_text())['binary_sha256']

            r['changes'].append(wr.write(ns+'/'+name,data))

        dll=Path('/mnt/e/xwn357/build001/diagnostic001/xwnown.dll');data=dll.read_bytes();assert m.sha(data)==json.loads((K.parent/'memory-warm357/build001.json').read_text())['cases']['diagnostic001']['sha256']

        before=wr.read('winnt/system32/xwnown.dll')
        at=1;parts=wr.parts('winnt/system32/xwnown.dll')
        for part in parts[:-1]:at=struct.unpack_from('<I',wr.directory(at)['entries'][part.lower()][2],44)[0]
        dc,off,entry=wr.directory(at)['entries'][parts[-1]]
        chain=list(wr.chain(struct.unpack_from('<I',entry,44)[0]));need=(len(data)+wr.p.cluster_size-1)//wr.p.cluster_size
        added=[]
        if need>len(chain):
            added=wr.allocate(need-len(chain));wr.fat[chain[-1]]=added[0]
        r['driver_allocation']=dict(before_clusters=len(chain),added_clusters=added,cluster_bytes=wr.p.cluster_size)
        m.replace(wr,'winnt/system32/xwnown.dll',data);r['driver']=dict(path='winnt/system32/xwnown.dll',before_sha256=m.sha(before),sha256=m.sha(data))

        before=wr.read(STARTUP);assert before==b'@echo off\r\nC:\\xwnstock339\\runner.exe /emulator\r\nexit\r\n'

        after=b'@echo off\r\nC:\\xwnmemory358\\runner.exe /emulator\r\nexit\r\n';m.replace(wr,STARTUP,after);wr.flush();fp.flush()

        r['startup']=dict(before_sha256=m.sha(before),after_sha256=m.sha(after))

        for n in ['system','software','default','sam','security']:(out/'artifacts'/('before-'+n)).write_bytes(wr.read('winnt/system32/config/'+n))

    subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)

    subprocess.run(['qemu-img','compare','-f','raw','-F','qcow2',str(raw),str(target)],check=True);subprocess.run(['qemu-img','check',str(target)],check=True)

    assert sha(parent)==r['parent_sha256']

    with ColdIO(parent) as a,ColdIO(target) as b:

        aa,bb=readers(a,parent)['E'],readers(b,target)['E']

        for n in ['system','software','default','sam','security']:assert aa.read('winnt/system32/config/'+n)==bb.read('winnt/system32/config/'+n)

        assert aa.read('winnt/system32/xwn-video-trace.bin')==bb.read('winnt/system32/xwn-video-trace.bin')

        assert bb.read('winnt/system32/xwnown.dll')==dll.read_bytes()

        for v in r['changes']:assert m.sha(bb.read(v['path']))==v['sha256']

    f={**old,'fixture_path_linux':str(target),'fixture_path_windows':'E:'+str(target)[6:],'fixture_sha256':sha(target),'parent':str(parent),'parent_sha256':r['parent_sha256'],'namespace':ns,'profile_mode':1,'primary_mode':1}

    for field in ['files','protected']:

        f[field]=dict(old[field])

        for p,h in [(STARTUP,r['startup']['after_sha256']),('winnt/system32/xwnown.dll',r['driver']['sha256'])]+[(v['path'],v['sha256']) for v in r['changes']]:

            keys=[n for n in f[field] if n.lower()==('E/'+p).lower()]

            for n in keys:f[field][n]=h

            if not keys:f[field]['E/'+p]=h

    (out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')

    scan(target,out/'before-allocation/artifacts');assert json.loads((out/'before-allocation/allocation.json').read_text())['allocation_consistent']

    # Only disposable verified raw staging file; never a QCOW parent or failure disk.

    assert raw.resolve().parent==rawroot.resolve() and raw.name=='staging.raw';raw.unlink()

    r.update(prepared=True,source_sha256=f['fixture_sha256'],raw_staging_removed_after_virtual_equality=True,hives_and_trace_unchanged=True);save()

except BaseException as e:r['error']=repr(e);save();raise

print(case,'prepared with immutable parent and clean E allocation',flush=True)

