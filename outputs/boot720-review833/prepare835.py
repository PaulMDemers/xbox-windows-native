"""Fresh source-only boot835: retain established720p, retail64, stock-E Windows."""
import difflib,hashlib,json,os,subprocess,sys
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=W/'outputs/boot720-native835';B=Path('/home/paul/xbox-windows-native/boot720835-source001')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held' and not B.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
K.mkdir(exist_ok=True);r={'physical_access':False,'space':require_space(B,21.5),'parents':{},'changes':{}}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parents={'cromwell':('/home/paul/xbox-windows-native/launcher677-validation002/default720/source','70c0a6c5aff82537f489e7d18410d5980fa797a7'), 'reactos':('/home/paul/xbox-windows-native/build/stock-boot334-build001/reactos','b2bb44a126630712c01af6bc331d5d7d9e4f07b0')}
for label,(path,tree) in parents.items():
 assert subprocess.check_output(['git','-C',path,'write-tree'],text=True).strip()==tree
 assert not subprocess.check_output(['git','-C',path,'diff','--name-only'])
 root=B/label;root.mkdir(parents=True);subprocess.run(['git','-C',path,'checkout-index','--all','--prefix='+str(root)+'/'],check=True)
 r['parents'][label]={'tree':tree,'path':path,'source_only':True}
def change(label,name,fn):
 p=B/label/name;before=p.read_text();old=sha(p);after=fn(before);assert after!=before
 p.write_text(after);r['changes'][label+'/'+name]={'before':old,'after':sha(p)}
 with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(before.splitlines(True),after.splitlines(True),'a/'+name,'b/'+name))
def replace(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def startup(s):
 s=replace(s,'extern void BootResetAction ( void ) {','''extern void XwnRetain720Entry835(void);
extern void XwnRetain720Mode835(CURRENT_VIDEO_MODE_DETAILS *);
extern void BootResetAction ( void ) {
#ifdef XWN_RETAIN_720_835
    XwnRetain720Entry835();
#endif''')
 s=replace(s,'\tBootAGPBUSInitialization();','#ifndef XWN_RETAIN_720_835\n\tBootAGPBUSInitialization();\n#endif')
 s=replace(s,'\tBootDetectMemorySize();','#ifdef XWN_RETAIN_720_835\n\txbox_ram=64; /* Verified by kernel frontend and exact multiboot contract. */\n#else\n\tBootDetectMemorySize();\n#endif')
 s=replace(s,'\tBootVgaInitializationKernelNG((CURRENT_VIDEO_MODE_DETAILS *)&vmode);','''#ifdef XWN_RETAIN_720_835
    XwnRetain720Mode835((CURRENT_VIDEO_MODE_DETAILS *)&vmode);
#else
    BootVgaInitializationKernelNG((CURRENT_VIDEO_MODE_DETAILS *)&vmode);
#endif''')
 assert s.count('XWNEBoot')==2;s=s.replace('XWNEBoot','XWN16Boot835')
 return s
change('cromwell','boot/BootResetAction.c',startup)
def pci(s):
 start='\t// Bus 0, Device 1e, Function 0 = nForce AGP Host to PCI Bridge'
 end='\t// Enable Serial COM1 by default if not already enabled'
 s=replace(s,start,'#ifndef XWN_RETAIN_720_835\n'+start)
 return replace(s,end,'#endif /* Retained GPU and AGP bridge configuration. */\n'+end)
change('cromwell','drivers/pci/pci.c',pci)
def bootmake(s):return replace(s,'O_TARGET :=','O_TARGET := retain835.o')
change('cromwell','boot/Makefile',bootmake)
change('cromwell','Makefile',lambda s:replace(s,'OBJECTS-CROM += $(TOPDIR)/obj/BootResetAction.o','OBJECTS-CROM += $(TOPDIR)/obj/BootResetAction.o\nOBJECTS-CROM += $(TOPDIR)/obj/retain835.o'))
(B/'cromwell/boot/retain835.c').write_bytes((K/'retain835.c').read_bytes())
r['new_source']={'cromwell/boot/retain835.c':sha(K/'retain835.c')}
def mem(s):
 a='    PCI_TYPE1_CFG_BITS PciCfg1;\n    UCHAR ControlRegion[TEST_SIZE];'
 s=replace(s,a,'''#ifdef XWN_RETAIN_720_835
    INT count, i;
    memory_map_t *map = XboxGetMultibootMemoryMap(&count);
    if (!map || count != 2)
        FrLdrBugCheckWithMessage(0, __FILE__, __LINE__, "retained720 retail64 map absent");
    for (i=0;i<count;i++)
        if (!XwnHdMapEntryValid(i,map[i].base_addr_low,map[i].base_addr_high,
                map[i].length_low,map[i].length_high,map[i].type))
            FrLdrBugCheckWithMessage(0, __FILE__, __LINE__, "retained720 retail64 map invalid");
    InstalledMemoryMb = 64;
#else
'''+a)
 return replace(s,'    AvailableMemoryMb = InstalledMemoryMb;','#endif\n    AvailableMemoryMb = InstalledMemoryMb;')
change('reactos','boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c',mem)
change('reactos','boot/freeldr/freeldr/freeldr.c',lambda s:replace(s,'\\\\Applications\\\\XWNEBoot','\\\\Applications\\\\XWN16Boot835'))
def cmake(s):
 return s+'''
option(XWN_RETAIN_720_835 "Retain kernel-established Xbox1.6 retail64 720p" OFF)
if(XWN_RETAIN_720_835)
    if(NOT XBOX_NATIVE_FATX_E_BOOT OR NOT XBOX_NT5_HD_RESERVATION)
        message(FATAL_ERROR "retained720 requires stock E and exact HD reservation")
    endif()
    target_compile_definitions(freeldr_pe PRIVATE XWN_RETAIN_720_835=1)
    target_compile_definitions(freeldr_common PRIVATE XWN_RETAIN_720_835=1)
endif()
'''
change('reactos','boot/freeldr/freeldr/pcat.cmake',cmake)
r['trees']={}
for label in parents:
 root=B/label;subprocess.run(['git','init','-q',str(root)],check=True);subprocess.run(['git','-C',str(root),'add','-f','.'],check=True)
 r['trees'][label]=subprocess.check_output(['git','-C',str(root),'write-tree'],text=True).strip()
(K/'source001.json').write_text(json.dumps(r,indent=2)+'\n');print('Fresh boot835 sources prepared')
