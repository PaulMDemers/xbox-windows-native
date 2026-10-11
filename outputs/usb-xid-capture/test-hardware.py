"""Offline ticket and uncertain-launch guards; no console contact."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
k=Path(__file__).resolve().parent;s=importlib.util.spec_from_file_location('xid_hardware',k/'hardware.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Guards(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for name,value in [('QUEUE',self.root),('CLAIM',self.root/'usb-xid-claimed.json'),('CLOSED',self.root/'usb-xid-closed.json'),('RECORD',self.root/'physical001.json')]:
   p=patch.object(m,name,value);p.start();self.addCleanup(p.stop)
 def write(self,name,r):(self.root/name).write_text(json.dumps(r))
 def predecessors(self):
  for name in ['audio','usb','pci']:
   self.write(name+'-claimed.json',dict(owner=name));self.write(name+'-closed.json',dict(baseline_restored=True))
 def test_no_socket_without_ticket(self):
  with patch.object(m.old,'FTP') as ftp:
   with self.assertRaises(AssertionError):m.connect()
   ftp.assert_not_called()
 def test_new_claim_requires_all_predecessors_closed(self):
  with patch.object(m,'pins'):
   with self.assertRaises(FileNotFoundError):m.claim()
  self.assertFalse(m.CLAIM.exists())
 def test_other_active_successor_blocks_claim(self):
  self.predecessors();self.write('other-claimed.json',dict(owner='other'))
  with patch.object(m,'pins'):
   with self.assertRaises(AssertionError):m.claim()
  self.assertFalse(m.CLAIM.exists())
 def test_closed_ticket_blocks_socket_and_reclaim(self):
  self.predecessors();self.write('usb-xid-claimed.json',dict(owner='usb-xid'));self.write('usb-xid-closed.json',dict(baseline_restored=True))
  with patch.object(m.old,'FTP') as ftp,patch.object(m,'pins'):
   with self.assertRaises(AssertionError):m.connect()
   with self.assertRaises(AssertionError):m.claim()
   ftp.assert_not_called()
 def test_uncertain_launch_never_retries(self):
  self.write('physical001.json',dict(captured_utc='before',launch_requested=True,launch_uncertain='TimeoutError'))
  with patch.object(m,'pins'),patch.object(m,'connect') as ftp:
   with self.assertRaises(AssertionError):m.launch()
   ftp.assert_not_called()
 def test_partial_staging_never_retries(self):
  self.write('physical001.json',dict(captured_utc='before',launch_requested=False,staging_started=True))
  with patch.object(m,'pins'),patch.object(m,'connect') as ftp:
   with self.assertRaises(AssertionError):m.launch()
   ftp.assert_not_called()
suite=unittest.defaultTestLoader.loadTestsFromTestCase(Guards);result=unittest.TextTestRunner().run(suite)
(k/'hardware-tests.json').write_text(json.dumps(dict(passed=result.wasSuccessful(),tests=result.testsRun,physical_access=False),indent=2)+'\n')
raise SystemExit(0 if result.wasSuccessful() else 1)
