"""Read-only full framebuf directory comparison against the exact303 Git tree."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;parent=K.parent/'hd-surface303';b=json.loads((parent/'build003.json').read_text())
root=Path('/home/paul/xbox-windows-native/build/hd-surface303-build001/source');prefix='win32ss/drivers/displays/framebuf/'
out=K/'driver-source-review002.json';assert not out.exists()
entries=subprocess.check_output(['git','-C',str(root),'ls-tree','-r',b['source_tree'],'--',prefix],text=True).splitlines();files={};finds=[]
for row in entries:
    head,name=row.split('\t');mode,kind,oid=head.split();assert kind=='blob'
    data=(root/name).read_bytes();assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid
    files[name]=dict(git_blob=oid,sha256=hashlib.sha256(data).hexdigest())
    for i,line in enumerate(data.decode().splitlines(),1):
        if any(x in line for x in ['XWN_BODY_PROFILE','XwnProfileStart','XwnProfileEnd','EngQueryPerformanceCounter']):finds.append(dict(file=name,line=i,text=line))
assert files and finds and b['cases']['candidate001']['definitions']['XWN_BODY_PROFILE']=='OFF'
out.write_text(json.dumps(dict(passed=True,source_tree=b['source_tree'],files=files,findings=finds,actual_source_root=str(root),driver_changed=False,production_body_profile='OFF',limits='Full tracked framebuf source identity only. No new matched profiling driver build or runtime; private source and original definitions unchanged.'),indent=2)+'\n')
print('PASS',len(files),'exact tree files;',len(finds),'clock/source leads')
