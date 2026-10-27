"""Fresh legacy GPU-function audit over every uniform initial CRTC byte.
Exact rebuilt function; modeled MMIO/indexed reads, not a video-output model.
"""
from pathlib import Path
import sys,json,hashlib,struct,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn700/gpu-build001')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
out=K/'gpu001.json';assert not out.exists()
b=json.loads((K/'gpu-build001.json').read_text());assert b['passed']
for n,h in b['files'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h
blob=(P/'native.bin').read_bytes();syms={a[2]:int(a[0],16) for line in (P/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
r={'passed':False,'scope':__doc__,'physical_access':False,'image_sha256':hashlib.sha256(blob).hexdigest(),'cases':[]}
try:
 for initial in range(256):
  uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x100000,0x10000);uc.mem_write(0x100000,blob);uc.mem_map(0x200000,0x10000)
  base=0xfd000000;uc.mem_map(base,0x800000);end=0x10ff00;sp=0x208000;gp=0x201000
  uc.mem_write(gp,pack(720,720,738,779,480,489,489,524,524,4,3));uc.mem_write(sp,pack(end,gp,base));uc.reg_write(x.UC_X86_REG_ESP,sp)
  regs=bytearray([initial]*256);sel=[0];writes=[];indices=set()
  untouched=[0x100200,0x600800,0x600804,0x680500,0x680504,0x680508,0x68050c,0x680630,0x680880,0x68084c,0x6808c4,0x600100,0x600140,0x100,0x140]
  for off in untouched:uc.mem_write(base+off,pack(0x5a5a0000+initial))
  def access(uc,kind,address,size,value,_):
   off=address-base
   if kind==u.UC_MEM_WRITE:
    writes.append([off,size,value])
    if off==0x6013d4:assert size==1;sel[0]=value
    elif off==0x6013d5:assert size==1;regs[sel[0]]=value;indices.add(sel[0])
    else:assert size==4 and 0x680800<=off<=0x680838
   elif off==0x6013d5:assert size==1;uc.mem_write(address,bytes([regs[sel[0]]]))
   else:raise AssertionError(('unexpected GPU read',off,size))
  uc.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,access,None,base,base+0x7fffff)
  uc.emu_start(syms['SetGPURegister'],end,timeout=1000000,count=10000);assert uc.reg_read(x.UC_X86_REG_EIP)==end
  get=lambda off:struct.unpack('<I',uc.mem_read(base+off,4))[0]
  assert (get(0x680838)+1,get(0x680818)+1,8*(((regs[0x19]&0xe0)<<3)|regs[0x13]),regs[0x28]&15)==(720,480,2880,3)
  assert get(0x680824)==779 and get(0x680804)==524
  assert all(get(off)==0x5a5a0000+initial for off in untouched)
  assert regs[0x39]==initial and 0x39 not in indices
  r['cases'].append({'initial_crtc':initial,'written_crtc':sorted(indices),'final_crtc':[list(v) for v in enumerate(regs) if v[0] in indices],'interlace_byte_unchanged':initial,'mmio_writes':[v for v in writes if v[0]!=0x6013d4 and v[0]!=0x6013d5],'all_writes_sha256':hashlib.sha256(json.dumps(writes).encode()).hexdigest(),'clocks_framebuffer_output_and_interrupt_sentinels_unchanged':True})
 r['inherited_bits_in_written_crtc']={str(i):sorted({c['final_crtc'][j][1] for c in r['cases']}) for j,(i,v) in enumerate(r['cases'][0]['final_crtc']) if len({c['final_crtc'][j][1] for c in r['cases']})>1}
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS256 GPU geometry fixtures; inherited CRTC bits:',','.join(r['inherited_bits_in_written_crtc']))
