"""Observe the unassisted MM phase-zero candidate in an owned emulator."""
import argparse,ftplib,json,pathlib,struct,sys
kit=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
from debug_remote import Remote
p=argparse.ArgumentParser()
for name in ['gdb','monitor','ftp']:p.add_argument('--'+name,type=int,required=True)
p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
e=json.loads(a.reference.read_text())['entry_record']['words'];K=e[6]
audit=json.loads((kit/'map-boundary-audit.json').read_text());halt=e[8]+int(next(x['rva'] for x in audit['blocks']['_HalpXwnMapCheckpoint@4'] if x['op']=='hlt'),16)
points={K+off:name for off,name in [(0x159cdc,'process-init-return'),(0x159d7c,'color-pool-allocation'),(0x159e09,'color-backing-released'),(0x155b55,'machine-mm-return'),(0x155b5d,'boot-images-reloaded'),(0x155b65,'driver-verifier-list'),(0x155f5a,'cache-page-tables'),(0x1560bd,'system-cache-ready'),(0x1561dc,'paged-pool-ready'),(0x1561e4,'loaded-module-list'),(0x1564c3,'mm-phase0-return')]}
points[halt]='validated-halt'
lock=acquire_monitor_lock(a.monitor);command(a.monitor,'stop');g=Remote(a.gdb);g.ask('qSupported');g.ask('?')
report={'emulator_only':True,'debugger_resumes_saved_native_registers':False,'events':[],'passed':False}
try:
 for addr in points:g.bp(addr)
 g.send('c')
 with ftplib.FTP() as ftp:
  ftp.connect('127.0.0.1',a.ftp,timeout=15);ftp.login('xbox','xbox');ftp.sendcmd(r'SITE EXEC E:\Applications\XWNLoader\default.xbe')
 for _ in range(len(points)):
  g.recv();regs=g.regs();name=points[regs['eip']];g.bp(regs['eip'],False)
  report['events'].append({'name':name,'regs':regs,'free_pages':struct.unpack('<I',g.read(K+0x81bf8,4))[0]})
  a.output.write_text(json.dumps(report,indent=2)+'\n')
  if name=='validated-halt':
   record=struct.unpack('<352I',g.read(e[95],1408));assert record[3]==90 and record[335]==1
   assert len(report['events'])==len(points);report['passed']=True;break
  g.send('c')
 assert report['passed'];a.output.write_text(json.dumps(report,indent=2)+'\n')
 # Execute the audited HLT after observing its address, so the independent
 # capture sees the CPU halted by the guest rather than by a breakpoint.
 g.send('c')
finally:g.s.close();lock.close()
print('Native MM phase-zero execution trace passed.')
