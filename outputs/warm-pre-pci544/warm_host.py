"""MIT. Restart admission negatives and independent exact542 binary comparison."""
import copy,hashlib,importlib.util,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('warm544',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
o=dict(at_dashboard=True,user_report_received=True,normal_windows_restart=True,manual_reset=False)
a=dict(closed=True,hives_clean=True,ordinary_code_exact=True,events={'system':{'normal_shutdown_delta':1}})
r=dict(no_powercycle_since_primer=True);cases=[]
c.warm_admit(o,a,r);cases.append('normal_restart_admitted')
for group,key,value in [(0,'at_dashboard',False),(0,'user_report_received',False),(0,'normal_windows_restart',False),(0,'manual_reset',True),(1,'closed',False),(1,'hives_clean',False),(1,'ordinary_code_exact',False),(2,'no_powercycle_since_primer',False)]:
 args=copy.deepcopy([o,a,r]);args[group][key]=value
 try:c.warm_admit(*args)
 except AssertionError:cases.append('reject_'+key)
 else:raise AssertionError(key)
for value in [0,-1]:
 bad=copy.deepcopy(a);bad['events']['system']['normal_shutdown_delta']=value
 try:c.warm_admit(o,bad,r)
 except AssertionError:cases.append('reject_shutdown_delta_'+str(value))
 else:raise AssertionError('shutdown delta')
def image(k):
 row=json.loads((k/'prepared001.json').read_text())['images']['1'];b=Path(row['path']).read_bytes()
 assert hashlib.sha256(b).hexdigest()==row['sha256'];return b
old=image(K.parent/'pre-pci-stop542');new=image(K)
assert new.count(b'XWNBoot544a')==old.count(b'XWNBoot542a')==4
normalized=bytearray(new.replace(b'XWNBoot544a',b'XWNBoot542a'))
normalized[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(normalized)-4096)+normalized[4096:]).digest()
assert bytes(normalized)==old
out=K/'warm-host001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,cases=cases,normalized_542_binary_exact=True,source_sha256=hashlib.sha256((K/'controller.py').read_bytes()).hexdigest(),physical_access=False),indent=2)+'\n')
print('PASS',len(cases),'restart admission cases; normalized542 exact')
