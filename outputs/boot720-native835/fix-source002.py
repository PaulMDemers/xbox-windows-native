"""Preserve compile001 failure; add missing forward declaration only."""
import difflib,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;B=Path('/home/paul/xbox-windows-native/boot720835-source001');p=B/'reactos/boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c'
assert not (K/'source002.json').exists()
r=json.loads((K/'source001.json').read_text());r['prior_failed_build']='chain001.json'
before=p.read_text();a='VOID\nXboxMemInit(VOID)';assert before.count(a)==1
after=before.replace(a,'memory_map_t *XboxGetMultibootMemoryMap(INT *Count);\n\n'+a);p.write_text(after)
(K/'reactos002.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),'a/boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c','b/boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c')))
r['changes']['reactos/boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c']['after']=hashlib.sha256(p.read_bytes()).hexdigest()
subprocess.run(['git','-C',str(B/'reactos'),'add','-f','.'],check=True)
r['trees']['reactos']=subprocess.check_output(['git','-C',str(B/'reactos'),'write-tree'],text=True).strip()
(K/'source002.json').write_text(json.dumps(r,indent=2)+'\n')
t=(K/'build-chain.py').read_text().replace('chain001','chain002').replace('source001.json','source002.json')
(K/'build-chain002.py').write_text(t)
