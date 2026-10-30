"""Restore existing Windows AGP bridge setup while retaining GPU video state."""
from pathlib import Path
import difflib,hashlib,json,os,subprocess,sys
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-load841'
B=Path('/home/paul/xbox-windows-native/boot720842-source001')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(A/'source002.json');assert read(A/'closed001.json')['state']=='CLOSED'
r={'physical_access':False,'space':require_space(B,22),'parents':{},'changes':{},'trees':{},'cache_sites':old['cache_sites']}
for label,tree in old['trees'].items():
 p=Path('/home/paul/xbox-windows-native/boot720841-source002')/label
 assert subprocess.check_output(['git','-C',str(p),'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',str(p),'diff','--name-only'])
 dst=B/label;dst.mkdir(parents=True);subprocess.run(['git','-C',str(p),'checkout-index','--all','--prefix='+str(dst)+'/'],check=True)
 r['parents'][label]={'tree':tree,'path':str(p),'source_only':True}
def change(label,path,new):
 p=B/label/path;old=p.read_text(encoding='latin1');assert old!=new
 h=sha(p);p.write_text(new,encoding='latin1');r['changes'][label+'/'+path]={'before':h,'after':sha(p)}
 with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(old.splitlines(True),new.splitlines(True),'a/'+path,'b/'+path))
for label,path in [('cromwell','boot/BootResetAction.c'),('reactos','boot/freeldr/freeldr/freeldr.c'),('reactos','boot/freeldr/freeldr/ntldr/winldr.c')]:
 p=B/label/path;t=p.read_text();change(label,path,t.replace('Boot841','Boot842').replace('Isolated841','Isolated842'))
p=B/'cromwell/drivers/pci/pci.c';t=p.read_text();a='#ifndef XWN_RETAIN_720_835\n\t// Bus 0, Device 1e, Function 0 = nForce AGP Host to PCI Bridge';assert t.count(a)==1
t=t.replace(a,'/* Windows bridge setup is independent of retained GPU timings. */\n\t// Bus 0, Device 1e, Function 0 = nForce AGP Host to PCI Bridge')
a='\t// Bus 1, Device 0, Function 0 = NV2A GeForce3 Integrated GPU';assert t.count(a)==1
t=t.replace(a,'#ifndef XWN_RETAIN_720_835\n'+a).replace('Retained GPU and AGP bridge configuration.','Retained GPU configuration; bridge initialized above.')
change('cromwell','drivers/pci/pci.c',t)
p=B/'cromwell/boot/BootResetAction.c';t=p.read_text();a='\tBootPciPeripheralInitialization();';assert t.count(a)==1
t=t.replace(a,a+'''
#ifdef XWN_RETAIN_720_835
    /* Defined bridge windows must match the ordinary Windows boot contract.
     * No GPU BAR, encoder, CRTC timing or AGP reset writes are enabled. */
    if (PciReadDword(0,30,0,0x20)!=0xfdf0fd00 ||
        PciReadDword(0,30,0,0x24)!=0xf7f0f000 ||
        (PciReadDword(0,30,0,0x18)&0x00ffffff)!=0x00010100 ||
        (PciReadDword(0,30,0,0x3c)&0xffff)!=7) {
        printk("XWN842: bridge setup readback failed; Windows not launched\\n");
        __asm__ __volatile__("cli");for(;;)__asm__ __volatile__("hlt");
    }
#endif
''');change('cromwell','boot/BootResetAction.c',t)
fd='drivers/filesystems/vfatfs/'
for p in (B/'fatx'/fd).iterdir():
 if p.is_file() and p.suffix in ['.c','.h','.txt']:
  t=p.read_text(encoding='latin1')
  if '841' in t:change('fatx',fd+p.name,t.replace('841','842'))
for prefix in ['cache','load']:
 for ext in ['c','h']:
  p=B/'fatx'/fd/(prefix+'841.'+ext)
  if p.exists():p.rename(B/'fatx'/fd/(prefix+'842.'+ext))
for label in old['trees']:
 dst=B/label;subprocess.run(['git','init','-q',str(dst)],check=True);subprocess.run(['git','-C',str(dst),'config','core.autocrlf','false'],check=True);subprocess.run(['git','-C',str(dst),'add','-f','.'],check=True);r['trees'][label]=subprocess.check_output(['git','-C',str(dst),'write-tree'],text=True).strip()
r['retention_unchanged_sha256']=sha(B/'cromwell/boot/retain835.c');r['loader_fat_unchanged_sha256']=sha(B/'reactos/boot/freeldr/freeldr/lib/fs/fat.c')
r['scope']='Re-enable existing AGP bridge PCI initialization in retained720p path, verify defined windows/bus/IRQ. GPU PCI setup and AGP reset remain skipped; encoder/timing code unchanged. Rename diagnostic namespace only.'
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n')
for n in ['main.c','Makefile','layout.c','layout.h','plan.c','plan.h','page.c','page.h','bridge.S','fixture.S','link.ld','plan_test.py','retain835.c']:
 data=(A/n).read_bytes()
 if n in ['main.c','Makefile']:data=data.replace(b'841',b'842').replace(b'xwn-fixed720-839',b'xwn-fixed720-842')
 (K/n).write_bytes(data)
for n in ['cache842.c','cache842.h','load842.c']:(K/n).write_bytes((B/'fatx'/fd/n).read_bytes())
for n in ['build-chain002.py','build-driver003.py','qualify-chain002.py','qualify-driver002.py','qualify-load003.py','review-driver002.py','host007.py','cpu006.py','build003.py','physical003.py']:
 t=(A/n).read_text().replace('boot720-load841','boot720-bridge842').replace('841','842').replace('boot720842-source002','boot720842-source001').replace("K/'source002.json'","K/'source001.json'")
 if n=='physical003.py':t=t.replace("['load-host003',","['bridge001','load-host003',").replace('display-load observation842; existing FATX fixes','AGP bridge setup842; retained720p; display-load observation')
 (K/n).write_text(t)
base=read(A/'baseline001.json');base['scope']='Immutable installed package, clean SYSTEM restoration before842; no failed runtime parent.'
base['projected_console_reserve']['additional_owned_budget']+=16*1024**2;base['projected_console_reserve']['projected_remaining']-=16*1024**2
(K/'baseline001.json').write_text(json.dumps(base,indent=2)+'\n');(K/'.gitattributes').write_bytes(b'* -text\n')
print('842 fresh source: bridge initialization restored, GPU state retained')
