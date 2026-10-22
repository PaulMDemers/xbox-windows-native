"""Pin local source observations; does not inspect a live console or closed runtime."""
import datetime,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];S=Path('C:/xwn651/source001')
out=K/'source-review002.json';assert not out.exists()
r=dict(passed=False,physical_access=False,scope='static source feasibility; no transport qualification',sources={},checks=[])
def save():out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
save()
try:
 build=json.loads((W/'outputs/readback651/build001.json').read_text())
 tree=subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C','/mnt/c/xwn651/source001','write-tree'],timeout=25,text=True).strip()
 assert tree==build['tree'];r['source_tree']=tree
 paths=['boot/BootResetAction.c','boot_xbe/xbeboot.S','drivers/ide/BootIde.c','drivers/pci/pci.c','drivers/video/xwn_hd_native.c']
 texts={}
 for n in paths:
  data=(S/n).read_bytes()
  indexed=subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C','/mnt/c/xwn651/source001','show',':'+n],timeout=25)
  assert data==indexed,n
  r['sources'][n]=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
  texts[n]=data.decode()
 boot=texts[paths[0]]
 assert boot.index('BootVgaInitializationKernelNG(')<boot.index('BootPciInterruptEnable();')<boot.index('BootStartUSB();')<boot.index('BootIdeInit();')
 r['checks'].append('video before interrupt enable, USB and IDE initialization')
 native=texts[paths[4]]
 assert hashlib.sha256((S/paths[4]).read_bytes()).hexdigest()==build['source_pins']['xwn_hd_native.c']
 assert native.index('result=xwn_hd_apply(')<native.index('capture651(&io,&XwnReadback651Post')<native.index('led651_show(')<native.index('if(result<0')<native.index('for(;;)')<native.index('return result;')
 r['checks'].append('post-result capture before LED/reset; failure cannot return to later IDE setup')
 ide=texts[paths[2]];write=ide[ide.index('int BootIdeWriteData('):ide.index('int BootIdeWriteAtapiData(')]
 assert 'n=BootIdeWaitDataReady(uIoBase);' in write and '//\tif(n) {' in write
 assert write.index('n=BootIdeWaitDataReady')<write.index('IoOutputWord(')<write.index('n=BootIdeWaitNotBusy')
 r['checks'].append('existing WriteData ignores its first data-ready failure; not admitted as backend')
 sector=ide[ide.index('int BootIdeWriteSector('):ide.index('int BootIdeBootSectorHddOrElTorito(')]
 assert 'tsaHarddiskInfo[nDriveIndex].m_fDriveExists' in sector
 r['checks'].append('existing WriteSector depends on initialized disk information')
 xbe=texts[paths[1]]
 assert 'cli;' in xbe and 'mov\tcr0, eax' in xbe and 'mov\tcr3, eax' in xbe
 r['checks'].append('native handoff changes CPU paging context; old kernel file calls not qualified here')
 serial=texts[paths[3]]
 assert 'while ((IoInputByte(SERIAL_PORT + SERIAL_LSR) & (1 << 5)) == 0);' in serial
 r['checks'].append('existing serial output wait unbounded; receiver also unestablished')
 for record in ['host001.json']:
  h=json.loads((K/record).read_text())
  for n,digest in h['source_pins'].items():assert hashlib.sha256((K/n).read_bytes()).hexdigest()==digest,n
 assert json.loads((K/'compiled001.json').read_text())['passed']
 r['checks'].append('host-tested source pins unchanged and linked i386 protocol tests pass')
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(passed=r['passed'],checks=len(r['checks']))))
