"""Audit installed SYSTEM hive and PE files without loading or modifying them."""
import hashlib,json,pathlib,struct,sys
r=pathlib.Path(__file__).resolve().parents[2];out=r/'outputs/native-windows-nt5';files=out/'installed-files'
sys.path.insert(0,str(r/'work/python-packages'))
from Registry import Registry
import pefile
system=files/'WINNT/system32/config/system'
reg=Registry.Registry(str(system))
def values(path):
    try:return {v.name():v.value() for v in reg.open(path).values()}
    except Registry.RegistryKeyNotFoundException:return None
select=values('Select');cs='ControlSet%03d'%select['Current']
services={name:values(cs+'\\Services\\'+name) for name in ['Atapi','IntelIde','PciIde','Pci','Isapnp','Disk','Classpnp','Ntfs','Fastfat','Scsiport','Mountmgr','Ftdisk','Dmio','Dmload','Partmgr','Ksecdd']}
services={name:None if vals is None else {key:vals[key] for key in ('Start','Type','Group','ImagePath','ErrorControl','Tag') if key in vals} for name,vals in services.items()}
cd=[]
try:
    for key in reg.open(cs+'\\Control\\CriticalDeviceDatabase').subkeys():
        vals={v.name():v.value() for v in key.values()}
        if str(vals.get('Service','')).lower() in ('atapi','intelide','pciide'):cd.append({'id':key.name(),'values':vals})
except Registry.RegistryKeyNotFoundException:pass
versions={}
for name in ('ntoskrnl.exe','hal.dll','bootvid.dll'):
    path=files/'WINNT/system32'/name;p=pefile.PE(str(path));v=p.VS_FIXEDFILEINFO[0]
    version=[v.FileVersionMS>>16,v.FileVersionMS&65535,v.FileVersionLS>>16,v.FileVersionLS&65535]
    versions[name]={'version':'.'.join(map(str,version)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
data=system.read_bytes();seq1,seq2=struct.unpack_from('<II',data,4)
setup=values('Setup');setup={k:v for k,v in (setup or {}).items() if k in ('SystemSetupInProgress','SetupType','CmdLine')}
report={'scope':'Read-only registry and file inspection; these PC IDE settings do not prove Xbox MCPX compatibility.',
        'system_hive_sequences':[seq1,seq2],'system_hive_clean':seq1==seq2,'select':select,'setup':setup,
        'system_control_set':cs,'services':services,'ide_critical_device_database':cd,'versions':versions,
        'boot_ini':(files/'boot.ini').read_text(encoding='cp1252')}
(out/'installed-system-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'clean_hive':seq1==seq2,'setup':setup,'versions':versions,'services':services},indent=2))
