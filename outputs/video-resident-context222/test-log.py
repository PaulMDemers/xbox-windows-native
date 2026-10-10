"""Log oracle positives/negative mutations, not a guest workload."""
import importlib.util,json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'parser-tests001.json';assert not dest.exists()
spec=importlib.util.spec_from_file_location('log222',k/'analyze-log.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rows=['BEGIN_CPU_OWNER_ONLY 222 16384 0','INSTALL_BEFORE_WORK 0 0 0','OWNER_STALE_SHORT_CLEANUP 1 1 1']
for i in range(64):rows+=['LEASE %d %d 2097152'%(i//16,i+2),'RELEASE %d %d 0'%(i//16,i+2)]
rows+=['WORKER %d 16 0'%i for i in range(4)]+['WAIT_JOIN 3 4 0','COMPLETE_CPU_OWNER_ONLY 65 65 65','VERIFIED_JOINED 3194880 1 4','INSTALL_BEFORE_RESTART 0 0 0','NORMAL_RESTART_REQUEST 222 0 0']
data=('\r\n'.join(rows)+'\r\n').encode();assert m.analyze(data)['passed']
interleaved=rows[:];interleaved[4],interleaved[35]=interleaved[35],interleaved[4]
# Select two neighboring distinct-worker lease/release pairs for actual log reordering.
interleaved=rows[:];interleaved[34],interleaved[35]=interleaved[35],interleaved[34]
assert m.analyze(('\r\n'.join(interleaved)+'\r\n').encode())['passed']
mutations=[data[:-2],data.replace(b'WAIT_JOIN 3',b'WAIT_JOIN 258'),data.replace(b'WORKER 0 16',b'WORKER 0 15'),data.replace(b'LEASE 0 2 ',b'LEASE 0 3 '),data.replace(b'RELEASE 0 2 0',b'RELEASE 0 2 1'),data.replace(b'2097152',b'62914560'),data.replace(b'3194880',b'3194879'),data+b'FAIL 0 0 0\r\n',data.replace(b'INSTALL_BEFORE_RESTART 0',b'INSTALL_BEFORE_RESTART 258')]
for blob in mutations:assert not m.analyze(blob)['passed']
dest.write_text(json.dumps(dict(passed=True,positive_cases=2,negative_cases=len(mutations),parser_sha256=hashlib.sha256((k/'analyze-log.py').read_bytes()).hexdigest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),guest_launch=False),indent=2)+'\n');print('Parser cases PASS')
