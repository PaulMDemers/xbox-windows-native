"""Freeze a private nxdk capture build; never edit the installed SDK."""
import argparse,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('attempt');p.add_argument('--emulator',action='store_true');a=p.parse_args()
assert a.attempt.startswith('build') and a.attempt[5:].isdigit()
sdk=Path('C:/nxdk'); dest=K/'artifacts'/a.attempt;dest.mkdir(parents=True,exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest()
git='C:/Program Files/Git/cmd/git.exe'
assert subprocess.check_output([git,'-C',str(sdk),'rev-parse','HEAD']).decode().strip()=='58427c078b4ccb0121f359b6b6c536b3b2914976'
assert subprocess.check_output([git,'-C',str(sdk/'lib/usb/libusbohci'),'rev-parse','HEAD']).decode().strip()=='6a0c5fefbcd9db53f4a27ee10df99f93d5bce745'
original=(sdk/'lib/usb/libusbohci/src_core/usb_core.c').read_text()
old='''            usbh_quit_utr(utr);
            free_utr(utr);'''
new='''            usbh_quit_utr(utr);
            /* Private capture guard: quit_xfer schedules removal at a later SOF.
             * Completion, not cancellation submission, transfers ownership. */
            uint32_t cancel_start = get_ticks();
            while (!utr->bIsTransferDone && get_ticks() - cancel_start < 100)
                delay_us(1000);
            if (!utr->bIsTransferDone) {
                extern void xid_guard_reboot(void) __attribute__((noreturn));
                xid_guard_reboot();
            }
            free_utr(utr);'''
assert original.count(old)==1
patched=original.replace(old,new)
(dest/'usb_core_guarded.c').write_text(patched)
ohci=(sdk/'lib/usb/libusbohci/src_core/ohci.c').read_text()
old_tail='''                while (td != NULL)
                {
                    utr = td->utr;'''
new_tail='''                while (td != NULL)
                {
                    /* The queue's dummy tail is not a submitted transfer. */
                    if ((uint32_t)virt_to_dma(td) == (ed_p->TailP & ~0xfu)) {
                        free_ohci_TD(td);
                        break;
                    }
                    utr = td->utr;'''
assert ohci.count(old_tail)==1
ohci=ohci.replace(old_tail,new_tail)
(dest/'ohci_guarded.c').write_text(ohci)
(dest/'main.c').write_bytes((K/'main.c').read_bytes())
(dest/'Makefile').write_text('XBE_TITLE = XWN XID Capture\nSRCS = $(CURDIR)/main.c $(CURDIR)/usb_core_guarded.c $(CURDIR)/ohci_guarded.c\nNXDK_DIR ?= /c/nxdk\nCFLAGS += -Wall -Wextra -Wno-unused-parameter'+(' -DXID_EMULATOR=1' if a.emulator else '')+'\nLDFLAGS += -map:link.map\n$(CURDIR)/main.obj: CFLAGS += -Werror\ninclude $(NXDK_DIR)/Makefile\n')
pins={str(v):sha(v.read_bytes()) for v in [K/'main.c',K/'prepare-build.py']}
for folder in ['lib/usb','lib/hal']:
 for v in (sdk/folder).rglob('*'):
  if v.is_file() and v.suffix in ['.c','.h','.obj']:pins[str(v)]=sha(v.read_bytes())
for v in (sdk/'lib').glob('*.lib'):pins[str(v)]=sha(v.read_bytes())
r=dict(attempt=a.attempt,emulator=a.emulator,physical_access=False,pins=pins,upstream_core_sha256=sha(original.encode()),guarded_core_sha256=sha(patched.encode()),guarded_ohci_sha256=sha(ohci.encode()),build_folder=str(dest),native_only=True)
(K/(a.attempt+'-inputs.json')).write_text(json.dumps(r,indent=2)+'\n')
print(dest)
