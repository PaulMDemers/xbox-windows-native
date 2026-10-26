"""Six fresh instruction fixtures; adapter return and reset are modeled."""
import hashlib,json,re,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=Path('C:/xwn677/wrapper001')
assert not O.exists() and not (K/'wrapper001.json').exists();O.mkdir()
sys.path.insert(0,str(W/'work/python-packages'));import unicorn as u
from unicorn import x86_const as x
build=json.loads((K/'validation002.json').read_text());assert build['passed']
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
r=dict(passed=False,physical_access=False,adapter_io='stubbed return; no hardware semantics inferred',cases=[])
try:
 for mode,name in [(1,'default720'),(3,'explicit480')]:
  root='/home/paul/xbox-windows-native/launcher677-validation002/'+name
  binary=O/(name+'.bin')
  subprocess.run(['wsl','-d','Ubuntu','--','objcopy','-O','binary',root+'/source/obj/image-crom.elf','/mnt/c/xwn677/wrapper001/'+binary.name],check=True,timeout=30)
  blob=binary.read_bytes();syms=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+'/symbols.txt']).decode()
  sym={a[2]:int(a[0],16) for line in syms.splitlines() if len(a:=line.split())==3}
  for result in [1,0,-1]:
   uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x200000);uc.mem_write(0x02600000,blob)
   uc.reg_write(x.UC_X86_REG_EFLAGS,0x202);uc.mem_write(sym['xbox_ram'],pack(64))
   end=0x027ef000;out=0x027e0000;sp=0x027fe000
   uc.mem_write(out,b'\xa5'*64);uc.mem_write(sp,pack(end,out,0,3,10));uc.reg_write(x.UC_X86_REG_ESP,sp)
   seen=dict(requests=[],resets=[],held=False)
   def ret(v):
    p=uc.reg_read(x.UC_X86_REG_ESP);dest=struct.unpack('<I',uc.mem_read(p,4))[0]
    uc.reg_write(x.UC_X86_REG_EAX,v&0xffffffff);uc.reg_write(x.UC_X86_REG_ESP,p+4);uc.reg_write(x.UC_X86_REG_EIP,dest)
   def adapter(uc,a,size,user):
    p=struct.unpack('<I',uc.mem_read(uc.reg_read(x.UC_X86_REG_ESP)+8,4))[0]
    seen['requests'].append(list(struct.unpack('<8I',uc.mem_read(p,32))));ret(result)
   def reset(uc,a,size,user):
    seen['resets'].append(list(struct.unpack('<3I',uc.mem_read(uc.reg_read(x.UC_X86_REG_ESP)+8,12))));ret(0)
   def instruction(uc,a,size,user):
    if uc.mem_read(a,1)==b'\xf4':
     assert not uc.reg_read(x.UC_X86_REG_EFLAGS)&512;seen['held']=True;uc.emu_stop()
   def forbidden(*args):raise AssertionError('Unexpected physical I/O in stubbed fixture')
   uc.hook_add(u.UC_HOOK_CODE,adapter,None,sym['xwn_hd_apply'],sym['xwn_hd_apply'])
   uc.hook_add(u.UC_HOOK_CODE,reset,None,sym['xwn_hd_smb_write'],sym['xwn_hd_smb_write'])
   uc.hook_add(u.UC_HOOK_CODE,instruction)
   uc.hook_add(u.UC_HOOK_INSN,forbidden,None,1,0,x.UC_X86_INS_IN);uc.hook_add(u.UC_HOOK_INSN,forbidden,None,1,0,x.UC_X86_INS_OUT)
   uc.emu_start(sym['XwnHdTry720'],end,timeout=1000000,count=10000)
   assert seen['requests']==[[mode,64<<20,55<<20,9<<20,316160,0,3,10]]
   held=result<0 or mode==3 and result==0
   assert seen['held']==held and seen['resets']==([[16,2,1]] if held else [])
   if not held:assert uc.reg_read(x.UC_X86_REG_EIP)==end and uc.reg_read(x.UC_X86_REG_EAX)==result
   geometry=struct.unpack('<4I',uc.mem_read(out+16,16))
   if result==1:assert geometry==((1280,720,0,0) if mode==1 else (720,480,0,0))
   else:assert bytes(uc.mem_read(out,64))==b'\xa5'*64
   if mode==3 and result==0:assert struct.unpack('<I',uc.mem_read(sym['XwnHdState311']+4,4))[0]==30
   r['cases'].append(dict(build=name,adapter_return=result,mode=mode,held=held,geometry=list(geometry),binary_sha256=hashlib.sha256(blob).hexdigest()))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:(K/'wrapper001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'compiled wrapper fixtures')
