"""Corrected decoder regression: actual report digest, unchanged pixel predicates."""
import hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('C:/xwn491/host002');out=K/'oracle-tests002.json';assert not P.exists() and not out.exists()
P.mkdir(parents=True)
files={'tools/graphics_d3dpresent.py':K/'decoder002.py','tools/graphics_present.py':W/'tools/graphics_present.py','tests/test_graphics_d3dpresent.py':W/'tests/test_graphics_d3dpresent.py','tests/test_graphics_present.py':W/'tests/test_graphics_present.py'}
for name,source in files.items():
 p=P/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source.read_bytes())
test=P/'tests/test_graphics_d3dpresent.py'
test.write_text(test.read_text().replace('import struct','import struct\nimport hashlib').replace('    def test_edge_allowance_is_bounded(self):',"    def test_actual_report_digest(self):\n        r=g.validate(encode(self.r),self.c,'default',0)\n        self.assertEqual(r['report_sha256'],hashlib.sha256(encode(self.r)).hexdigest())\n    def test_edge_allowance_is_bounded(self):"),newline='\n')
r=subprocess.run([sys.executable,'-B',str(test)],capture_output=True,text=True,timeout=120)
out.write_text(json.dumps(dict(passed=r.returncode==0,exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in P.rglob('*') if p.is_file()}),indent=2)+'\n');print(r.stderr);assert not r.returncode
