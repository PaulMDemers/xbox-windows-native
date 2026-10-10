"""Compile/test the future-driver wire decoder and replay every physical sample."""
import ctypes,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;src=k/'driver-core';out=k/'artifacts/decoder-tests';out.mkdir(exist_ok=True)
cc='C:/msys64/mingw64/bin/gcc.exe';flags=['-std=c99','-O2','-Wall','-Wextra','-Werror']
subprocess.run([cc,*flags,str(src/'xid_wire.c'),str(src/'test.c'),'-o',str(out/'test.exe')],check=True)
reply=subprocess.check_output([str(out/'test.exe')]).decode().strip();assert reply=='66083 XID decode checks passed',reply
subprocess.run([cc,*flags,'-shared',str(src/'xid_wire.c'),'-o',str(out/'xid_wire.dll')],check=True)
class Sample(ctypes.Structure):_fields_=[('digital',ctypes.c_uint16),('pressure',ctypes.c_uint8*8),('sticks',ctypes.c_int16*4)]
lib=ctypes.CDLL(str(out/'xid_wire.dll'));decode=lib.xwn_xid_decode;decode.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.POINTER(Sample)];decode.restype=ctypes.c_int
rows=json.loads((k/'artifacts/physical001/decoded.json').read_text())['reports'];valid=empty=0
for row in rows:
 assert row['status']==0
 b=bytes.fromhex(row['raw']);buf=ctypes.create_string_buffer(b);sample=Sample();ctypes.memset(ctypes.byref(sample),0xa5,ctypes.sizeof(sample));prior=bytes(sample)
 result=decode(buf,len(b),ctypes.byref(sample))
 if not b:assert result==0 and bytes(sample)==prior;empty+=1
 else:
  expected=row['decoded'];assert result==1 and sample.digital==expected['buttons'] and list(sample.pressure)==list(expected['analog'].values()) and list(sample.sticks)==expected['sticks'];valid+=1
r=dict(passed=True,host_checks=66083,physical_samples_replayed=len(rows),valid_samples=valid,empty_samples_preserved_without_state_update=empty,source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in src.iterdir() if p.is_file()},nt5_runtime_qualified=False,windows_driver_installed=False)
(k/'decoder-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
