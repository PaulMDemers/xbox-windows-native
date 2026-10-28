"""Prepare761 independent source, bounds and optical schema reviewers."""
from pathlib import Path
import json,re
k=Path(__file__).resolve().parent;old=k.parent/'native-crtc-gate759'
def ns(s,a,b):return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
oldoff='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5350,0x5378,0x5364,0x5370,0x5374'
newoff='0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5378,0x53a4,0x5390,0x539c,0x53a0'
s=ns((old/'source_review.py').read_text(),'759','761')
s=s.replace("'native-crtc-bit757'","'native-crtc-gate759'").replace("'crtc-display-gate758'","'crtc-display-end760'")
s=s.replace("'758','761'","'760','761'").replace("'761','757'","'761','759'").replace("'757','761'","'759','761'")
a=s.index(" if n=='bridge.S':");z=s.index('\n assert clean(a)',a)
s=s[:a]+" if n=='bridge.S':a=a.replace("+repr(oldoff)+','+repr(newoff)+')'+s[z:]
s=s.replace('==169','==189').replace('==159','==179').replace('==164','==176').replace('164*4','176*4')
s=s.replace('0x5390<0x5400','0x53c0<0x5400').replace('[0x5100,0x5390]','[0x5100,0x53c0]')
s=s.replace("'model_cases':169","'model_cases':189").replace("'integration_cases':159","'integration_cases':179").replace("'result_bytes':656","'result_bytes':704").replace("'result_end_offset':0x5390","'result_end_offset':0x53c0")
s=s.replace('[0,2,3,4,5,0x1f','[0,1,2,3,4,5,0x1f')
s=s.replace(" if c['name'] in ['c17-undo-read'", " if c['name'] in ['c1-undo-read','c1-drop-undo']:assert c['raw_result'][0]==0x76119 and c['raw_result'][169]==1 and c['raw_result'][101]==0\n if c['name'] in ['c17-undo-read'")
s=s.replace('probe_matches758','probe_matches760').replace('matches757','matches759')
s=s.replace('CR17 before/after/restored and eight aggregate masks exposed. Forward status, selectors, neighbor readbacks and individual prior restorations/H7/nativeCR0/3/4 unexposed.','CR01 before/after/restored and eight aggregate masks exposed. Second CR05 cleanup mask and forward status/selectors/neighbors/prior individual restorations/H7/nativeCR0/3/4 unexposed; final761 still requires all nine masks.')
s=s.replace('physical758 transaction and757 frontend','physical760 transaction and759 frontend').replace('CR17 recovery/report','CR01 recovery/report')
assert not (k/'source_review.py').exists();(k/'source_review.py').write_text(s,newline='\n')
off=[int(v,0) for v in newoff.split(',')]
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR00_cleanup_mask','CR02_cleanup_mask','CR03_cleanup_mask','CR17_cleanup_mask','CR01_cleanup_mask','CR01_before','CR01_after','CR01_restored']
schema={'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'CRTC_cleanup_mask':'bit0 CR04,bit1 CR05; full-byte own-value recovery','target_CR01':89,'limits':'Target59 is frozen source contract. Second CR05 cleanup mask, forward status, selectors, CPU, neighbors and individual prior restorations/H7 are not exposed. Eight of nine aggregate recovery masks and CR01 triplet exposed. Final761 requires forward success and all nine masks clear. No native disk persistence/full mode/Windows proof.'}
(k/'optical-schema001.json').write_text(json.dumps(schema,indent=2)+'\n',newline='\n')
s=ns((old/'review_prepare.py').read_text(),'759','761')
a=s.index('off=');b=s.index('checks=',a)
s=s[:a]+'off='+repr(off)+'\n'+"b=Path('C:/xwn761/host002/bridge.bin').read_bytes()\nassert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off\nassert load('optical-schema001.json')=="+repr(schema)+'\n'+s[b:]
s=s.replace("'result_bytes':656","'result_bytes':704").replace("'result_end':0x5390","'result_end':0x53c0").replace('CR17 bit7 clear after qualified prefix/H7/CR04/05/00/02/03 and second CR05','CR01 display end after qualified prefix/H7/CR04/05/00/02/03/secondCR05/CR17; secondCR05 mask not optically exposed')
(k/'review_prepare.py').write_text(s,newline='\n')
note=b'''# 761 PREPARING: native CR01 display-end and own recovery

Kernel760 CLOSED PASS pushed94d8f229. Fresh761 source-only760probe/model002 and
759frontend;176words704bytes end53c0 within initialized5400. Fresh validation
pending; no761build/stage/launch yet.13rows expose eight masks/CR01triplet;
secondCR05 mask omitted optically but all nine required by final success.
No hook/owned process/VM. Console last authenticated dashboard after760.
All760/prior CLOSED. NEXT outputs/native-crtc-end761/NEXT.md. Current watcher/
photo/reset required before native hold. No fullmode/Windows1.6 qualification.

'''
for n in ['CONTINUATION.md','STATUS.md']:
 p=k.parent/'engineering-notes'/n;p.write_bytes(note+p.read_bytes())
(k/'NEXT.md').write_text('''# Test761 preparation

Complete fresh ELF/CPU/integration/optical/source/nxdk/page/plan/link checks,
freeze exact source/index bytes, stage unique E application with readback and
commit/push. No native hold launch until current watch/photo/reset readiness.
One SITE request with20-second reply bound; never retry accepted/uncertain.
After photo preservation and user reset collect once/double-read and audit.
All760/prior runtimes CLOSED. No hook. SecondCR05 mask, forward status, CPU,
selectors, neighbors and prior individual recovery values are not exposed by
13rows. Final761 still requires all nine masks. No native disk/fullmode/Windows
proof. Later CR02 target59 write and CR17 enable remain separate operations.
''',newline='\n')
