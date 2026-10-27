"""Read retained source/capture evidence locally, never recollect a closed runtime."""
import ast,datetime,hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn730')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
out=K/'audit001.json';assert not out.exists()
r={'passed':False,'physical_access':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'captures':[],'local_inputs':{}}
try:
 for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
 for n in ['build001.json','model001.json']:assert read(K/n)['passed']
 refs=read(P/'references001/manifest.json');pins=read(P/'references001/pins.json')
 for n,v in refs['files'].items():assert sha(P/'references001'/n)==v['sha256']
 assert all(v['matches_download'] for v in pins['pins'])
 (K/'references001.json').write_text(json.dumps({'downloads':refs,'commit_pins':pins,'private_directory':str(P/'references001'),'initial_browser_limitations':['Some raw-source browser requests returned429 before later successful retrieval.','Guessed envytools nv_crtc.xml path returned404; not used.'],'not_inferred':'No full NV2A CR22 write/read specification or CR33 writable mask is established.'},indent=2)+'\n')
 nv=(P/'references001/envy-nv_vga.xml').read_text()
 assert '<reg8 offset="0x22" name="MEM_LATCH"/>' in nv
 n=(P/'references001/linux-nvreg.h').read_text()
 assert re.search(r'NV_CIO_CRE_LCD__INDEX\s+0x33',n) and re.search(r'NV_CIO_CRE_LCD_ROUTE_MASK\s+0x3b',n)
 bochs=(P/'references001/bochs-vgacore.cc').read_text()
 assert 's.CRTC.address == 0x22' in bochs and 's.graphics_ctrl.latch[BX_VGA_THIS s.graphics_ctrl.read_map_select]' in bochs
 tx=W/'outputs/xcal-transaction704/transaction003.c';assert sha(tx)=='6336794d817f0b801db939b2611c1832736acad598e71437f9ca87bc797a345b'
 oldmodel=W/'outputs/xcal-transaction704/cpu005.py'
 assert "banks[key[0]][key[1]]=v" in oldmodel.read_text() and "val=banks[key[0]][key[1]]" in oldmodel.read_text()
 for p in [tx,oldmodel,W/'src/boot/xromwell/drivers/video/BootVgaInitialization.c']:
  r['local_inputs'][str(p.relative_to(W))]=sha(p)
 for kit,private,names,field in [('kernel-mode722','C:/xwn722',['xwn-mode722-02.json','xwn-mode722-05.json','xwn-mode722-08.json'],'crtc'),('kernel-samples729','C:/xwn729',['xwn-mode729-03.json'],'crtc_kernel_reads')]:
  root=W/'outputs'/kit;assert read(root/'audit001.json')['passed']
  col=read(root/'collection001.json')
  r['local_inputs'][str((root/'collection001.json').relative_to(W))]=sha(root/'collection001.json')
  r['local_inputs'][str((root/'audit001.json').relative_to(W))]=sha(root/'audit001.json')
  for name in names:
   item=col['reports'][name];raw=Path(private)/'collection001'/name
   assert sha(raw)==item['sha256'] and read(raw)==item['data']
   d=item['data'];cr=dict(d[field]);assert cr[0x22]==0xfe and cr[0x33]==0x11
   r['captures'].append({'kit':kit,'report':name,'sha256':item['sha256'],'phase':d['phase'],'sdk_mode':d.get('sdk_mode'),'CR22':cr[0x22],'CR33':cr[0x33],'meaning':'Retained complete kernel mode; NOT original704 phase4 post-write evidence.'})
 r['unchanged_driver']=True;r['old_model_assumption']='Default indexed CRTC writes store a byte and subsequent reads return it, including CR22; this is not a physical access specification.'
 r['limitations']=['No new physical result or firmware trace.','CapturedFE does not establish CR22 post-write value in708/709.','CR1b or earlier MMIO failures can short-circuit before CR22 is read.','A simulatedFF latch passes even if the modeledCR22 write is ignored.','No inferred writable mask, omitted write, changed guard or modesetting patch.']
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS730 primary-source pins and four retained capture identities')
