"""Build an offline IDE-enabled derivative; never write the PC base disk.
Run with the task-private hivex/ntfs-3g runtime under WSL.
"""
import argparse,hashlib,json,os,pathlib,shutil,struct,subprocess,sys
root=pathlib.Path('/home/paul/xbox-windows-native')
workspace=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out=workspace/'outputs/native-windows-nt5-kernel'
runtime=root/'toolchains/offline-disk/root'
sys.path.insert(0,str(runtime/'usr/lib/python3/dist-packages'))
import hivex
base=workspace/'outputs/native-windows-nt5/artifacts/windows2000-pc-base.qcow2'
parser=argparse.ArgumentParser();parser.add_argument('--add-pciide',action='store_true');parser.add_argument('--video',action='store_true');parser.add_argument('--legacy-indexes',action='store_true');parser.add_argument('--usb',action='store_true');args=parser.parse_args()
if args.usb:assert args.video and args.legacy_indexes
revision='005' if args.usb else ('004' if args.legacy_indexes else ('003' if args.video else ('002' if args.add_pciide else '001')))
target=out/f'artifacts/windows2000-xbox-ide-{revision}.qcow2'
temp=root/f'fixtures/offline-ide-{revision}'
assert not target.exists() and not temp.exists()
temp.mkdir(parents=True)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
base_hash=sha(base)
assert base_hash=='59d7e920b19f10a05ba3a914f05c90e43764f2a7506a8bb16e816b781c54785e'
def run(args):return subprocess.run(list(map(str,args)),check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True).stdout
record={'base_sha256':base_hash,'changes':[],'scope':'Offline boot-service and critical-device binding experiment, not proof of IDE driver compatibility.'}
try:
 original=workspace/'outputs/native-windows-nt5/installed-files/WINNT/system32/config/system'
 hive=temp/'SYSTEM';shutil.copyfile(original,hive)
 h=hivex.Hivex(str(hive),write=True)
 def node(path,create=False):
  n=h.root()
  for name in path.split('\\'):
   child=h.node_get_child(n,name)
   if not child and create:child=h.node_add_child(n,name)
   assert child,path
   n=child
  return n
 for cs in ['ControlSet001','ControlSet002']:
  service=node(cs+'\\Services\\PciIde')
  assert h.value_dword(h.node_get_value(service,'Start'))==4
  h.node_set_value(service,{'key':'Start','t':4,'value':struct.pack('<I',0)})
  path=cs+'\\Control\\CriticalDeviceDatabase\\pci#ven_10de&dev_01bc'
  assert not h.node_get_child(node(cs+'\\Control\\CriticalDeviceDatabase'),'pci#ven_10de&dev_01bc')
  critical=node(path,True)
  for key,value in [('Service','pciide'),('ClassGUID','{4D36E96A-E325-11CE-BFC1-08002BE10318}')]:
   h.node_set_value(critical,{'key':key,'t':1,'value':(value+'\0').encode('utf-16le')})
  record['changes'].append({'control_set':cs,'PciIde_Start':{'before':4,'after':0},'critical_device':path,'service':'pciide'})
  if args.video:
   def set_values(path,values):
    key=node(path,True)
    for name,value in values.items():
     kind=4 if isinstance(value,int) else (7 if isinstance(value,list) else 1)
     data=struct.pack('<I',value) if kind==4 else (('\0'.join(value)+'\0\0') if kind==7 else value+'\0').encode('utf-16le')
     h.node_set_value(key,{'key':name,'t':kind,'value':data})
   service=cs+'\\Services\\XboxVnt5'
   set_values(service,{'Type':1,'Start':1,'ErrorControl':1,'Group':'Video','ImagePath':'system32\\drivers\\xboxvnt5.sys'})
   set_values(service+'\\Device0',{'InstalledDisplayDrivers':['framebuf'],'VgaCompatible':0,'Device Description':'Xbox NV2A firmware framebuffer','DefaultSettings.XResolution':640,'DefaultSettings.YResolution':480,'DefaultSettings.BitsPerPel':32,'DefaultSettings.VRefresh':60})
   set_values(cs+'\\Control\\CriticalDeviceDatabase\\pci#ven_10de&dev_02a0',{'Service':'XboxVnt5','ClassGUID':'{4D36E968-E325-11CE-BFC1-08002BE10318}'})
   set_values(cs+'\\Services\\VgaSave',{'Start':4})
   record['changes'].append({'control_set':cs,'video_service':'XboxVnt5','display_driver':'framebuf','critical_device':'PCI VEN_10DE DEV_02A0','VgaSave_Start':4})
  if args.usb:
   # Service settings and class GUIDs come from the supplied SP4 INF files.
   for name,start,group,error in [('openhci',3,'Base',1),('usbhub',3,'Base',1),('HidUsb',2,'extended base',0),('kbdhid',1,'Keyboard Port',0),('mouhid',3,'Pointer Port',0)]:
    set_values(cs+'\\Services\\'+name,{'Type':1,'Start':start,'ErrorControl':error,'Group':group,'ImagePath':'system32\\drivers\\'+name.lower()+'.sys'})
   set_values(cs+'\\Services\\kbdhid\\Parameters',{'WorkNicely':0})
   set_values(cs+'\\Services\\mouhid\\Parameters',{'UseOnlyMice':0,'TreatAbsoluteAsRelative':0,'TreatAbsolutePointerAsAbsolute':0})
   usb_class='{36FC9E60-C465-11CF-8056-444553540000}'
   bindings=[('pci#ven_10de&dev_01c2','openhci',usb_class),('usb#root_hub','usbhub',usb_class),('usb#class_09','usbhub',usb_class),('usb#class_03','HidUsb','{745A17A0-74D3-11D0-B6FE-00A0C90F57DA}'),('hid_device_system_keyboard','kbdhid','{4D36E96B-E325-11CE-BFC1-08002BE10318}'),('hid_device_system_mouse','mouhid','{4D36E96F-E325-11CE-BFC1-08002BE10318}')]
   for hardware,service,cls in bindings:
    set_values(cs+'\\Control\\CriticalDeviceDatabase\\'+hardware,{'Service':service,'ClassGUID':cls})
   for cls,filter_ in [('{4D36E96B-E325-11CE-BFC1-08002BE10318}','kbdclass'),('{4D36E96F-E325-11CE-BFC1-08002BE10318}','mouclass')]:
    set_values(cs+'\\Control\\Class\\'+cls,{'UpperFilters':[filter_]})
   record['changes'].append({'control_set':cs,'usb_bindings':bindings,'source':'Supplied SP4 usb.inf, input.inf, keyboard.inf, msmouse.inf'})
 h.commit(str(hive));del h
 if args.legacy_indexes:
  from nt5_hive_indexes import normalize
  converted,record['nt5_index_conversion']=normalize(hive.read_bytes());hive.write_bytes(converted)
 # Separate parser/read handles verify serialized registry changes.
 h=hivex.Hivex(str(hive))
 for cs in ['ControlSet001','ControlSet002']:
  assert h.value_dword(h.node_get_value(node(cs+'\\Services\\PciIde'),'Start'))==0
  assert h.value_string(h.node_get_value(node(cs+'\\Control\\CriticalDeviceDatabase\\pci#ven_10de&dev_01bc'),'Service'))=='pciide'
 del h
 raw=temp/'disk.raw';partition=temp/'partition.ntfs'
 run(['qemu-img','convert','-O','raw',base,raw])
 with raw.open('rb') as f:
  mbr=f.read(512);assert mbr[510:512]==b'\x55\xaa' and mbr[450]==7
  start,sectors=struct.unpack_from('<II',mbr,454);offset=start*512;size=sectors*512
  assert start==63 and sectors==4185153
  f.seek(offset)
  with partition.open('xb') as dest:
   remaining=size
   while remaining:
    block=f.read(min(4*1024*1024,remaining));assert block;dest.write(block);remaining-=len(block)
 record['ntfscp_log']=run([runtime/'usr/sbin/ntfscp',partition,hive,'/WINNT/system32/config/system'])
 if args.add_pciide or args.video:
  seven=root/'toolchains/7zip/root/usr/lib/7zip/7z'
  media=workspace/'outputs/EN_WIN2000_PRO_SP4.ISO'
  run([seven,'x','-y',f'-o{temp}/media',media,'I386/PCIIDE.SY_'])
  compressed=temp/'media/I386/PCIIDE.SY_'
  assert compressed.exists()
  run([seven,'x','-y',f'-o{temp}/driver',compressed])
  driver=next(p for p in (temp/'driver').iterdir() if p.name.lower()=='pciide.sys')
  run([runtime/'usr/sbin/ntfscp',partition,driver,'/WINNT/system32/drivers/pciide.sys'])
  record['added_driver']={'path':'WINNT/system32/drivers/pciide.sys','sha256':sha(driver),'source_iso_sha256':sha(media)}
  driver_out=out/'installed-files/WINNT/system32/drivers/pciide.sys'
  driver_out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(driver,driver_out)
 if args.video:
  video=out/'artifacts/xboxvnt5.sys'
  assert video.exists()
  run([runtime/'usr/sbin/ntfscp',partition,video,'/WINNT/system32/drivers/xboxvnt5.sys'])
  record['video_miniport']={'sha256':sha(video),'path':'WINNT/system32/drivers/xboxvnt5.sys'}
 if args.usb:
  media_files=workspace/'work/usb-media/expanded'
  by_name={p.name.lower():p for p in media_files.iterdir() if p.is_file()}
  record['usb_files']=[]
  for name in ['openhci.sys','usbd.sys','usbhub.sys','hidusb.sys','hidclass.sys','hidparse.sys','kbdhid.sys','mouhid.sys','hid.dll','pid.dll']:
   source=by_name[name];destination='WINNT/system32/'+('drivers/' if name.endswith('.sys') else '')+name
   run([runtime/'usr/sbin/ntfscp',partition,source,'/'+destination])
   record['usb_files'].append({'path':destination,'sha256':sha(source)})
 # Read back through an independent NTFS implementation before assembling disk.
 extracted=temp/'readback'
 run([root/'toolchains/7zip/root/usr/lib/7zip/7z','x','-y','-ssc-',f'-o{extracted}',partition,'WINNT/system32/config/system'])
 back=next(p for p in extracted.rglob('*') if p.is_file())
 assert back.read_bytes()==hive.read_bytes()
 if args.usb:
  run([root/'toolchains/7zip/root/usr/lib/7zip/7z','x','-y','-ssc-',f'-o{extracted}',partition,*[f['path'] for f in record['usb_files']]])
  actual={str(p.relative_to(extracted)).lower():p for p in extracted.rglob('*') if p.is_file()}
  for entry in record['usb_files']:assert sha(actual[entry['path'].lower()])==entry['sha256']
  record['usb_readback_equal']=True
 if args.video:
  run([root/'toolchains/7zip/root/usr/lib/7zip/7z','x','-y','-ssc-',f'-o{extracted}',partition,'WINNT/system32/drivers/xboxvnt5.sys','WINNT/system32/framebuf.dll'])
  actual={str(p.relative_to(extracted)).lower():p for p in extracted.rglob('*') if p.is_file()}
  assert sha(actual['winnt/system32/drivers/xboxvnt5.sys'])==sha(video)
  assert sha(actual['winnt/system32/framebuf.dll'])==sha(out/'installed-files/WINNT/system32/framebuf.dll')
  record['video_file_readback_equal']=True
 with raw.open('r+b') as dest,partition.open('rb') as source:
  dest.seek(offset);shutil.copyfileobj(source,dest,4*1024*1024)
 run(['qemu-img','convert','-O','qcow2',raw,target])
 record.update(disk_sha256=sha(target),system_before_sha256=sha(original),system_after_sha256=sha(hive),hive_bytes=hive.stat().st_size,ntfs_readback_equal=True)
 record['qemu_img_check']=run(['qemu-img','check',target])
 assert sha(base)==base_hash
 record['base_preserved']=True
finally:
 assert temp.resolve().is_relative_to((root/'fixtures').resolve())
 shutil.rmtree(temp)
 record['temporary_raws_removed']=True
 (out/f'ide-disk-{revision}.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
