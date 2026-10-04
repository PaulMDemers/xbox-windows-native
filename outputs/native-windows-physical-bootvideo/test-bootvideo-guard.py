"""Inject one bounded error into an owned emulator; never access hardware."""
import argparse,ftplib,json,pathlib,struct,sys
kit=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
from debug_remote import Remote
p=argparse.ArgumentParser()
for name in ['gdb','monitor','ftp']:p.add_argument('--'+name,type=int,required=True)
p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True)
p.add_argument('--corrupt',choices=['video-disabled','debug-display','wrong-loader','mm-incomplete','phase1-caller'],required=True)
a=p.parse_args();e=json.loads(a.reference.read_text())['entry_record']['words'];K=e[6]
lock=acquire_monitor_lock(a.monitor);command(a.monitor,'stop');g=Remote(a.gdb);g.ask('qSupported');g.ask('?')
def u32(addr):return struct.unpack('<I',g.read(addr,4))[0]
def write(addr,value):assert g.ask(f'M{addr:x},4:'+struct.pack('<I',value).hex())=='OK'
report={'emulator_only':True,'corruption':a.corrupt,'passed':False}
try:
 audit=json.loads((kit/'map-boundary-audit.json').read_text())
 phase=a.corrupt in ['mm-incomplete','phase1-caller']
 target=e[8]+int(audit['symbols_rva']['_HalpXwnPhase1'],16) if phase else e[352]
 g.bp(target);g.send('c')
 with ftplib.FTP() as ftp:
  ftp.connect('127.0.0.1',a.ftp,timeout=15);ftp.login('xbox','xbox');ftp.sendcmd(r'SITE EXEC E:\Applications\XWNLoader\default.xbe')
 g.recv();regs=g.regs();assert regs['eip']==target;g.bp(target,False)
 if a.corrupt=='video-disabled':addr=K+0x739c0;value=0
 elif a.corrupt=='debug-display':addr=K+0x739c4;value=1
 elif a.corrupt=='wrong-loader':addr=regs['ebp']+8;value=e[4]+4
 elif a.corrupt=='mm-incomplete':addr=e[95]+336*4;value=0
 else:addr=regs['esp']+8;value=K+0x148523
 report.update(address=hex(addr),original=u32(addr),injected=value);write(addr,value)
 block='_HalpXwnPhase1' if phase else '_HalpXwnBootAfter@4'
 halts=[x for x in audit['blocks'][block] if x['op']=='hlt'];assert len(halts)==1
 halt=e[8]+int(halts[0]['rva'],16);g.bp(halt);g.send('c');g.recv();assert g.regs()['eip']==halt
 record=list(struct.unpack('<384I',g.read(e[95],1536)));report['record']=record
 assert record[3]==40 and record[335]==1
 if phase:assert record[341]==0 and record[351]==0
 else:assert record[24]==240 and record[341]==1 and record[350]==1 and record[351]==0
 report['passed']=True;a.output.write_text(json.dumps(report,indent=2)+'\n')
finally:g.s.close();lock.close()
print('Rejected '+a.corrupt+' before storage initialization.')
