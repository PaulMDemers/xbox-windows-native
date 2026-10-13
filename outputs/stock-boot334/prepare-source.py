"""Private stock-E launcher sources from exact reviewed HD parents; no deployment."""
import difflib,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
B=Path('/home/paul/xbox-windows-native/build/stock-boot334-build001')
assert not B.exists();B.mkdir()
parents={'reactos':('/home/paul/xbox-windows-native/build/hd-reservation300-build001/source','32705ddc77b3d3370eea8bdf62806b3dec9d2332'),
         'cromwell':('/home/paul/xbox-windows-native/build/hd-interlace316-build001/source','18ae8ef9452f81d953d287beff6939235c35cca1')}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(physical_access=False,guest_launch=False,parents={},changes={})
for label,(path,tree) in parents.items():
    assert subprocess.check_output(['git','-C',path,'write-tree'],text=True).strip()==tree
    assert not subprocess.check_output(['git','-C',path,'diff','--name-only'])
    root=B/label;root.mkdir();subprocess.run(['git','-C',path,'checkout-index','--all','--prefix='+str(root)+'/'],check=True)
    r['parents'][label]=dict(path=path,tree=tree)
def change(label,name,transform):
    p=B/label/name;before=p.read_text();old=sha(p);after=transform(before);assert before!=after
    p.write_text(after);r['changes'][label+'/'+name]=dict(before=old,after=sha(p))
    with (K/(label+'.patch')).open('a') as f:f.writelines(difflib.unified_diff(before.splitlines(True),after.splitlines(True),'a/'+name,'b/'+name))
def cmake(s):
    assert s.count('if(XBOX_NATIVE_FATX_F_BOOT)')==1
    return s+'''

option(XBOX_NATIVE_FATX_E_BOOT "Load isolated E XWNEBoot launcher and native E Windows root" OFF)
if(XBOX_NATIVE_FATX_E_BOOT)
    if(NOT SARCH STREQUAL "xbox" OR NOT XBOX_NATIVE_IO_PREFLIGHT OR
       XBOX_NATIVE_FATX_F_BOOT OR XBOX_NATIVE_EXTENDED_NT5_BOOT OR
       NOT XBOX_NATIVE_NT5_HANDOFF OR NOT XBOX_NATIVE_NT5_ENTER OR
       NOT XBOX_NATIVE_NT5_AUTORUN OR XBOX_NATIVE_FATX_IO_PREFLIGHT OR
       XBOX_NATIVE_FATX_NT5_PREFLIGHT)
        message(FATAL_ERROR "FATX E boot requires ordinary Xbox partition-1 native autorun without F boot")
    endif()
    target_compile_definitions(freeldr_pe PRIVATE XBOX_NATIVE_FATX_E_BOOT=1)
    target_compile_definitions(freeldr_common PRIVATE XBOX_NATIVE_FATX_E_BOOT=1)
endif()
'''
change('reactos','boot/freeldr/freeldr/pcat.cmake',cmake)
def loader(s):
    anchor='#elif defined(XBOX_NATIVE_FATX_IO_PREFLIGHT) || defined(XBOX_NATIVE_FATX_NT5_PREFLIGHT)'
    assert s.count(anchor)==1
    return s.replace(anchor,r'''#elif defined(XBOX_NATIVE_FATX_E_BOOT)
    /* Independent launcher and Windows root both live on stock partition 1. */
    if (strcmp(FrLdrBootPath, "multi(0)disk(0)rdisk(0)partition(1)") != 0 ||
        !NT_SUCCESS(RtlStringCbCatA(FrLdrBootPath, sizeof(FrLdrBootPath),
                                   "\\Applications\\XWNEBoot")))
        XwnStop("XWNFAIL: unexpected FATX E-boot launcher device");
'''+anchor)
change('reactos','boot/freeldr/freeldr/freeldr.c',loader)
def fs(s):
    assert s.count('#ifdef XBOX_NATIVE_FATX_F_BOOT')==2
    return s.replace('#ifdef XBOX_NATIVE_FATX_F_BOOT','#if defined(XBOX_NATIVE_FATX_F_BOOT) || defined(XBOX_NATIVE_FATX_E_BOOT)')
change('reactos','boot/freeldr/freeldr/lib/fs/fs.c',fs)
def crom(s):
    assert s.count('XWNFBoot')==2
    return s.replace('XWNFBoot','XWNEBoot')
change('cromwell','boot/BootResetAction.c',crom)
r['trees']={}
for label in parents:
    root=B/label;subprocess.run(['git','init','-q',str(root)],check=True)
    subprocess.run(['git','-C',str(root),'add','-f','.'],check=True)
    r['trees'][label]=subprocess.check_output(['git','-C',str(root),'write-tree'],text=True).strip()
r['scope']='Only isolated launcher path, mutually exclusive E profile, retained backing-device reference behavior. Existing bootmgr partition1 default selected by disabling EXTENDED_NT5_BOOT. No driver changes.'
(K/'source-review001.json').write_text(json.dumps(r,indent=2)+'\n');print('Fresh stock-E source prepared')
