"""Close the refused observer attempt without qualifying the unexecuted jump."""
import datetime,hashlib,json,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'final-review.json';assert not out.exists()
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
pins=json.loads((K/'emu001/frozen.json').read_text());external=json.loads((K/'emu001/host-dependencies.json').read_text())
for p,h in pins.items():assert sha(W/p)==sha(Path('C:/xwn511/frozen001')/p)==h,p
for p,h in external.items():assert sha(Path(p))==h,p
t=json.loads((K/'emu001/trace.json').read_text());a=json.loads((K/'emu001/audit.json').read_text());p=json.loads((K/'emu001/protected.json').read_text())
assert not t['passed'] and t['error']=="ValueError('loaded entry')"
assert len(t['checkpoints'])==1 and t['checkpoints'][0]['registers']['EIP']==0x11100
assert len(t['reads'])==2 and not t.get('calls') and not t.get('trampoline')
reads={v['label']:v for v in t['reads']}
for v in t['reads']:assert sha(Path(v['private_file']))==v['sha256']
header=Path(reads['trampoline-loaded-header']['private_file']).read_bytes()
stub=Path(reads['trampoline-five-bytes']['private_file']).read_bytes()
x=Path('C:/xwn510/build001/default.xbe').read_bytes()
assert struct.unpack_from('<I',header,296)[0]==0x11100
assert struct.unpack_from('<I',x,296)[0]^0xa8fc57ab==0x11100
assert stub==x[0x1100:0x1105]==bytes.fromhex('e9fa390800')
diff=[dict(offset=i,on_disk=struct.unpack_from('<I',x,i)[0],loaded=struct.unpack_from('<I',header,i)[0]) for i in range(0,4096,4) if x[i:i+4]!=header[i:i+4]]
assert not t['remaining_breakpoints'] and t['physical_mode_restored'] and not t['physical_mode_remaining'] and not t.get('cleanup_error')
assert a['host_exit']['passed'] and a['allocation']['allocation_consistent'] and a['source_unchanged'] and a['eeprom_unchanged'] and p['passed']
assert all(not v['present'] for v in a['receipts'].values())
win=subprocess.run(['pwsh','-NoProfile','-Command',"@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' } | Select-Object ProcessId,Name) | ConvertTo-Json -Compress"],capture_output=True,text=True,timeout=30,check=True).stdout.strip();assert win in ('','[]')
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','qemu'],capture_output=True,text=True,timeout=30);assert q.returncode==1 and not q.stdout.strip()
files={str(f):sha(f) for f in Path('C:/xwn511').rglob('*') if f.is_file()}
r=dict(closeout_passed=True,runtime_observer_passed=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       reason='Observer incorrectly required encoded on-disk entry in already decoded loaded header',
       initial_entry_observed=True,jump_executed=False,diagnostic_API_calls_observed=0,
       header_dword_differences=diff,loaded_entry=0x11100,pinned_encoded_entry=struct.unpack_from('<I',x,296)[0],stub_hex=stub.hex(),
       all_owned_processes_closed=True,closed_sessions=[76640,50684,35492],frozen_inputs=len(pins),external_inputs=len(external),
       private_files_verified=len(files),private_files=files,protected_files_exact=8,
       strict_whole_disk_equal=a['strict_whole_disk_equal'],changed_bytes=a['changed_bytes'],
       physical_access=False,windows_started=False,normal_guest_shutdown=False,physical_launch_queued=False)
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print({k:v for k,v in r.items() if k!='private_files'})
