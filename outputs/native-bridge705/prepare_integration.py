"""Generate a NEW705 model harness from retained704 source, never run its fixture."""
from pathlib import Path
import hashlib
K=Path(__file__).resolve().parent; W=K.parents[1]
p=W/'outputs/xcal-transaction704/cpu005.py'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='19f7a737c39c44a3ca9c60842adfe3c486541145ad6ceae1465520d3b30e6d7c'
s=p.read_text();s=s[:s.index('\ntry:\n from relocate')]
def rep(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
rep('P=Path(\'C:/xwn704/build004\')','P=Path(\'C:/xwn705/build002\')')
rep("OUT=K/'cpu005.json'","OUT=K/'integration001.json'")
rep("(K/'build004.json')","(K/'build002.json')")
rep("blob=(P/'native.bin').read_bytes()\nsyms={a[2]:int(a[0],16) for l in (P/'symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}","page=(P/'dual/page.bin').read_bytes(); syms=b['bridge_symbols']; blob=page[4096:4096+9916]")
rep('CODE=0x100000;BASE=0xfd000000;FB=0x03c5c000;ALLOC=3686400;RP=0x201000;OP=0x202000;SP=0x208000;END=0x10ff00',
 'LOAD=0x1ef0000;CODE=LOAD+4096;BASE=0xfd000000;FB=0x3000000;ALLOC=3686400;RP=LOAD+0x5000;OP=LOAD+0x5100;SP=LOAD+0x8000;END=LOAD+syms["bridge_hold"]')
rep('DEFAULT=[0x4000000,0x3c5c000,','DEFAULT=[0x4000000,FB,')
rep('drop_phase=None,high_alias=False):','drop_phase=None,high_alias=False,pci_bad=None,refusal=None):')
rep('c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(CODE,0x10000);c.mem_write(CODE,blob)\n c.mem_map(0x200000,0x10000);',
 'c=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32);c.mem_map(LOAD-4096,40960);c.mem_write(LOAD-4096,b"G"*40960);c.mem_write(LOAD,page)\n ')
rep("c.mem_write(RP,pack(*req));c.mem_write(OP-16,b'X'*(160+32))\n c.mem_write(SP,pack(END,0 if null=='req' else RP,0 if null=='gpu' else BASE,\n                    0 if null=='fb' else FB+0x80000000 if high_alias else FB+4096 if alias_bad else FB,0 if null=='out' else OP))\n c.reg_write(x.UC_X86_REG_ESP,SP);c.reg_write(x.UC_X86_REG_EFLAGS,flags)",
 '''c.mem_write(RP,pack(*req))
 # Explicitly initialized post-transition model. This does NOT prove paging,
 # cache behavior or inherited descriptors; separate diskless CPU tests do that.
 data=bytearray(c.mem_read(LOAD,0x6000));total=sum(struct.unpack_from('<I',data,i)[0] for i in range(0,0x6000,4) if i!=0x854 and not 0x880<=i<0x900)&0xffffffff
 c.mem_write(LOAD+0x854,pack(total)); initial_page=bytes(c.mem_read(LOAD,32768))
 c.reg_write(x.UC_X86_REG_GDTR,(0,LOAD+0x800,31,0))
 c.reg_write(x.UC_X86_REG_CR0,0x40000011)
 for reg,val in [(x.UC_X86_REG_CS,0x10),(x.UC_X86_REG_DS,0x18),(x.UC_X86_REG_ES,0x18),(x.UC_X86_REG_SS,0x18)]:c.reg_write(reg,val)
 c.reg_write(x.UC_X86_REG_EBP,LOAD);c.reg_write(x.UC_X86_REG_ESP,SP);c.reg_write(x.UC_X86_REG_EFLAGS,flags)
 pci={0x80010000:0x02a010de,0x80010004:2,0x80010010:0xfd000000,
      0x80000900:0x01b410de,0x80000904:1,0x80000914:0xc001,
      0x80000800:0x01b210de,0x80000804:1,0x80000810:0x8001,0x80000884:0}
 if pci_bad is not None:pci[pci_bad[0]]=pci_bad[1]
 pci_state={'selector':0x12345678,'trace':[]}
''')
rep("  reads+=1\n  if port==0x8008:","""  if port in (0xcf8,0xcfc):
   assert width==4
   val=pci_state['selector'] if port==0xcf8 else pci[pci_state['selector']]
   pci_state['trace'].append(['in',port,width,val]);return val
  reads+=1
  if port==0x8008:""")
rep('  ph=phase();ports.append([ph,port,width,v])',"""  if port==0xcf8:
   assert width==4;pci_state['selector']=v;pci_state['trace'].append(['out',port,width,v]);return
  ph=phase();ports.append([ph,port,width,v])""")
rep(" c.emu_start(syms['native_transaction704'],END,timeout=10000000,count=50000000)"," c.emu_start(LOAD+syms['bridge_post'],END,timeout=10000000,count=50000000)")
rep(" ret=c.reg_read(x.UC_X86_REG_EAX);assert ret==expected,(label,ret,expected,phase())", """ assert pci_state['selector']==0x12345678,'CF8 not restored'
 assert len(pci_state['trace'])==22,'complete ten-function capture plus save/restore'
 assert c.mem_read(LOAD-4096,4096)==b'G'*4096 and c.mem_read(LOAD+32768,4096)==b'G'*4096
 final_page=bytes(c.mem_read(LOAD,32768))
 for begin,end in [(0,0x880),(0x900,0x5100),(0x51a0,0x6000)]:assert final_page[begin:end]==initial_page[begin:end],(label,begin,end)
 assert c.reg_read(x.UC_X86_REG_ESP)==SP,'cdecl cleanup/stack not restored'
 if refusal is not None:
  assert not writes and not ports and not reads
  assert struct.unpack_from('<I',final_page,0x880)[0]==2
  assert struct.unpack_from('<I',final_page,0x8d0)[0]==refusal
  assert c.mem_read(FB,ALLOC)==b'Z'*ALLOC
  R['cases'].append({'name':label,'PCI_refusal':refusal,'no_device_transaction':True,'CF8_restored':True,'guards_unchanged':True});return
 assert struct.unpack_from('<I',final_page,0x880)[0]==4
 ret=struct.unpack_from('<I',final_page,0x8d4)[0];assert ret==expected,(label,ret,expected,phase())""")
rep(" assert c.mem_read(OP-16,16)==b'X'*16 and c.mem_read(OP+160,16)==b'X'*16,label\n",'')
rep(" 'IF_and_protected_state_unchanged':True,'guards_unchanged':True,'selectors_restored':True})", " 'IF_and_protected_state_unchanged':True,'guards_unchanged':True,'selectors_restored':True,\n  'bridge_phase':4,'CF8_restored':True,'stack_restored':True,'page_sha256':sha(initial_page)})")
s='''"""NEW705 post-transition model integration. Exact bridge/page/payload bytes.
Initialized CPU context and modeled devices are not physical transition proof.
Derived from retained704 cpu005 model source, not its closed runtime.
"""\n'''+s[s.index('from pathlib'):]
s+='''
try:
 for name in ('dual','relocated'):
  page=(P/name/'page.bin').read_bytes();LOAD=struct.unpack_from('<I',page,0x844)[0];CODE=LOAD+4096
  RP=LOAD+0x5000;OP=LOAD+0x5100;SP=LOAD+0x8000;END=LOAD+syms['bridge_hold'];blob=page[4096:4096+9916]
  run(name+'-complete',ext_lock=True)
  run(name+'-encoder-error',fail_bus=147,bus_kind='error',expected=10)
  run(name+'-locked-baseline',pre=('cr',0x11,0x80),expected=5)
  run(name+'-blank-failure',drop=('sq',1),expected=6)
  run(name+'-enable-failure',enable_drop=True,expected=14)
  run(name+'-settle-failure',fail_delay=144,delay_kind='backwards',expected=13)
  for addr,value,code in [(0x80010000,0,1),(0x80010004,0,1),(0x80010010,0xfc000000,1),
       (0x80000900,0,2),(0x80000904,0,2),(0x80000914,0xd001,2),
       (0x80000800,0,3),(0x80000804,0,3),(0x80000810,0x9001,3)]:
   run(name+'-PCI-'+hex(addr),pci_bad=(addr,value),refusal=code)
 R['passed']=True
except BaseException as e:R['failure']=repr(e);raise
finally:
 R['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 OUT.write_text(json.dumps(R,indent=2)+'\\n',encoding='utf8')
print('PASS',len(R['cases']),'705 bridge/transaction integration cases; host models only')
'''
out=K/'integration001.py';assert not out.exists();out.write_text(s)
