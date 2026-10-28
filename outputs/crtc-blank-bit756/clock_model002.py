"""Execute actual main.obj clock-gate fragment with injected EDX:EAX return.
Tests capture/log arguments and complete64-bit comparison, not kernel clock accuracy
or libc printf implementation. No Xbox/VM access, no video/register writes.
"""
import sys,os,json,hashlib,datetime,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn756/build001')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
assert os.environ.get('XBOX_XEMU_MODE')=='exclusive'
out=K/'clock-model002.json';assert not out.exists()
b=(P/'main.obj').read_bytes();r={'passed':False,'object_sha256':hashlib.sha256(b).hexdigest(),'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':__doc__,'cases':[]}
try:
 machine,nsec,_,_,_,optsz,_=struct.unpack_from('<HHLLLHH',b);assert machine==0x14c and optsz==0
 secs=[struct.unpack_from('<8sLLLLLLHHL',b,20+40*i) for i in range(nsec)]
 h=next(v for v in secs if v[0].rstrip(b'\0')==b'.text');code=b[h[4]:h[4]+h[3]]
 dis=subprocess.check_output(['wsl','-d','Ubuntu','--','objdump','-dr','/mnt/c/xwn756/build001/main.obj'],text=True)
 a=dis.index('__imp__KeQueryPerformanceFrequency');snippet=dis[a:a+1650]
 assert '154:' in snippet and '17f: DISP32\t_append' in snippet and '19e: dir32' in snippet and 'clock_reference_refused' in snippet and '1c1:' in snippet
 assert code[0x152:0x154]==b'\xff\xd0' and code[0x17e:0x183]==bytes.fromhex('e800000000')
 assert code[0x154:0x162]==bytes.fromhex('899424ac050000898424a8050000')
 assert code[0x191:0x19a]==bytes.fromhex('35987f330009c87427')
 assert b'kernel_qpc_frequency_high' in b
 r['disassembly_excerpt']=snippet
 cases=[(3375000,0),(3374999,0),(3375001,0),(3375300,0),(3375400,0),(0,0),(0xffffffff,0),(3375000,1),(3375000,0xffffffff),(0,1)]
 for low,high in cases:
  c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(0x100000,0x10000);c.mem_write(0x100000,code);c.mem_map(0x200000,0x10000);c.mem_write(0x200000,b'G'*0x10000)
  c.reg_write(x.UC_X86_REG_ESP,0x208000);c.reg_write(x.UC_X86_REG_EAX,low);c.reg_write(x.UC_X86_REG_EDX,high)
  logs=[];ends=[];writes=[]
  def hook(uc,pc,size,_):
   if pc in [0x10019c,0x1001c1]:ends.append(pc);uc.emu_stop();return
   assert 0x100154<=pc<0x10019c,(hex(pc),size)
   if pc==0x10017e:
    args=list(struct.unpack('<II',uc.mem_read(0x208004,8)));assert args==[low,high];logs.append(args)
    for reg in [x.UC_X86_REG_EAX,x.UC_X86_REG_ECX,x.UC_X86_REG_EDX]:uc.reg_write(reg,0xdeadbeef)
    uc.reg_write(x.UC_X86_REG_EIP,pc+5)
  def write(uc,kind,addr,size,val,_):
   assert (0x208000<=addr and addr+size<=0x20800c) or (0x2085a8<=addr and addr+size<=0x2085b0),(hex(addr),size)
   writes.append([addr,size])
  c.hook_add(u.UC_HOOK_CODE,hook);c.hook_add(u.UC_HOOK_MEM_WRITE,write)
  c.emu_start(0x100154,0x100200,count=100,timeout=100000)
  admitted=(low==3375000 and high==0)
  assert ends==[0x1001c1 if admitted else 0x10019c] and logs==[[low,high]]
  assert c.reg_read(x.UC_X86_REG_ESP)==0x208000
  r['cases'].append({'low':low,'high':high,'logged_arguments':logs[0],'admitted':admitted,'endpoint':hex(ends[0]),'writes':writes})
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS756 actual clock gate',len(r['cases']),'cases')
