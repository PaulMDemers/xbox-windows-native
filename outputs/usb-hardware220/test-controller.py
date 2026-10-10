"""Offline fault checks for queue gating, single launch and startup-first recovery."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
K=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('usbphysical',K/'physical.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class FTP:
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def mkd(self,p):pass
    def sendcmd(self,c):raise EOFError('simulated lost launch reply')

class Checks(unittest.TestCase):
    def setUp(self):
        root=K.parents[1]/'work';root.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(prefix='usb220-test-',dir=root);self.k=Path(self.tmp.name)
        self.patches=[patch.object(m,'K',self.k),patch.object(m,'ART',self.k/'artifacts'),
            patch.object(m,'RECORD',self.k/'physical.json'),patch.object(m,'QUEUE',self.k/'queue')]
        for p in self.patches:p.start()
        m.ART.mkdir();(m.ART/'incoming-rollback.zip').write_bytes(b'rollback')
        self.exe=self.k/'usbprobe.exe';self.exe.write_bytes(b'probe')
        (self.k/'before-hive-audit.json').write_text('{"passed":true}')
        (self.k/'before-allocation.json').write_text('{"allocation_consistent":true}')
        r=dict(capture_complete=True,companions_captured=True,launch_requested=False,startup_enabled=False,before={})
        for i,key in enumerate([m.STARTUP]+m.HIVES):r['before'][key]=m.keep('before/'+str(i),key.encode())
        m.save(r)
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def setup_launch(self):
        r=m.read(m.RECORD);data={m.STARTUP:m.local(r['before'][m.STARTUP])}
        data.update({m.auxiliary()[n]:m.local(r['before'][n]) for n in m.HIVES})
        return [patch.object(m,'pins',return_value={'binary':str(self.exe)}),
            patch.object(m,'connect',return_value=FTP()),patch.object(m,'names',return_value=set()),
            patch.object(m,'expected',return_value={m.STARTUP:'unused'}),patch.object(m,'get',side_effect=lambda f,p:data[p])]
    def test_queue_refusal_prevents_socket(self):
        with patch.object(m,'FTP') as ftp:
            with self.assertRaises(FileNotFoundError):m.connect()
            ftp.assert_not_called()
    def test_transient_record_replace_recovers(self):
        actual=Path.replace;attempts=[]
        def flaky(path,target):
            attempts.append(1)
            if len(attempts)==1:raise PermissionError('temporary scanner lock')
            return actual(path,target)
        with patch.object(Path,'replace',flaky),patch.object(m.time,'sleep'):
            m.save({'durable':'yes'})
        self.assertEqual(len(attempts),2);self.assertEqual(m.read(m.RECORD),{'durable':'yes'})
    def test_closed_ticket_prevents_socket(self):
        state=m.QUEUE/'state';state.mkdir(parents=True)
        for name,value in [('audio-closed',{'baseline_restored':True}),('usb-claimed',{'owner':'usb'}),('usb-closed',{})]:
            (state/(name+'.json')).write_text(json.dumps(value))
        with patch.object(m,'FTP') as ftp:
            with self.assertRaises(AssertionError):m.connect()
            ftp.assert_not_called()
    def test_uncertain_launch_cannot_repeat(self):
        ps=self.setup_launch()
        for p in ps:p.start()
        try:
            with patch.object(m,'put'):
                m.launch();r=m.read(m.RECORD)
                self.assertTrue(r['launch_requested']);self.assertEqual(r['launch_reply_uncertain'],'EOFError')
                with self.assertRaises(AssertionError):m.launch()
        finally:
            for p in reversed(ps):p.stop()
    def test_partial_startup_write_restores_before_launch(self):
        ps=self.setup_launch();writes=[]
        def put(f,path,data):
            writes.append((path,data))
            if path==m.STARTUP and data==m.TEST:raise OSError('partial write')
        for p in ps:p.start()
        try:
            with patch.object(m,'put',side_effect=put):
                with self.assertRaises(OSError):m.launch()
            r=m.read(m.RECORD)
            self.assertEqual(writes[-1],(m.STARTUP,m.local(r['before'][m.STARTUP])))
            self.assertFalse(r['launch_requested']);self.assertFalse(r['startup_enabled'])
        finally:
            for p in reversed(ps):p.stop()
    def test_collection_restores_startup_before_failed_log_read(self):
        r=m.read(m.RECORD);r['launch_requested']=True;r['startup_enabled']=True;m.save(r);order=[]
        def put(*args):order.append('restore')
        def get(*args,**kw):order.append('read');raise OSError('lost connection')
        with patch.object(m,'pins'),patch.object(m,'connect',return_value=FTP()),patch.object(m,'put',side_effect=put),patch.object(m,'get',side_effect=get):
            with self.assertRaises(OSError):m.collect()
        self.assertEqual(order,['restore','read']);self.assertFalse(m.read(m.RECORD)['startup_enabled'])

if __name__=='__main__':unittest.main()
