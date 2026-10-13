"""Exercise the actual selector with an in-memory FTP transport; no console access."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
s=importlib.util.spec_from_file_location('selector',W/'tools/configure-e-display.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class FTP:
    def __init__(self,files):self.files=dict(files);self.reads=[];self.writes=[];self.fail=False
    def retrbinary(self,cmd,callback,block):
        p=cmd.removeprefix('RETR ');self.reads.append(p);callback(self.files[p])
    def storbinary(self,cmd,stream,block):
        op,p=cmd.split(' ',1);self.writes.append(p);b=stream.read()
        self.files[p]=(self.files[p] if op=='APPE' else b'')+b
        if self.fail:self.fail=False;raise OSError('Simulated interrupted write')
class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.old=b'old launcher';self.new=b'new launcher'*5000
        pin=lambda b:dict(bytes=len(b),sha256=m.sha(b))
        self.policy=dict(target=m.TARGET,prerequisites={p:pin(p.encode()) for p in m.ALLOWED-{m.TARGET}},profiles={'1080i':pin(self.old),'720p':pin(self.new)})
        self.ftp=FTP({**{p:p.encode() for p in self.policy['prerequisites']},m.TARGET:self.old})
    def tearDown(self):
        self.assertTrue(set(self.ftp.reads)<=m.ALLOWED);self.assertTrue(set(self.ftp.writes)<={m.TARGET});self.tmp.cleanup()
    def test_apply_restore(self):
        r=self.root/'receipt';m.apply(self.ftp,self.policy,'720p',self.new,r);self.assertEqual(self.ftp.files[m.TARGET],self.new)
        m.restore(self.ftp,self.policy,r);self.assertEqual(self.ftp.files[m.TARGET],self.old)
        with self.assertRaises(ValueError):m.restore(self.ftp,self.policy,r)
    def test_corrupt_local_no_write(self):
        with self.assertRaises(ValueError):m.apply(self.ftp,self.policy,'720p',b'wrong',self.root/'r')
        self.assertFalse(self.ftp.writes)
    def test_wrong_prerequisite_no_write(self):
        self.ftp.files[next(iter(self.policy['prerequisites']))]=b'other'
        with self.assertRaises(ValueError):m.apply(self.ftp,self.policy,'720p',self.new,self.root/'r')
        self.assertFalse(self.ftp.writes)
    def test_unknown_current_no_write(self):
        self.ftp.files[m.TARGET]=b'unknown'
        with self.assertRaises(ValueError):m.inspect(self.ftp,self.policy)
        self.assertFalse(self.ftp.writes)
    def test_receipt_not_overwritten(self):
        r=self.root/'r';r.mkdir()
        with self.assertRaises(ValueError):m.apply(self.ftp,self.policy,'720p',self.new,r)
        self.assertFalse(self.ftp.writes)
    def test_interrupted_write_restores(self):
        self.ftp.fail=True;r=self.root/'r'
        with self.assertRaises(OSError):m.apply(self.ftp,self.policy,'720p',self.new,r)
        self.assertEqual(self.ftp.files[m.TARGET],self.old);self.assertTrue(m.read_json(r/'result.json')['rollback_verified'])
    def test_tampered_receipt_no_write(self):
        r=self.root/'r';m.apply(self.ftp,self.policy,'720p',self.new,r);(r/'before.xbe').write_bytes(b'corrupt');self.ftp.writes.clear()
        with self.assertRaises(ValueError):m.restore(self.ftp,self.policy,r)
        self.assertFalse(self.ftp.writes)
    def test_same_profile_no_write(self):
        m.apply(self.ftp,self.policy,'1080i',self.old,self.root/'r');self.assertFalse(self.ftp.writes)
    def test_other_volume_refused(self):
        for p in ['/C/config.xml','/F/winnt/system32/xwnown.dll','/E/../C/config.xml']:
            with self.assertRaises(ValueError):m.fetch(self.ftp,p)
    def test_wrong_policy(self):
        self.policy['target']='/F/default.xbe'
        with self.assertRaises(ValueError):m.inspect(self.ftp,self.policy)
        self.assertFalse(self.ftp.reads)
if __name__=='__main__':
    dest=K/'selector-tests001.json';assert not dest.exists()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    dest.write_text(json.dumps(dict(passed=result.wasSuccessful(),tests=result.testsRun,physical_access=False,transport='Modeled FTP; actual selector functions executed'),indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
