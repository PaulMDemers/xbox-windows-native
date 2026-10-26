"""Fresh instruction-level fixtures of compiled native binding; modeled ports."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn687/build001')
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
out=K/'cpu001.json';assert not out.exists()
build=json.loads((K/'build001.json').read_text());assert build['passed']
for n,h in build['files'].items():assert hashlib.sha256((P/n).read_bytes()).hexdigest()==h
blob=(P/'native.bin').read_bytes();syms={a[2]:int(a[0],16) for line in (P/'symbols.stdout').read_text().splitlines() if len(a:=line.split())==3}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
r={'passed':False,'physical_access':False,'image_sha256':hashlib.sha256(blob).hexdigest(),'cases':[],
   'scope':'actual GCC12 freestanding32-bit code with modeled SMBus/PM ports; no encoder or native startup qualification'}
def run(name,fn,args,expected,entry=0,status=0x10,length=4,if_set=False,clock=None,expected_writes=None):
    uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);uc.mem_map(0x100000,0x10000);uc.mem_write(0x100000,blob)
    uc.mem_map(0x200000,0x10000);end=0x10ff00;sp=0x208000;value_ptr=0x204000
    uc.mem_write(value_ptr,pack(0xdeadbeef,0xdeadbeef,0xdeadbeef,0xdeadbeef))
    uc.mem_write(sp,pack(end,*args));uc.reg_write(x.UC_X86_REG_ESP,sp)
    uc.reg_write(x.UC_X86_REG_EFLAGS,0x202 if if_set else 2)
    reads=[];writes=[];data=[0x12,0x34,0x56,0x78];counter=[0]
    def pin(uc,port,width,_):
        if port==0x8008:
            assert width==4 and clock is not None
            start,step,mask=clock;v=(start+counter[0]*step)&mask;counter[0]+=1
        elif (port,width)==(0xc000,2):v=entry
        elif (port,width)==(0xc000,1):v=status
        elif (port,width)==(0xc006,2):v=length
        elif (port,width)==(0xc006,1):v=8
        elif (port,width)==(0xc009,1):v=data.pop(0)
        else:raise AssertionError(('unexpected port read',hex(port),width))
        reads.append([port,width,v]);return v
    def pout(uc,port,width,value,_):writes.append([port,width,value])
    uc.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
    uc.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
    uc.emu_start(syms[fn],end,timeout=10000000,count=10000000)
    actual=uc.reg_read(x.UC_X86_REG_EAX);assert uc.reg_read(x.UC_X86_REG_EIP)==end
    assert actual==expected,(name,actual,expected)
    assert bool(uc.reg_read(x.UC_X86_REG_EFLAGS)&0x200)==if_set
    if expected_writes is not None:assert writes==expected_writes,(name,writes)
    output=list(struct.unpack('<IIII',uc.mem_read(value_ptr,16)))
    if fn=='native_read':assert output[0]==(0x78563412 if expected==0 else 0xdeadbeef)
    if fn=='native_config_read':assert output[0]==(0xdeadbe08 if expected==0 else 0xdeadbeef)
    if fn=='native_delay' and expected==0:assert 1688<=output[2]<=33750 and output[3]==counter[0]
    if fn=='native_delay' and expected==2:assert counter[0]==100001 and output[3]==100001
    if if_set or (fn=='native_delay' and expected==1):assert not reads and not writes
    if fn!='native_delay' and expected==4:assert len(reads)==100001
    r['cases'].append({'name':name,'return':actual,'read_count':len(reads),'read_prefix':reads[:8],
       'read_suffix':reads[-3:],'read_sha256':hashlib.sha256(json.dumps(reads).encode()).hexdigest(),
       'writes':writes,'output':output,'IF_unchanged':True})
try:
    read_head=[[0xc004,1,0xe1],[0xc008,1,4],[0xc002,1,0x0d]]
    run('block_read','native_read',[4,0x204000],0,expected_writes=read_head+[[0xc000,2,0x10]])
    write_head=[[0xc004,1,0xe0],[0xc008,1,7]]+[[0xc009,1,v] for v in [0x12,0x34,0x56,0x78]]+[[0xc006,2,4],[0xc002,1,0x1d]]
    run('block_write','native_write',[7,0x78563412],0,expected_writes=write_head+[[0xc000,2,0x10]])
    for fn,args in [('native_read',[4,0x204000]),('native_write',[4,0])]:
        run(fn+'_IF_refusal',fn,args,1001,if_set=True,expected_writes=[])
        run(fn+'_busy',fn,args,2,entry=0x800,expected_writes=[])
        run(fn+'_dirty',fn,args,3,entry=0x10,expected_writes=[])
    run('combined_error','native_read',[4,0x204000],5,status=0x36,expected_writes=read_head+[[0xc000,2,0x36]])
    run('short_read','native_read',[4,0x204000],6,length=3,expected_writes=read_head+[[0xc000,2,0x10]])
    run('read_timeout','native_read',[4,0x204000],4,status=0,expected_writes=read_head)
    run('write_timeout','native_write',[7,0x78563412],4,status=0,expected_writes=write_head)
    run('null_read','native_read',[4,0],1,expected_writes=[])
    for step in [1,2,7,101,1687,1688,1689]:
        for start in [0,0xffffffd0]:
            run(f'delay_{step}_{start}','native_delay',[0x204000,1],0,clock=(start,step,0xffffffff),expected_writes=[])
    run('clock_stalled','native_delay',[0x204000,1],2,clock=(123,0,0xffffffff),expected_writes=[])
    for name,clock in [('backwards',(100,-1,0xffffffff)),('24bit_wrap',(0xfffff0,16,0xffffff)),('large_gap',(0,33751,0xffffffff))]:
        run(name,'native_delay',[0x204000,1],3,clock=clock,expected_writes=[])
    run('clock_unqualified','native_delay',[0x204000,0],1,expected_writes=[])
    run('delay_IF_refusal','native_delay',[0x204000,1],1001,if_set=True,expected_writes=[])
    for address,reg in [(0x10,4)]+[(0x54,v) for v in [0x58,0x59,0x5a,0x5b,0x96]]:
        head=[[0xc004,1,(address<<1)|1],[0xc008,1,reg],[0xc002,1,0x0a]]
        run(f'config_{address}_{reg}','native_config_read',[address,reg,0x204000],0,expected_writes=head+[[0xc000,2,0x10]])
    head=[[0xc004,1,0xa9],[0xc008,1,0x96],[0xc002,1,0x0a]]
    run('config_error','native_config_read',[0x54,0x96,0x204000],5,status=0x36,expected_writes=head+[[0xc000,2,0x36]])
    run('config_timeout','native_config_read',[0x54,0x96,0x204000],4,status=0,expected_writes=head)
    run('config_dirty','native_config_read',[0x54,0x96,0x204000],3,entry=0x10,expected_writes=[])
    run('config_busy','native_config_read',[0x54,0x96,0x204000],2,entry=0x800,expected_writes=[])
    run('config_IF','native_config_read',[0x54,0x96,0x204000],1001,if_set=True,expected_writes=[])
    for address,reg in [(0x54,0),(0x70,0),(0x10,2),(0x54,0x97)]:
        run(f'config_refused_{address}_{reg}','native_config_read',[address,reg,0x204000],1,expected_writes=[])
    r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'compiled32-bit cases; no physical I/O')
