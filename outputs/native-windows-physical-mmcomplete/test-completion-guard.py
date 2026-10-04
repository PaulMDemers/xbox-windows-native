"""Inject one bounded error into an owned emulator; never access hardware."""
import argparse,ftplib,json,pathlib,struct,sys
kit=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parent/'native-windows-prebuild'))
from monitor_capture import command,acquire_monitor_lock
from debug_remote import Remote
p=argparse.ArgumentParser()
for name in ['gdb','monitor','ftp']:p.add_argument('--'+name,type=int,required=True)
p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True)
p.add_argument('--corrupt',choices=['status','free-count','color-head','image-reference','free-cycle'],required=True)
a=p.parse_args();e=json.loads(a.reference.read_text())['entry_record']['words'];K=e[6]
lock=acquire_monitor_lock(a.monitor);command(a.monitor,'stop');g=Remote(a.gdb);g.ask('qSupported');g.ask('?')
def u32(addr):return struct.unpack('<I',g.read(addr,4))[0]
def write(addr,value):assert g.ask(f'M{addr:x},4:'+struct.pack('<I',value).hex())=='OK'
report={'emulator_only':True,'corruption':a.corrupt,'passed':False}
try:
 g.bp(e[80]);g.send('c')
 with ftplib.FTP() as ftp:
  ftp.connect('127.0.0.1',a.ftp,timeout=15);ftp.login('xbox','xbox');ftp.sendcmd(r'SITE EXEC E:\Applications\XWNLoader\default.xbe')
 g.recv();assert g.regs()['eip']==e[80];g.bp(e[80],False)
 if a.corrupt=='status':
  raw=bytearray.fromhex(g.ask('g'));report['original']=struct.unpack_from('<I',raw)[0];struct.pack_into('<I',raw,0,0);assert g.ask('G'+raw.hex())=='OK'
 else:
  if a.corrupt=='free-count':addr=K+0x81bf8;value=u32(addr)-1
  elif a.corrupt=='color-head':addr=u32(K+0x811bc);value=0xffffffff
  elif a.corrupt=='image-reference':addr=0xffb85000+((K&0x7fffffff)>>12)*24+12;value=u32(addr)&0xffff
  else:
   first=u32(K+0x72770);addr=0xffb85000+first*24;value=first
  report.update(address=hex(addr),original=u32(addr),injected=value);write(addr,value)
 audit=json.loads((kit/'map-boundary-audit.json').read_text());halts=[x for x in audit['blocks']['_HalpXwnMapCheckpoint@4'] if x['op']=='hlt'];assert len(halts)==1
 halt=e[8]+int(halts[0]['rva'],16);g.bp(halt);g.send('c');g.recv();assert g.regs()['eip']==halt
 record=list(struct.unpack('<352I',g.read(e[95],1408)));report['record']=record
 assert record[3]==40 and record[24]==230 and record[293]==1 and record[309]==1 and record[335]==0
 assert record[87]==record[308]==1
 report['passed']=True;a.output.write_text(json.dumps(report,indent=2)+'\n')
finally:g.s.close();lock.close()
print('Rejected '+a.corrupt+' before MM returned to executive initialization.')
