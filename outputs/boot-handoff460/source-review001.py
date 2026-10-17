"""Reconstruct the exact original wrapper and review the actual compiled capsule."""
import ast,hashlib,json,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;B=Path('/mnt/e/xwn460/build003')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def path(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
out=K/'source-review001.json';assert not out.exists()
r=json.loads((K/'build003.json').read_text());assert r['status']=='compiled'
for p,h in r['pins'].items():assert sha(Path(p))==h,p
assert sha(B/'xbeboot.S')==r['source_sha256'] and sha(B/'default.xbe')==r['sha256']
original=Path('/mnt/e/xwn374/build001/default.xbe').read_bytes()
assert hashlib.sha256(original).hexdigest()==r['original_xbe_sha256']
raw=Path('/home/paul/xbox-windows-native/build/resolution-e374-build001/source/boot_xbe/xbeboot.S').read_bytes()
assert hashlib.sha256(raw).hexdigest()==r['original_wrapper_sha256']
tree=ast.parse((K/'build003.py').read_text());changes=[]
for stmt in tree.body:
 if isinstance(stmt,ast.Expr) and isinstance(stmt.value,ast.Call) and isinstance(stmt.value.func,ast.Name) and stmt.value.func.id=='replace':
  a,b=[eval(compile(ast.Expression(x),'<reviewed-builder-expression>','eval'),dict(K=K,struct=struct,original=original)) for x in stmt.value.args]
  changes.append((a,b))
assert len(changes)==11
text=(B/'xbeboot.S').read_text()
for a,b in reversed(changes):assert text.count(b)==1; text=text.replace(b,a)
assert text.encode()==raw
x=(B/'default.xbe').read_bytes();assert x[12288:]==original[12288:] and x[0x1080:0x1088]==original[0x1080:0x1088]
s=840;head=bytearray(x[:4096]);head[s+36:s+56]=original[s+36:s+56];assert head==original[:4096]
off,size=struct.unpack_from('<II',x,s+12);assert hashlib.sha1(struct.pack('<I',size)+x[off:off+size]).digest()==x[s+36:s+56]
symbols=r['symbols'];assert symbols['diag_record']-symbols['blentry']>=1024
assert symbols['diag_trailer']-symbols['diag_record']==160
assert x[symbols['diag_handoff']-65536:symbols['diag_handoff']-65536+4]==b'\x61\x9d\xff\xe2'
assert x[symbols['blentry']-65536]==0xfa
assert symbols['newloc']-symbols['blentry']==80 and symbols['ptr_newloc']-symbols['blentry']==74
host=json.loads((K/'host001.json').read_text());assert host['status']=='passed' and host['cases']==45
for p,v in host['files'].items():assert sha(Path(p))==v['sha256']
dec=json.loads((K/'decoder001.json').read_text());assert dec['passed'] and dec['negative_controls_rejected']==296
for p,h in dec['files'].items():assert sha(path(p))==h
dis=subprocess.check_output(['objdump','-d','-Mintel',str(B/'wrapper.elf')]);(B/'review-disassembly.txt').write_bytes(dis)
result=dict(reviewed=True,qualified_wrapper_sha256=r['sha256'],original_source_reconstructed_byte_exact=True,
 explicit_replacement_sites=len(changes),embedded_payload_bytes=len(x)-12288,embedded_payload_unchanged=True,
 original_header_except_digest=True,section_digest_valid=True,actual_handoff_bytes='61 9d ff e2',
 original_privileged_loader_unchanged_by_source_reconstruction=True,host_actual_wrapper_cases=45,
 decoder_negative_controls=296,physical_execution=False,installed_launcher_changed=False,
 limitations=['Kernel/file effects modeled in host harness; CLI faults before execution, no CR0 execution',
 'A full report does not prove final flush/close/post-log checks or handoff',
 'Diagnostic changes timing and allocations; individual kernel file calls not independently cancellable'],
 pins={str(p):sha(p) for p in [K/'source-review001.py',K/'build003.py',K/'build003.json',K/'logger.S',K/'verify.S',K/'decode.py',K/'decoder001.json',K/'host001.json',B/'xbeboot.S',B/'default.xbe',B/'review-disassembly.txt']})
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['reviewed','explicit_replacement_sites','host_actual_wrapper_cases','decoder_negative_controls']}))
