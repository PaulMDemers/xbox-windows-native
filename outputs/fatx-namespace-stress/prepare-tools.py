"""Use candidate0100 with five-worker stress, retaining the same cold-audit policy."""
import shutil
from pathlib import Path
k=Path(__file__).resolve().parent;prior=k.parent/'fatx-namespace-order'
names=['Run.ps1','supervise.py','trial.py','audit.py','audit-allocation.py','capture-timeout.py','decode-timeout.py','qualify.py','prepare-fixture.py']
for name in names:
    target=k/name;assert not target.exists()
    text=(prior/name).read_text().replace('fatx-namespace-order','fatx-namespace-stress')
    if name=='Run.ps1':text=text.replace('-Seconds 900','-Seconds 1200')
    if name=='supervise.py':text=text.replace('time.monotonic()+600','time.monotonic()+900')
    if name=='decode-timeout.py':
        text=text.replace("process['diagnostic_counters']={name:list(struct.unpack('<3I',read(image_base+symbols['symbols'][name],12)))", "process['diagnostic_counters']={name:list(struct.unpack('<5I',read(image_base+symbols['symbols'][name],20)))")
    if name=='audit.py':
        text=text.replace('ATTEMPT_ONCE 3 500','ATTEMPT_ONCE 5 500').replace(r'ERRORS 0 0 0\r\nCOMPLETE',r'ERRORS 0 0 0\r\nNAMESPACE_COUNTS 500 500 0\r\nNAMESPACE_ERRORS 0 0 0\r\nCOMPLETE')
        marker='\ndef recurring(v):'
        assert marker in text
        extra='''    try:data=after['F'].read('xwncc01/meta.bin')
    except KeyError:data=b''
    r['worker_files'].append(dict(worker='metadata',bytes=len(data),sha256=m.sha(data),exact=data==bytes((j*19+499*31)&255 for j in range(4097))))
    try:after['F'].read('xwncc01/meta.tmp');r['intermediate_absent']=False
    except KeyError:r['intermediate_absent']=True
'''
        text=text.replace(marker,extra+marker).replace("r['workload_completed'] and all", "r['workload_completed'] and r['intermediate_absent'] and all")
    if name=='qualify.py':text=text.replace("len(a['worker_files'])==2","len(a['worker_files'])==3")
    if name=='prepare-fixture.py':text=text.replace('Two regular-file workers and one volume-flush worker.', 'Two regular-file workers, volume flush, metadata/rename and directory enumeration;500 rounds each.')
    target.write_text(text)
for name in ['binary-review.json','fatx-layouts.json','kernel-resource-layouts.json']:
    shutil.copyfile(prior/name,k/name)
shutil.copyfile(prior/'artifacts/xwnfatx.sys',k/'artifacts/xwnfatx.sys')
