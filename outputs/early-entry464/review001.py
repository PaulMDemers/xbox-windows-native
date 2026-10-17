"""Pin the real pre-stack boot boundary and review candidate observation channels."""
import hashlib
import importlib.util
import json
import struct
import subprocess
from pathlib import Path

K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('E:/xwn464/source001')
assert not P.exists() and not (K/'source-review001.json').exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
s=importlib.util.spec_from_file_location('review414',W/'outputs/cromwell-devices414/review.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
elf=Path('E:/xwn374/build001/image-crom.elf').read_bytes()
payload=Path('E:/xwn374/build001/image-crom.bin').read_bytes()
xbe=Path('E:/xwn374/build001/default.xbe').read_bytes()
prior=json.loads((W/'outputs/cromwell-devices414/source-review.json').read_text(encoding='utf-8'))
assert sha(elf)==prior['elf_sha256'] and sha(payload)==prior['payload_sha256']
assert sha(xbe)==prior['original_xbe_sha256'] and xbe[0x3000:0x3000+len(payload)]==payload
sections=m.verify_sections(elf,payload)
assert payload[:5]==bytes.fromhex('e98b000000')
assert payload[0xf0:0xf5]==bytes.fromhex('bc00008002')
assert payload[0x90:0x99]==bytes.fromhex('fab8330001600f22c0')
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n','/mnt/e/xwn374/build001/image-crom.elf']).decode()
symbols={v[2]:int(v[0],16) for line in nm.splitlines() if len(v:=line.split())==3}
assert symbols['start_linux']==0x2600090 and symbols['reload_cs']==0x26000e0
assert symbols['BootResetAction']==0x2600420
source={};P.mkdir(parents=True)
root='/home/paul/xbox-windows-native/build/resolution-e374-build001/source/'
for name in ['boot_xbe/xbeboot.S','boot/BootStartup.S','boot/BootResetAction.c','include/memory_layout.h','drivers/pci/i2cio.c','drivers/pci/i2c.h','lib/misc/LED.c']:
    b=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+name])
    if name in prior['source_files']:assert sha(b)==prior['source_files'][name]
    if name=='boot_xbe/xbeboot.S':assert sha(b)=='b8ddf72f41a682d3868f1b801492b31005611c6868aa5927f54e5ce14bb94a2c'
    p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    source[name]=dict(path=str(p),sha256=sha(b),bytes=len(b))
i2c=(P/'drivers/pci/i2cio.c').read_text()
write=i2c.split('int WriteToSMBus(',1)[1].split('int ReadfromSMBus(',1)[0]
assert 'while(IoInputWord(I2C_IO_BASE+0)&0x0800) ;' in write
assert 'while( (b&0x36)==0 )' in write
led=i2c.split('int I2cSetFrontpanelLed(',1)[1].split('int I2cResetFrontpanelLed(',1)[0]
assert 'I2CTransmitWord( 0x10, 0x800 | b)' in led and 'I2CTransmitWord( 0x10, 0x701)' in led
assert 'return ERR_SUCCESS;' in led
wrapper=(P/'boot_xbe/xbeboot.S').read_text()
transition=wrapper.split('blentry:',1)[1].split('newflash:',1)[0]
assert 'mov\tcr0, eax' in transition and 'KERNEL_RAM_ADDRESS' in transition
assert 'esp' not in transition.lower()
startup=(P/'boot/BootStartup.S').read_text()
before_stack=startup.split('start_linux:',1)[1].split('movl $STACK_TOP, %esp',1)[0]
assert '\tcall' not in before_stack and '\tpush' not in before_stack
reset=(P/'boot/BootResetAction.c').read_text()
assert reset.index('BootPciPeripheralInitialization();')<reset.index('BootVgaInitializationKernelNG(')<reset.index('setLED("rrrr");')
disasm=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-d','-Mintel','/mnt/e/xwn374/build001/image-crom.elf','--start-address=0x2600000','--stop-address=0x2600420'])
(P/'entry-disassembly.txt').write_bytes(disasm)
(P/'symbols.txt').write_text(nm,encoding='utf-8')
r=dict(passed=True,scope='Exact source/binary boundary review only; no installed marker or runtime result',
       sections=sections,elf_sha256=sha(elf),payload_sha256=sha(payload),xbe_sha256=sha(xbe),source=source,
       entry=0x2600000,start_linux=symbols['start_linux'],stack_install_instruction=0x26000f0,
       stack_top=0x2800000,boot_reset=symbols['BootResetAction'],
       wrapper_does_not_rebase_esp=True,prestack_ordinary_call_not_authorized=True,
       original_smbus_busy_and_completion_waits_unbounded=True,
       original_led_helper_ignores_transaction_failure=True,
       stock_red_led_is_after_pci_video_init=True,original_debug_led_loop_is_terminal=True,
       kernel_file_calls_after_paging_allowed=False,physical_access=False,shared_source_changed=False,
       original_boot_failure_cause_established=False,actual_marker_implemented=False,
       private_review_files={str(p.relative_to(P)):sha(p.read_bytes()) for p in P.rglob('*') if p.is_file()})
(K/'source-review001.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k] for k in ['passed','entry','stack_install_instruction','original_smbus_busy_and_completion_waits_unbounded','actual_marker_implemented']}))
