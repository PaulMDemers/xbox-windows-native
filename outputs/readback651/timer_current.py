"""Exact retained wait_us/GetTimerTicks instructions; synthetic IN, fresh CPU per case."""
import datetime,hashlib,json,struct,subprocess,sys
from fractions import Fraction
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
B=Path('C:/xwn651/build001');b=json.loads((K/'build001.json').read_text())
blob=(B/'image-crom.bin').read_bytes();sha=lambda v:hashlib.sha256(v).hexdigest()
assert sha(blob)==b['outputs']['image-crom.bin']['sha256']
nm=subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n','/mnt/c/xwn651/build001/image-crom.elf'],text=True,timeout=25)
symbols={a[2]:int(a[0],16) for line in nm.splitlines() if len(a:=line.split())==3}
out=K/'timer-current001.json';assert not out.exists()
r=dict(passed=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,guest_disk=False,retained_binary_sha256=sha(blob),results=[],scope='Exact timer/delay instructions in fresh isolated Unicorn CPUs; only IN is modeled. No real timer frequency, FPU state or elapsed physical duration established.')
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
def oracle(ticks):
 # Independent rational multiplication and nearest-even binary32 rounding.
 q=Fraction.from_float(3.579545)*min(ticks,1200000)
 if not q:return 0
 exponent=q.numerator.bit_length()-q.denominator.bit_length()
 if q<Fraction(2)**exponent:exponent-=1
 unit=Fraction(2)**(exponent-23);scaled=q/unit
 integer,rem=divmod(scaled.numerator,scaled.denominator)
 if rem*2>scaled.denominator or (rem*2==scaled.denominator and integer%2):integer+=1
 rounded=integer*unit
 return rounded.numerator//rounded.denominator
def trial(name,ticks,cw=0x37f,mode='boundary'):
 uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x02600000,0x100000);uc.mem_write(0x02600000,blob)
 uc.mem_map(0x027f0000,0x10000);esp=0x027fe000;end=0x026ff000
 uc.mem_write(esp,struct.pack('<2I',end,ticks));uc.reg_write(x.UC_X86_REG_ESP,esp)
 uc.reg_write(x.UC_X86_REG_FPCW,cw);uc.reg_write(x.UC_X86_REG_FPSW,0);uc.reg_write(x.UC_X86_REG_FPTAG,0xffff)
 for reg in (x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP):uc.reg_write(reg,0x12345678)
 reads=[];limit=[]
 def inp(uc,port,size,unused):
  assert port==0x8008 and size==4
  target=uc.reg_read(x.UC_X86_REG_EDI)
  if not limit:limit.append(target)
  assert target==limit[0]
  if mode=='boundary':seq=[100,100+target,101+target]
  elif mode=='wrap32':seq=[0xfffffff0,(0xfffffff0+target)&0xffffffff,(0xfffffff1+target)&0xffffffff]
  elif mode=='wrap24':seq=[0xfffff0,0xfffffa,5]
  elif mode=='backward':seq=[100,99]
  elif mode=='frozen':seq=[100]
  else:raise AssertionError(mode)
  value=seq[min(len(reads),len(seq)-1)];reads.append(value);return value
 uc.hook_add(u.UC_HOOK_INSN,inp,None,1,0,x.UC_X86_INS_IN)
 uc.emu_start(symbols['wait_us'],end,timeout=1000000,count=10000)
 returned=uc.reg_read(x.UC_X86_REG_EIP)==end
 assert returned==(mode!='frozen')
 assert uc.reg_read(x.UC_X86_REG_FPCW)==cw
 expected=oracle(ticks)
 if cw==0x37f:assert limit[0]==expected,(ticks,limit[0],expected)
 else:assert abs(limit[0]-expected)<=1,(cw,ticks,limit[0],expected)
 if mode in ('boundary','wrap32'):assert len(reads)==3
 if mode in ('backward',):assert len(reads)==2
 if mode=='wrap24':assert len(reads)==3 and (reads[-1]-reads[0])&0xffffffff>limit[0]
 if returned:
  assert uc.reg_read(x.UC_X86_REG_ESP)==esp+4
  assert all(uc.reg_read(reg)==0x12345678 for reg in (x.UC_X86_REG_EBX,x.UC_X86_REG_ESI,x.UC_X86_REG_EDI,x.UC_X86_REG_EBP))
 return dict(name=name,ticks_argument=ticks,fpu_control_word=cw,timer_model=mode,target=limit[0],nearest_even_oracle=expected,returned=returned,timer_reads=len(reads),first_timer=reads[0],last_timer=reads[-1],unsigned_delta=(reads[-1]-reads[0])&0xffffffff,host_instruction_budget=10000,control_word_preserved=True)
try:
 for ticks in (0,1,10,80,1000000,1200000,1200001,0xffffffff):r['results'].append(trial('normal',ticks));save()
 for cw in (0x77f,0xb7f,0xf7f,0x7f,0x27f):
  for ticks in (10,80,1000000,1200000):r['results'].append(trial('fpu_mode',ticks,cw));save()
 for mode in ('wrap32','wrap24','backward','frozen'):r['results'].append(trial(mode,10,mode=mode));save()
 r.update(passed=True,cases=len(r['results']),source_timer_frequency_assumption_hz=3579545,physical_timer_width_verified=False,
          limitations=['Unsigned subtraction supports modeled32-bit wrap, but24-bit wrap/backward jump returns early in this model','A frozen timer does not return within the host budget; existing wait_us has no independent iteration bound','FPU modes were set only in isolated host CPUs; no physical control registers/state changed','Normal source boot has CLTS/FNINIT, but current physical FPU state was not captured'])
except BaseException as e:r['failure']=repr(e);raise
finally:save()
print('PASS',len(r['results']),'compiled timer cases')
