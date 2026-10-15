"""Final cold namespace/code/startup verification; no runtime recollection."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import ColdIO,m,sha,STARTUP
import importlib.util
spec=importlib.util.spec_from_file_location('stage',K/'normal-stage006.py')
# Reuse only the reviewed pure inventory definition, never execute a preparation script.
import ast
tree=ast.parse((K/'normal-stage006.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory')
import struct
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(K/'normal-stage006.py'),'exec'))
out=K/'installed-final001.json';assert not out.exists()
audit=json.loads((K/'emu006/audit.json').read_text());assert audit['runtime_components_all_passed']
source=Path('/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2')
assert sha(source)=='ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796'
disk=Path('/mnt/c/xwn405/runs/nt5-fresh405-emu006/hdd.qcow2');assert sha(disk)==audit['disk_sha256']
base=json.loads((K/'assembly006.json').read_text());m.fatx.PARTITIONS['E']=(5633024*512,10000048*512)
with ColdIO(disk) as io:
    wr=m.Writer(io,m.fatx.open_partition(io,disk,'E'));files=inventory(wr)
    assert STARTUP.lower() not in files
    code=[]
    for p,row in base['sources'].items():
        if row['kind'].startswith('fresh403'):
            assert files[p]==row['sha256'];code.append(dict(path=p,kind=row['kind'],sha256=files[p]))
    assert len(code)==15 and len({v['sha256'] for v in code})==11
    installers={}
    for name,service in [('Audio','xwnaci207'),('Network','nvnetnt5')]:
        b=wr.read('XWN405/'+name+'/install207.log');text=b.decode('ascii')
        for line in ['UPDATE_RESULT 1','UPDATE_ERROR 0','AFTER_SERVICE '+service,'DEVNODE_STATUS_RESULT 0','DEVNODE_PROBLEM 0','INSTALL207_END 0']:
            assert text.splitlines().count(line)==1,(name,line)
        assert [v for v in text.splitlines() if v.startswith('EXACT_TARGET_COUNT ')]==['EXACT_TARGET_COUNT 1']*2
        installers[name]=dict(passed=True,sha256=m.sha(b),service=service)
    audio_stack={}
    for p in ['drivers/sysaudio.sys','drivers/kmixer.sys','drivers/wdmaud.sys','drivers/portcls.sys','wdmaud.drv','streamci.dll']:
        b=wr.read('winnt/system32/'+p);audio_stack[p]=dict(bytes=len(b),sha256=m.sha(b))
assert len(files)==audit['allocation']['files']
private=Path('/mnt/c/xwn405/final-files001.json');assert not private.exists();private.write_text(json.dumps(files,indent=2)+'\n')
r=dict(fresh404_source_unchanged=True,final_disk_sha256=sha(disk),normal_diagnostic_startup_absent=True,
       all_final_files_read=len(files),private_file_manifest=str(private),private_file_manifest_sha256=sha(private),
       fresh403_components=code,unique_compiled_artifacts=11,installed_packages=installers,audio_stack=audio_stack,
       settings_utility_runtime_tested=False,physical_access=False,
       scope='Cold file bytes, namespace and installed-package evidence; not all Windows feature or file-semantics qualification')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['fresh403_components','audio_stack']}))
