"""Independent cold verification of the actual unused-device package, not function support."""
from common import *
dest=k/'candidate001/package-verification.json';assert not dest.exists()
out=k/'candidate001';inv=read(out/'device-inventory.json');a=read(out/'audit.json');f=read(k/'fixture-candidate001.json')
disk=ws/'work/runs/nt5-settled181-candidate001/hdd.qcow2';assert (disk.parent/'cleanup.json').exists()
expected={'01B0':'Xbox audio processor (unused; no function driver)','01B4':'Xbox SMBus controller (unused; no function driver)','0005':'QEMU PCI test function (unused; no function driver)'}
before={v['path']:v for v in inv['hives'][0]['devices']};results=[]
with ColdIO(disk) as io:
 rr=readers(io,disk)
 for row in inv['hives'][1]['devices']:
  vals=row['values'];d=row['driver_values'] or {};get=lambda key:vals.get(key,{}).get('decoded')
  ident=next(v for v in expected if '&DEV_'+v in row['path']);prev=before.get(row['path'])
  inf=d.get('InfPath',{}).get('decoded');section=d.get('InfSection',{}).get('decoded');data=None
  if inf:
   try:data=rr['F'].read('winnt/inf/'+inf)
   except KeyError:pass
  same_ids=prev is None and ident=='0005' or (prev is not None and all(vals.get(v)==prev['values'].get(v) for v in ['HardwareID','CompatibleIDs','LocationInformation']))
  check=dict(path=row['path'],identity_preserved=same_ids,description=get('DeviceDesc'),driver=get('Driver'),service=get('Service'),config_flags=get('ConfigFlags'),class_guid=get('ClassGUID'),
   inf_path=inf,inf_section=section,inf_sha256=None if data is None else m.sha(data),exact_inf=data==(k/'xwnunused179.inf').read_bytes(),function_driver_supported=False)
  check['package_bound']=check['identity_preserved'] and check['description']==expected[ident] and bool(check['driver']) and not check['service'] and check['config_flags'] in [None,0] and check['class_guid']=='{4D36E97D-E325-11CE-BFC1-08002BE10318}' and section=='XWN.Unused' and check['exact_inf']
  results.append(check)
r=dict(physical_access=False,debugger=False,devices=results,package_bound=len(results)==3 and all(v['package_bound'] for v in results),setupapi_history_preserved=a['setupapi_history_preserved'],
 runtime_guard_idle=a['runner_normal_restart'],normal_lifecycle=a['workload_passed'],integrity_passed=a['integrity_passed'],strict_qualification_passed=a['strict_qualification_passed'],
 limits='A bound null INF records unused devices with no function service; audio/SMBus/test protocol remain unsupported. Configuration intervention, not a driver/race fix. This new subsequent boot has no installer helper, INF restaging or UI action.')
r['configuration_observed']=r['package_bound'] and r['setupapi_history_preserved'] and r['runtime_guard_idle'] and r['normal_lifecycle'] and r['integrity_passed']
save(dest,r);print(json.dumps(r,indent=2))
