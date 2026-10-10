"""Privately pin actual launcher/loader artifacts and bounded handoff source.
Historical build-source relationships remain explicit; no full rebuild claim.
"""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'handoff-inventory.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
roots={
 'cromwell':Path('/home/paul/xbox-windows-native/build/cromwell-physical-f-001'),
 'loader-current':Path('/home/paul/xbox-windows-native/sources/reactos-extended'),
 'nt5-106':Path('/home/paul/xbox-windows-native/build/video-shared-framebuffer-001/source')}
names={
 'cromwell':['boot_xbe/xbeboot.S','boot/BootFromDevice.c','boot/BootResetAction.c','boot/LoadReactOS.c','drivers/pci/pci.c','drivers/video/BootVgaInitialization.c','drivers/video/VideoInitialization.c','include/boot.h','include/memory_layout.h'],
 'loader-current':['boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c','boot/freeldr/freeldr/arch/i386/xbox/xboxvideo.c','boot/freeldr/freeldr/ntldr/winldr.c','boot/freeldr/freeldr/ntldr/wlmemory.c'],
 'nt5-106':['drivers/base/bootvid/precomp.h','sdk/include/reactos/drivers/bootvid/display.h','drivers/base/bootvid/i386/xbox/bootvid.c','win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c']}
out=k/'artifacts/handoff002';out.mkdir(parents=True,exist_ok=False);pins={}
for group,files in names.items():
 for name in files:
  p=roots[group]/name;q=out/group/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());assert sha(q)==sha(p)
  pins[group+'/'+name]=dict(source=str(p),sha256=sha(q),bytes=q.stat().st_size)
fixture=read(k.parent/'video-gpu-state214/fixture-candidate001.json');binaries={}
for name,p in {
 'E/Applications/XWNFBoot/default.xbe':roots['cromwell']/'xbe/xromwell.xbe',
 'E/Applications/XWNFBoot/freeldr.sys':Path('/home/paul/xbox-windows-native/build/physical-f-loader/boot/freeldr/freeldr/freeldr.sys')}.items():
 assert sha(p)==fixture['files'][name];q=out/'binaries'/p.name;q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
 binaries[name]=dict(sha256=sha(q),original=str(p),private_copy=str(q.relative_to(k)),bytes=q.stat().st_size)
launcher=read(k.parent/'native-windows-physical-f/launcher.json');assert launcher['xbe_sha256']==binaries['E/Applications/XWNFBoot/default.xbe']['sha256']
lc=(out/'cromwell/boot/LoadReactOS.c').read_text();xm=(out/'loader-current/boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c').read_text()
assert 'BootStopUSB();' in lc and 'asm volatile ("cli\\n");' in lc and 'memset((void *)IDT_LOC' in lc
assert 'mmap->length_low = (xbox_ram * 1024 * 1024) - FB_SIZE;' in lc and 'mmap->type = 0;' in lc
assert 'case 0: // Video RAM' in xm and 'return LoaderFirmwarePermanent;' in xm
assert '#define FB_SIZE' in (out/'cromwell/include/memory_layout.h').read_text()
objdump='/usr/bin/objdump';binaries['launcher-disassembly']=dict(tool_sha256=sha(Path(objdump)),path='artifacts/handoff002/launcher-disassembly.txt')
p=roots['cromwell']/'obj/LoadReactOS.o';assert p.exists();q=out/'binaries/LoadReactOS.o';q.write_bytes(p.read_bytes());binaries['launcher-object']=dict(sha256=sha(q),original=str(p))
(out/'launcher-disassembly.txt').write_text(subprocess.check_output([objdump,'-dr',str(q)],text=True))
save=dict(passed=True,source_sha256=sha(Path(__file__)),files=pins,binaries=binaries,
 launcher_base=launcher['base'],launcher_patch_sha256=launcher['patch_sha256'],
 loader_source_relationship='Current original build-cache source; may include later edits. Pinned106 parallel source reviewed separately. Neither is asserted byte-identical to the original historical compiler input. Exact intended freeldr binary is separately verified.',
 cpu_handoff_found=True,gpu_release_record_found=False,gpu_instance_backing_proven=False,
 guest_launch=False,physical_access=False,gpu_register_access=False,
 limits='Bounded static source and actual intended artifacts; absence of a GPU release record in these paths is not proof of GPU idle. No PRAMIN physical alias/address,context grant or interrupt handling authority.')
dest.write_text(json.dumps(save,indent=2)+'\n');print('Pinned handoff:',len(pins),'source files; actual214 launcher/loader hashes match.')
