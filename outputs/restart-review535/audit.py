"""Read retained exact binaries; execute HAL dispatch only with no device access.

This is an instruction-level host test, not a hardware restart or Windows test.
Proprietary kernel bytes are read locally and never emitted into the report.
"""
from pathlib import Path
import datetime, hashlib, json, shutil, struct, subprocess, sys

K = Path(__file__).resolve().parent
W = K.parents[1]
sys.path.insert(0, str(W / 'work/python-packages'))
import capstone
import pefile
import unicorn
from unicorn import x86_const as x86

sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
out = K / 'audit001.json'
assert not out.exists()
assert shutil.disk_usage('C:/').free - 1024**2 >= 20 * 1024**3
accepted = read(W / 'outputs/demo-integration399/accepted-state.json')
# These exact hashes are also the protected installed policy pins checked in534.
hal_path = Path('E:/xwn415/demo/Applications/XWNEBoot/loader/halxboxnt5.dll')
nt_path = Path('E:/xwn415/demo/winnt/system32/ntoskrnl.exe')
hal = hal_path.read_bytes()
nt = nt_path.read_bytes()
assert sha(hal) == 'a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648'
assert sha(nt) == '84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
p = pefile.PE(data=hal)
base = p.OPTIONAL_HEADER.ImageBase
entry = base + next(e.address for e in p.DIRECTORY_ENTRY_EXPORT.symbols
                    if e.name == b'HalReturnToFirmware')
assert entry == 0x197b0
# Exact binary symbols were independently inspected with GNU objdump. Each host
# run stops BEFORE this helper, so no port access or restart helper executes.
power_helper = 0x196c0
invalid_first_call = 0x88da8
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
image = p.get_memory_mapped_image()
dispatch = list(md.disasm(image[entry-base:entry-base+0x4c], entry))
assert dispatch[-1].address + dispatch[-1].size == entry + 0x4c
assert not any(i.mnemonic in ('in', 'out', 'cli', 'sti', 'hlt') for i in dispatch)
cases = []
for action, expected in [(0,0x80), (1,0x80), (2,0x40), (3,1),
                         (4,None), (0x7fffffff,None), (0xffffffff,None)]:
    u = unicorn.Uc(unicorn.UC_ARCH_X86, unicorn.UC_MODE_32)
    u.mem_map(base, (len(image)+4095)&~4095)
    u.mem_write(base, image)
    u.mem_map(0x400000, 0x10000)
    sp = 0x408000
    u.mem_write(sp, struct.pack('<II', 0xdeadbeef, action))
    u.reg_write(x86.UC_X86_REG_ESP, sp)
    observed = {}
    executed = []
    def hook(uc, address, size, data):
        if address in (power_helper, invalid_first_call):
            observed.update(boundary=address, command=(uc.reg_read(x86.UC_X86_REG_EAX)&255)
                            if address == power_helper else None)
            uc.emu_stop()
            return
        assert entry <= address < entry+0x4c, hex(address)
        executed.append(address)
    u.hook_add(unicorn.UC_HOOK_CODE, hook)
    u.emu_start(entry, 0xdeadbeef, timeout=1_000_000, count=100)
    assert observed, action
    assert observed['command'] == expected, (action, observed)
    assert observed['boundary'] == (power_helper if expected is not None else invalid_first_call)
    cases.append(dict(action=action,command=observed['command'],
                      stopped_before_helper=True,executed_instructions=len(executed)))

# Static kernel IAT-reference inventory. This deliberately does not label UI
# paths, decode from arbitrary preceding bytes or claim runtime branch coverage.
n = pefile.PE(data=nt)
iat = next(i.address for m in n.DIRECTORY_ENTRY_IMPORT for i in m.imports
           if i.name == b'HalReturnToFirmware')
references = []
for s in n.sections:
    if not s.Characteristics & 0x20000000:
        continue
    b = s.get_data()
    for j in range(len(b)-6):
        if b[j:j+6] == b'\xff\x15' + struct.pack('<I',iat):
            references.append(dict(rva=s.VirtualAddress+j,
                immediately_preceding_push3=b[max(0,j-2):j] == b'\x6a\x03'))

source_root = '/home/paul/xbox-windows-native/build/'
sources = {}
for rel in [
 'hd-reservation300-build001/source/hal/halx86/xbox/reboot.c',
 'hd-reservation300-build001/source/hal/halx86/xbox/halxbox.h',
 'resolution-e374-build001/source/boot_xbe/xbeboot.S',
 'resolution-e374-build001/source/boot/BootResetAction.c',
 'resolution-e374-build001/source/drivers/pci/i2cio.c']:
    path = source_root + rel
    data = subprocess.check_output(['wsl','-d','Ubuntu','-u','paul','--','cat',path],timeout=30)
    sources[path] = dict(sha256=sha(data),bytes=len(data))
    if rel.endswith('xbeboot.S'):
        assert sha(data) == read(W/'outputs/windows-pair532/preflight001.json')['wrapper_source_sha256']

before = read(W/'outputs/cold-pair534/before1.json')
row = before['files']['/E/Applications/XWNEBoot/default.xbe']
xbe = Path(row['path']).read_bytes()
assert sha(xbe) == row['sha256'] == '6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
# XBE mapping: original single section file11000-base10000, entry11100.
initial = []
for ins in md.disasm(xbe[0x1100:0x1500], 0x11100):
    initial.append(dict(address=ins.address,mnemonic=ins.mnemonic,operands=ins.op_str))
    if ins.mnemonic == 'cli':
        break
assert initial[-1]['mnemonic'] == 'cli'
first_copy = next(i for i,x in enumerate(initial) if x['mnemonic'].startswith('rep movsb'))
assert not any(x['mnemonic'] == 'cld' for x in initial[:first_copy])
calls = [x for x in initial if x['mnemonic']=='call']
assert len(calls)==5
assert not any(x['mnemonic'].startswith('j') and x['mnemonic']!='jmp' for x in initial)

r = dict(closed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    scope='Host instruction execution of exact HAL dispatcher; static original wrapper/source review',
    physical_access=False,physical_launches=0,remote_writes=[],new_binary_built=False,
    hal_sha256=sha(hal),ntoskrnl_sha256=sha(nt),ordinary_xbe_sha256=sha(xbe),
    tools=dict(unicorn=unicorn.__version__,capstone=capstone.__version__,pefile=pefile.__version__),
    dispatch_entry_va=entry,power_helper_va=power_helper,dispatch_cases=cases,
    device_io_executed=False,kernel_runtime_action_observed=False,
    kernel_static_direct_iat_references=references,
    kernel_static_reference_limit='Byte-pattern inventory only; no caller identity, complete xrefs or UI-to-firmware mapping claim',
    original_wrapper_prefix=initial,original_prefix_call_count=len(calls),
    original_prefix_conditional_branches=0,first_payload_copy_before_cld=True,
    source_pins=sources,
    source_provenance_limit='374 wrapper hash matches532 retained build;300 HAL source is a reference, not a claim that300 built the installed HAL',
    hardware_root_cause_known=False,functional_patch=False,source_sha256=sha(Path(__file__).read_bytes()))
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k] for k in ['closed','dispatch_cases','device_io_executed','original_prefix_call_count','first_payload_copy_before_cld']}))
