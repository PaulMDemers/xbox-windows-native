"""Read-only identities of installed storage binaries before/after closed diagnostics."""
import sys
from common import *
case=sys.argv[1];assert case in ['serial001','serial002','serial003','serial004','serial005']
out=k/case;dest=out/'storage-binaries.json';assert not dest.exists()
f=read(k/('fixture-'+case+'.json'));run=ws/('work/runs/nt5-dump-config-trace-'+case);assert (run/'cleanup.json').exists()
paths=['ftdisk.sys','disk.sys','atapi.sys','scsiport.sys','classpnp.sys','diskdump.sys']
r=dict(scope=__doc__,case=case,physical_access=False,files=[])
for phase,disk in [('before',ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']),('after',run/'hdd.qcow2')]:
 with ColdIO(disk) as io:
  volume=readers(io,disk)['F']
  for name in paths:
   data=volume.read('winnt/system32/drivers/'+name)
   if phase=='before':r['files'].append(dict(name=name,size=len(data),sha256=m.sha(data)))
   else:
    row=next(v for v in r['files'] if v['name']==name);row['after_sha256']=m.sha(data);row['unchanged']=row['sha256']==row['after_sha256'];assert row['unchanged']
   (out/'artifacts'/(phase+'-'+name)).write_bytes(data)
r['passed']=all(v['unchanged'] for v in r['files']);save(dest,r);print(case+' storage binaries unchanged')
