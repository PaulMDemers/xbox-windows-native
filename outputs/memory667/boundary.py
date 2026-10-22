"""Exact-linked boundary wrapper tests with a modeled memory detector, no hardware.
The detector's outgoing IF is controlled only inside this host test. Production
wrapper performs two PUSHF/POP-to-GPR reads and the unchanged original call.
"""
import datetime,hashlib,json,re,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('C:/xwn667/build001');P=Path('C:/xwn667/boundary001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
sha=lambda b:hashlib.sha256(b).hexdigest()
build=json.loads((K/'build001.json').read_text());blob=(B/'image-crom.bin').read_bytes()
assert sha(blob)==build['artifacts']['image-crom.bin']['sha256']
out=K/'boundary001.json';assert not out.exists() and not P.exists();P.mkdir()
r=dict(passed=False,physical_access=False,source_sha256=sha(Path(__file__).read_bytes()),image_sha256=sha(blob),cases=[],scope='Exact linked wrapper with modeled BootDetectMemorySize return; no physical interrupt or memory detection proof.')
try:
 elf='/mnt/c/xwn667/build001/image-crom.elf'
 nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n',elf],text=True,timeout=25)
 sym={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
 dis={}
 for name in ['XwnMemoryBoundary667','BootResetAction','BootDetectMemorySize','malloc','free']:
  dis[name]=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-d','--disassemble='+name,elf],text=True,timeout=25)
  (P/(name+'.txt')).write_text(dis[name])
 wrapper=dis['XwnMemoryBoundary667'];reset=dis['BootResetAction']
 assert wrapper.count('<BootDetectMemorySize>')==1
 assert not re.search(r'\t(?:cli|sti|popf\w*|in\w*|out\w*|wrmsr|wbinvd)\b|%cr',wrapper)
 instructions=re.findall(r'^\s*([0-9a-f]+):\s+(?:[0-9a-f]{2}\s+)+\s*(.+)$',wrapper,re.M)
 pushes=[int(a,16) for a,op in instructions if op.strip().startswith('pushf')];assert len(pushes)==2
 call=[int(a,16) for a,op in instructions if '<BootDetectMemorySize>' in op][0]
 assert pushes[0]<call<pushes[1]
 call_index=next(i for i,(a,op) in enumerate(instructions) if int(a,16)==call)
 assert int(instructions[call_index+1][0],16)==pushes[1], 'post capture must immediately follow call'
 assert reset.count('<XwnMemoryBoundary667>')==1 and '<BootDetectMemorySize>' not in reset
 assert reset.index('<cache_enable>')<reset.index('<XwnMemoryBoundary667>')<reset.index('<BootEepromReadEntireEEPROM>')<reset.index('<BootVgaInitializationKernelNG>')<reset.index('<BootPciInterruptEnable>')
 assert '<malloc>' in dis['BootDetectMemorySize'] and '<free>' in dis['BootDetectMemorySize']
 assert '\tsti' in dis['malloc'] and '\tsti' in dis['free']
 r['placement']=dict(before_pushf=hex(pushes[0]),detector_call=hex(call),after_pushf=hex(pushes[1]),post_read_immediate=True,original_order_preserved=True)
 for before in [0,1]:
  for after in [0,1]:
   uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob);uc.mem_map(0x027f0000,0x10000)
   esp=0x027fe000;end=0x026ff000;uc.mem_write(esp,struct.pack('<I',end));uc.reg_write(x.UC_X86_REG_ESP,esp);uc.reg_write(x.UC_X86_REG_EFLAGS,2|(before<<9))
   calls=[];observed=[]
   def capture(uc,a,size,user):observed.append(uc.reg_read(x.UC_X86_REG_EFLAGS))
   def memory(uc,a,size,user):
    calls.append(a);flags=uc.reg_read(x.UC_X86_REG_EFLAGS);assert (flags>>9)&1==before
    saved=struct.unpack('<4I',uc.mem_read(sym['Memory667'],16));assert saved[0]==observed[0] and saved[2]==0x667b0001 and saved[3]==0
    uc.reg_write(x.UC_X86_REG_EFLAGS,(flags&~512)|(after<<9))
    sp=uc.reg_read(x.UC_X86_REG_ESP);dest=struct.unpack('<I',uc.mem_read(sp,4))[0];uc.reg_write(x.UC_X86_REG_ESP,sp+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
   for p in pushes:uc.hook_add(u.UC_HOOK_CODE,capture,None,p,p)
   uc.hook_add(u.UC_HOOK_CODE,memory,None,sym['BootDetectMemorySize'],sym['BootDetectMemorySize'])
   uc.emu_start(sym['XwnMemoryBoundary667'],end,timeout=1000000,count=1000)
   assert uc.reg_read(x.UC_X86_REG_EIP)==end and len(calls)==1 and len(observed)==2
   values=struct.unpack('<4I',uc.mem_read(sym['Memory667'],16))
   assert values==(observed[0],observed[1],0x667b0001,0x667a0001)
   assert ((values[0]>>9)&1,(values[1]>>9)&1)==(before,after)
   assert (uc.reg_read(x.UC_X86_REG_EFLAGS)>>9)&1==after and uc.reg_read(x.UC_X86_REG_ESP)==esp+4
   r['cases'].append(dict(incoming_IF=before,modeled_detector_outgoing_IF=after,saved_flags=list(values[:2]),validity_markers=list(values[2:]),calls=1,wrapper_preserves_outgoing_IF=True))
 r['disassembly_pins']={p.name:sha(p.read_bytes()) for p in P.iterdir()};r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS linked placement and four memory-boundary transitions')
