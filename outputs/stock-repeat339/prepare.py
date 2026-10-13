"""Intentional second boot of successful335 installation; never reset its hives/trace."""
import json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001';P=Path('/mnt/e/xwn339/seed001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not out.exists() and not P.exists()
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
from stock_io002 import readers,scan
old=K.parent/'stock-runtime335/emu001';audit=json.loads((old/'audit.json').read_text());assert audit['scoped_combined_passed'] and audit['orderly_host_exit']
parent=Path('/mnt/e/xwn335/runs/nt5-stock335-emu001/hdd.qcow2');assert (parent.parent/'cleanup.json').exists()
assert shutil.disk_usage('/mnt/e').free-12*1024**3>20*1024**3
oldfixture=json.loads((old/'fixture.json').read_text());parenthash=sha(parent)
out.mkdir();(out/'artifacts').mkdir();P.mkdir(parents=True);raw=P/'repeat.raw';target=P/'source.qcow2'
r=dict(prepared=False,physical_access=False,intentional_repeat_boot_of_successful335=True,parent=str(parent),parent_sha256=parenthash,registry_edited=False,trace_reseeded=False,changes=[],retained_first_boot_files={})
def save():(out/'preparation.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
    subprocess.run(['qemu-img','check',str(parent)],check=True)
    subprocess.run(['qemu-img','convert','-O','raw',str(parent),str(raw)],check=True)
    with raw.open('r+b') as fp:
        w=m.Writer(fp,m.fatx.open_partition(fp,raw,'E'))
        first=1
        for name in ['xwndemo251']:first=int.from_bytes(w.directory(first)['entries'][name][2][44:48],'little')
        def capture(c,path):
            if not c:return
            for name,(_,_,e) in w.directory(c)['entries'].items():
                child=path+'/'+name;start=int.from_bytes(e[44:48],'little')
                if e[1]&16:capture(start,child)
                else:r['retained_first_boot_files'][child]=m.sha(w.read(child))
        capture(first,'xwndemo251')
        assert 'xwnstock339' not in w.directory(1)['entries']
        for name in ['runner.exe','wizard.exe','state.exe','probe.exe','replay.exe']:
            data=w.read('xwndemo251/'+name)
            if name=='wizard.exe':
                data=Path('/mnt/e/xwn338/build001/wizard.exe').read_bytes();assert m.sha(data)==json.loads((K.parent/'stock-focus338/build-review001.json').read_text())['binary_sha256']
            r['changes'].append(w.write('xwnstock339/'+name,data))
        before=w.read(STARTUP);assert before==b'@echo off\r\nC:\\xwndemo251\\runner.exe /emulator\r\nexit\r\n'
        after=b'@echo off\r\nC:\\xwnstock339\\runner.exe /emulator\r\nexit\r\n'
        # Existing bounded same-chain overwrite helper; private host image only.
        m.replace(w,STARTUP,after);w.flush();fp.flush()
        r['startup']=dict(before_sha256=m.sha(before),after_sha256=m.sha(after))
        for n in ['system','software','default','sam','security']:(out/'artifacts'/('before-'+n)).write_bytes(w.read('winnt/system32/config/'+n))
        for p,h in r['retained_first_boot_files'].items():assert m.sha(w.read(p))==h
    subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
    subprocess.run(['qemu-img','compare','-f','raw','-F','qcow2',str(raw),str(target)],check=True)
    subprocess.run(['qemu-img','check',str(target)],check=True)
    assert sha(parent)==parenthash
    with ColdIO(parent) as a,ColdIO(target) as b:
        aa,bb=readers(a,parent)['E'],readers(b,target)['E']
        for name in ['system','software','default','sam','security']:
            assert aa.read('winnt/system32/config/'+name)==bb.read('winnt/system32/config/'+name)
        assert aa.read('winnt/system32/xwn-video-trace.bin')==bb.read('winnt/system32/xwn-video-trace.bin')
    f={**oldfixture,'fixture_path_linux':str(target),'fixture_path_windows':'E:'+str(target)[6:],'fixture_sha256':sha(target),'parent':str(parent),'parent_sha256':parenthash,'namespace':'xwnstock339'}
    f['files']={**oldfixture['files'],'E/'+STARTUP:r['startup']['after_sha256']}
    f['protected']={**f['protected'],**{'E/'+v['path']:v['sha256'] for v in r['changes']}}
    r.update(prepared=True,source_sha256=f['fixture_sha256'],hives_and_trace_byte_identical_to_first_boot=True)
    (out/'fixture.json').write_text(json.dumps(f,indent=2)+'\n')
    scan(target,out/'before-allocation/artifacts');assert json.loads((out/'before-allocation/allocation.json').read_text())['allocation_consistent']
except BaseException as e:r['error']=repr(e);raise
finally:save()
print('Repeat boot prepared with first-boot hives and output intact',flush=True)
