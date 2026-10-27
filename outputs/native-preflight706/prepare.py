"""Prepare kernel-only706 from retained701 and705 sources; no deployment."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1]
assert not (K/'main.c').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=W/'outputs/native-gpu701';B=W/'outputs/native-bridge705'
a=json.loads((A/'build001.json').read_text());b=json.loads((B/'build002.json').read_text())
for n in ['main.c','layout.c','layout.h']:assert sha(A/n)==a['files'][n]['sha256']
for n in ['plan.c','plan.h']:assert sha(B/n)==b['sources'][n]
for n in ['layout.c','layout.h']:(K/n).write_bytes((A/n).read_bytes())
for n in ['plan.c','plan.h']:(K/n).write_bytes((B/n).read_bytes())
s=(A/'main.c').read_text().replace('#include "page.h"\n','')
s=s.replace('xwn-native701-','xwn-preflight706-').replace('xwn-native-checkpoint701','xwn-kernel-preflight706')
start=s.index('extern const unsigned char stub701_');end=s.index('\nint main(void)',start)
s=s[:start]+(K/'kernel_probe.inc').read_text()+s[end:]
s=s.replace('int probe_ok=allocation_probe701(layout.address,layout.bytes);',
 '''int state_saved=context706();
    if(state_saved){HalReturnToFirmware(HalRebootRoutine);return 8;}
    int probe_ok=allocation_probe706(layout.address,layout.bytes,layout.allocation);''')
s=s.replace('probe_ok?0x2080ff:0xff0000','probe_ok?0x00ff00:0xff0000')
start=s.index('    if(probe_ok){\n     Sleep(5000);');end=s.index('    Sleep(10000);',start)
s=s[:start]+s[end:]
s=s.replace('release701();','')
s=s.replace('memory.TotalPhysicalPages==16384;', 'memory.TotalPhysicalPages==16384 && XboxHardwareInfo.GpuRevision==0xd3 && XboxHardwareInfo.McpRevision==0xd5;')
s=s.replace(' * Owned-page native checkpoint after kernel admission. Deliberate manual-reset hold.',
 ' * Kernel-only 32KiB allocation/context preflight. Marker bytes are NEVER executed.')
s=s.replace(' * Kernel display calls are not bounded by this application. Watched test only.',
 ' * Kernel API calls are not bounded by this application. Watched test; automatic return.')
(K/'main.c').write_text(s)
(K/'Makefile').write_text('XBE_TITLE = XWN\\ Kernel\\ Preflight\\ 706\nSRCS = $(CURDIR)/main.c $(CURDIR)/layout.c $(CURDIR)/plan.c\nNXDK_DIR ?= /c/nxdk\nCFLAGS += -std=gnu11 -Wall -Wextra -Werror\ninclude $(NXDK_DIR)/Makefile\n')
(K/'.gitattributes').write_text('* -text\n* whitespace=cr-at-eol\n')
(K/'sources001.json').write_text(json.dumps({'retained_inputs':{str(p.relative_to(W)):sha(p) for p in [A/'main.c',A/'layout.c',A/'layout.h',B/'plan.c',B/'plan.h']},'physical_access':False},indent=2)+'\n')
