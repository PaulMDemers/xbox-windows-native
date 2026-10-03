"""Read-only installed SYSTEM hive audit; no driver compatibility claim."""
import hashlib,json,pathlib,struct,sys
out=pathlib.Path(__file__).resolve().parent;root=out.parents[1]
sys.path.insert(0,str(root/'work/python-packages'))
from Registry import Registry
files=out.parent/'native-windows-nt5/installed-files'
hive=files/'WINNT/system32/config/system';reg=Registry.Registry(str(hive))
def values(path):
 try:return {v.name():v.value() for v in reg.open(path).values()}
 except Registry.RegistryKeyNotFoundException:return {}
select=values('Select');cs='ControlSet%03d'%select['Default']
groups=values(cs+'\\Control\\ServiceGroupOrder')['List']
orders=values(cs+'\\Control\\GroupOrderList')
actual={str(p.relative_to(files)).replace('\\','/').lower():p for p in files.rglob('*') if p.is_file()}
drivers=[]
for key in reg.open(cs+'\\Services').subkeys():
 vals={v.name():v.value() for v in key.values()};name=key.name()
 if vals.get('Start')!=0 and name.lower()!='ntfs':continue
 path=vals.get('ImagePath','system32\\drivers\\'+name+'.sys')
 f=actual.get(('WINNT/'+path.replace('\\','/')).lower())
 group=vals.get('Group','');tag=vals.get('Tag');order=orders.get(group,b'')
 tags=list(struct.unpack('<'+'I'*(len(order)//4),order))[1:] if order else []
 drivers.append({'service':name,'start':vals.get('Start'),'type':vals.get('Type'),'group':group,'tag':tag,'group_index':groups.index(group) if group in groups else len(groups),'tag_index':tags.index(tag) if tag in tags else len(tags),'image_path':path,'error_control':vals.get('ErrorControl'),'dependencies':{k:vals[k] for k in ['DependOnService','DependOnGroup'] if k in vals},'selection_reason':'Start=0' if vals.get('Start')==0 else 'NTFS boot filesystem explicitly added by CmpFindDrivers','available_in_prior_extraction':bool(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest() if f else None})
drivers.sort(key=lambda d:(d['group_index'],d['tag_index'],d['service'].lower()))
critical=[]
for key in reg.open(cs+'\\Control\\CriticalDeviceDatabase').subkeys():
 vals={v.name():v.value() for v in key.values()}
 if str(vals.get('Service','')).lower() in ['atapi','intelide','pciide'] or 'ven_10de' in key.name().lower():
  critical.append({'id':key.name(),**vals})
report={'scope':'Static service selection and group/tag ordering only; equal-rank order and dependencies must be verified from runtime loader lists. Missing extraction entries do not imply missing disk files. No registry modification.', 'system_sha256':hashlib.sha256(hive.read_bytes()).hexdigest(),'select':select,'normal_boot_control_set':cs,'boot_filesystem':'Ntfs','drivers':drivers,'critical_devices':critical,'pciide_service':values(cs+'\\Services\\PciIde'),'nls':values(cs+'\\Control\\Nls\\CodePage'),'findings':['IntelIde is enabled for the PC fixture; PciIde is disabled (Start=4).','No boot-controller mapping for PCI VEN_10DE DEV_01BC is installed in this hive.','NTFS Start=4 does not exclude it from this loader: CmpFindDrivers explicitly adds the filesystem of the SYSTEM hive volume.','Read-only loader access does not test Windows atapi/pciide on Xbox hardware.']}
(out/'boot-driver-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'control_set':cs,'selected_count':len(drivers),'services':[d['service'] for d in drivers],'missing_prior_extraction':[d['image_path'] for d in drivers if not d['available_in_prior_extraction']],'findings':report['findings']},indent=2))
