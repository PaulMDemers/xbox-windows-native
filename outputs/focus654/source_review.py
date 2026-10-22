"""Source-only transport-boundary review; no live/closed runtime access."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn651/source001')
out=K/'source-review001.json';assert not out.exists()
r=dict(passed=False,physical_access=False,checks=[],sources={},source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 tree=subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C','/mnt/c/xwn651/source001','write-tree'],text=True,timeout=25).strip()
 assert tree=='2fda813f3b8109dfc6b70f6d37e21d2cf9a66d55';r['tree']=tree
 names=['boot/BootResetAction.c','drivers/video/xwn_hd_native.c','drivers/video/BootVgaInitialization.c',
        'lib/misc/BootLibrary.c','drivers/ide/BootIde.c','fs/fatx/BootFATX.h','fs/fatx/BootFATX.c',
        'drivers/pci/pci.c','boot/LoadReactOS.c']
 texts={}
 for n in names:
  b=(P/n).read_bytes()
  assert b==subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C','/mnt/c/xwn651/source001','show',':'+n],timeout=25)
  r['sources'][n]=hashlib.sha256(b).hexdigest();texts[n]=b.decode()
 def check(name,file,*anchors):
  s=texts[file];positions=[s.index(a) for a in anchors]
  assert positions==sorted(positions),name
  r['checks'].append(dict(finding=name,file=file,lines=[s.count('\n',0,p)+1 for p in positions]))
 check('display precedes STI, USB, IDE and loader',names[0],
       'BootVgaInitializationKernelNG(', 'BootPciInterruptEnable();', 'BootStartUSB();', 'BootIdeInit();','BootFromDevice(&entry);')
 check('pre/post capture precedes diagnostic; failure resets and halts before return',names[1],
       'capture651(&io,&XwnReadback651Pre','result=xwn_hd_apply(',
       'capture651(&io,&XwnReadback651Post','XwnDiag651Status=led651_show(',
       'if(result<0','xwn_hd_smb_write(&io,0x10,0x02,0x01)','for(;;)','return result;')
 check('success wrapper performs further video writes before returning to boot',names[2],
       'if (XwnHdTry720(', 'NVVertIntrEnabled(&riva,0);','NVSetFBStart(&riva,0,pvmode->m_dwFrameBufferStart);')
 check('interrupt enable helper executes STI',names[3],'void BootPciInterruptEnable()', '"sti"')
 check('IDE initialization changes bus-master state and initializes drives',names[4],
       'int BootIdeInit(void)', 'IoOutputByte(0xff60+0, 0x00)', 'IoOutputByte(0xff60+2, 0x62)',
       'BootIdeDriveInit(IDE_BASE1, 0);', 'BootIdeDriveInit(IDE_BASE1, 1);')
 assert 'BootIdeWriteSector' not in texts[names[6]] and 'IoOutput' not in texts[names[6]]
 assert 'Write' not in texts[names[5]]
 r['checks'].append(dict(finding='Inspected FATX facade exposes file loading; no file-write API or direct sector-write call found',files=names[5:7]))
 check('existing serial sender can wait forever',names[7],
       'int serial_putchar(int ch)','while ((IoInputByte(SERIAL_PORT + SERIAL_LSR) & (1 << 5)) == 0);')
 check('loader disables interrupts later but then changes CPU/memory and moves image',names[8],
       'BootStopUSB();','BootIdeSetTransferMode(0,', 'asm volatile ("cli\\n");',
       'memset((void *)IDT_LOC','memcpy((u8 *)mbHeader->load_addr,')
 for symbol in ('XwnReadback651Pre','XwnReadback651Post','XwnTrace649'):
  assert symbol not in texts[names[8]]
 r['checks'].append(dict(finding='Inspected loader has no explicit651 snapshot handoff; RAM durability must not be assumed',file=names[8]))
 assert 'c->io.flags(c->io.opaque)&0x200u' in (W/'outputs/pio653/pio.c').read_text()
 r['checks'].append(dict(finding='PIO653 rejects IF set; cannot directly bind after normal STI without a design change'))
 r['decision']='Do not integrate early/deferred PIO. Use one post-result comparison indication with unchanged capture/apply/reset path; it reports a masked subset only, not full snapshots.'
 r['initial_search_failure']='PowerShell did not expand wildcard path arguments in one rg query (OS error123); repeated using explicit directories. No source or runtime changed.'
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(passed=r['passed'],checks=len(r['checks']))))
