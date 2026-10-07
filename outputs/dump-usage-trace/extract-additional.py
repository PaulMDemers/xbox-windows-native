"""Cold extraction of additional observed storage-stack code, without guest changes."""
from common import *
k=Path(__file__).resolve().parent;fixture=read(k/'fixture-dispatch001.json');disk=ws/'outputs/native-windows-fatx-forensics/artifacts'/fixture['fixture_name'];assert sha(disk)==fixture['fixture_sha256']
art=k/'artifacts';art.mkdir(exist_ok=True);rows=[]
paths=[('F','winnt/system32/drivers/'+n) for n in ['diskperf.sys','partmgr.sys','pci.sys','pciide.sys','pciidex.sys','intelide.sys','wmilib.sys','dmio.sys','dmload.sys','mountmgr.sys']]+[('E','Applications/XWNFBoot/loader/halxboxnt5.dll')]
with ColdIO(disk) as io:
 rr=readers(io,disk)
 for vol,path in paths:
  name=path.split('/')[-1].lower();name='hal.dll' if name=='halxboxnt5.dll' else name
  target=art/('cold-'+name);assert not target.exists();data=rr[vol].read(path);target.write_bytes(data);rows.append(dict(name=name,volume=vol,guest_path=path,size=len(data),sha256=m.sha(data),private_file=target.name))
output=k/'additional-modules.json';assert not output.exists();save(output,dict(scope=__doc__,fixture_sha256=sha(disk),files=rows));print('Pinned',len(rows),'additional storage/bus/HAL files')
