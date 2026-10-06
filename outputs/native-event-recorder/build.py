"""Build an isolated opt-in event recorder, restoring borrowed xemu sources."""
import difflib, hashlib, json, os, shutil, subprocess
from pathlib import Path
assert os.environ.get('XWN_BUILD_LEASE') == 'held'
k = Path(__file__).resolve().parent
ws = k.parents[1]
s = Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
revision = 'e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
git = ['git','-c','safe.directory='+str(s)]
assert subprocess.check_output(git+['rev-parse','HEAD'],cwd=s,text=True).strip() == revision
base = 0x823df000
layout = read(k.parent/'native-windows-nt5-kernel/process-layouts.json')
symbols = read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols']
sparse = read(k.parent/'shutdown-popup-workload/site-review-sparse.json')
lifecycle = read(k.parent/'shutdown-popup-workload/site-review-lifecycle.json')
sites = sparse['sites'] + [v for v in lifecycle['sites'] if v['name'] in [
    '_PspExitProcess@8','NtTerminateProcess_AfterReference','NtResumeThread_BeforeResume']]
caller = read(k.parent/'shutdown-popup-workload/caller-review.json')
sites += [dict(name='Win32k_Terminate_call', module='win32k.sys', address=0xa007e409,
               bytes='ff15084916a0', argc=2, kind='terminate_call')]
assert any(v['address']=='0xa007e409' and v['bytes']=='ff15084916a0' for v in caller['instructions'])
kinds = {'NtTerminateProcess_AfterReference':2, 'NtResumeThread_BeforeResume':3,
         '_PspExitProcess@8':4, '_ExRaiseHardError@24':5, '_ExpRaiseHardError@24':5,
         '_NtShutdownSystem@4':6}
for i, site in enumerate(sites):
    site.update(index=i, pc=base+site['rva'] if site['module']=='ntoskrnl.exe' else site['address'],
                capture_kind=1 if site['name'] in ['PnP_Create_call','PnP_Create_return','PnP_Wait_return'] else kinds.get(site['name'],0))
header = ['/* Generated from reviewed owned-binary sites; see sites.json. */',
          'typedef struct XwnSite { uint32_t pc; uint8_t size, kind, bytes[8]; } XwnSite;',
          'static const XwnSite xwn_sites[] = {']
for site in sites:
    b=bytes.fromhex(site['bytes']); assert 0 < len(b) <= 8
    header.append('    {0x%x, %d, %d, {%s}},' % (site['pc'],len(b),site['capture_kind'],','.join(hex(x) for x in b)))
header += ['};', 'static int xwn_site_for_pc(uint64_t pc)', '{',
           '    static int enabled = -1;',
           '    if (enabled < 0) { const char *p = getenv("XWN_NATIVE_EVENT_LOG"); enabled = p && *p; }',
           '    if (!enabled) { return -1; }',
           '    for (unsigned i = 0; i < ARRAY_SIZE(xwn_sites); ++i) { if (pc == xwn_sites[i].pc) { return i; } }',
           '    return -1;', '}']
fields=layout['_EPROCESS']['fields']
constants=dict(PROCESS_CR3=layout['_KPROCESS']['fields']['DirectoryTableBase']['offset'],
               PROCESS_PEB=fields['Peb']['offset'], PROCESS_PID=fields['UniqueProcessId']['offset'],
               PROCESS_IMAGE=fields['ImageFileName']['offset'], THREAD_OWNER=sparse['thread_owner_offset'],
               TICK=base+symbols['_KeTickCount']['rva'], TOKEN=sparse['token_global'])
header += ['#define XWN_%s 0x%x' % (name,value) for name,value in constants.items()]
(k/'sites.json').write_text(json.dumps(dict(kernel_base=hex(base), sites=sites, constants=constants,
    binaries=sparse['binaries'] | caller['binaries'], kernel_sha256=sparse['kernel_sha256'],
    limits='Fixed addresses for the pinned fixture; exact bytes checked per hit. Nonresident reads explicitly invalid. No guest writes.'),indent=2)+'\n')
(k/'xwn-sites.h').write_text('\n'.join(header)+'\n')
paths=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','target/i386/helper.h',
       'target/i386/tcg/translate.c','target/i386/tcg/misc_helper.c',
       'target/i386/tcg/xwn-sites.h','target/i386/tcg/xwn-recorder.c.inc']
original={p:(s/p).read_bytes() if (s/p).exists() else None for p in paths}
nvnet=sha(s/'hw/xbox/mcpx/nvnet/nvnet.c')
image=read(k.parent/'native-windows-physical-f/xemu-resource-model-build.json')['toolchain']
report=dict(scope=__doc__,source_revision=revision,toolchain=image,nvnet_sha256=nvnet,
            source_inputs={p:hashlib.sha256(b).hexdigest() if b else None for p,b in original.items()},
            recorder_source_sha256=sha(k/'recorder.c.inc'),sites_header_sha256=sha(k/'xwn-sites.h'))
try:
    subprocess.run(git+['apply',str(k.parent/'native-windows-physical-f/xemu-nv2a-resource-model.patch')],cwd=s,check=True)
    shutil.copyfile(k/'xwn-sites.h',s/'target/i386/tcg/xwn-sites.h')
    shutil.copyfile(k/'recorder.c.inc',s/'target/i386/tcg/xwn-recorder.c.inc')
    p=s/'target/i386/helper.h'
    p.write_text(p.read_text()+'\nDEF_HELPER_FLAGS_2(xwn_event, TCG_CALL_NO_WG, void, env, i32)\n')
    p=s/'target/i386/tcg/misc_helper.c'
    p.write_text(p.read_text()+'\n#include "xwn-recorder.c.inc"\n')
    p=s/'target/i386/tcg/translate.c';t=p.read_text()
    t=t.replace('#include "decode-new.h"','#include "decode-new.h"\n#include "xwn-sites.h"')
    needle='    target_ulong orig_pc_save = dc->pc_save;'
    assert t.count(needle)==1
    t=t.replace(needle,needle+'\n    int xwn_site = xwn_site_for_pc(dc->base.pc_next);\n    if (xwn_site >= 0) { gen_helper_xwn_event(tcg_env, tcg_constant_i32(xwn_site)); }')
    p.write_text(t)
    patch=[]
    for rel,old in original.items():
        new=(s/rel).read_bytes()
        patch.extend(difflib.unified_diff((old or b'').decode().splitlines(True),new.decode().splitlines(True),
                     fromfile='a/'+rel if old is not None else '/dev/null',tofile='b/'+rel))
    (k/'recorder.patch').write_text(''.join(patch))
    subprocess.run(['podman','run','--rm','--pull=never','-v',str(s)+':/src','-w','/src/build',image,
                    'ninja','-j4','qemu-system-i386w.exe'],check=True)
    target=k/'artifacts/xemu-events.exe';target.parent.mkdir(exist_ok=True)
    shutil.copyfile(s/'build/qemu-system-i386w.exe',target)
    report.update(binary_sha256=sha(target),patch_sha256=sha(k/'recorder.patch'),built=True)
finally:
    for rel,old in original.items():
        p=s/rel
        if old is None:
            # Only the two explicitly named files created above may be removed.
            assert rel in ['target/i386/tcg/xwn-sites.h','target/i386/tcg/xwn-recorder.c.inc']
            if p.exists():p.unlink()
        else:p.write_bytes(old)
    assert all((s/p).read_bytes()==b if b is not None else not (s/p).exists() for p,b in original.items())
    assert sha(s/'hw/xbox/mcpx/nvnet/nvnet.c')==nvnet
    report['borrowed_sources_restored']=True
    (k/'build.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
