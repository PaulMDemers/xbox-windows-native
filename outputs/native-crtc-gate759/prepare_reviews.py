"""Create759 reviewers from retained source only; no closed runtime access."""
from pathlib import Path
import json,re
k=Path(__file__).resolve().parent;old=k.parent/'native-crtc-bit757'
def ns(s,a,b):
 return re.sub(r'(?<![0-9])'+a+r'(?![0-9])',b,re.sub(r'0x'+a+r'(?=[0-9a-f]*\b)','0x'+b,s))
s=ns((old/'source_review.py').read_text(),'757','759')
s=s.replace("'native-crtc-end755'","'native-crtc-bit757'").replace("'crtc-blank-bit756'","'crtc-display-gate758'")
s=s.replace("'756','759'","'758','759'").replace("'759','755'","'759','757'").replace("'755','759'","'757','759'")
s=s.replace('0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5314,0x5320,0x5324,0x5170','OLD_OFFSETS')
s=s.replace('0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5350,0x533c,0x5348,0x534c','0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5350,0x5378,0x5364,0x5370,0x5374')
s=s.replace('OLD_OFFSETS','0,0x8d4,0x5104,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5350,0x533c,0x5348,0x534c')
s=s.replace('==152','==169').replace('==142','==159').replace('==153','==164').replace('153*4','164*4').replace('0x5364','0x5390')
# Restore CR17 before offset in the literal map after result-end substitution.
s=s.replace('0x5378,0x5390,0x5370','0x5378,0x5364,0x5370')
s=s.replace("'model_cases':152","'model_cases':169").replace("'integration_cases':142","'integration_cases':159").replace("'result_bytes':612","'result_bytes':656")
s=s.replace(" if c['name'] in ['c5b-undo-read'", " if c['name'] in ['c17-undo-read','c17-drop-undo']:assert c['raw_result'][0]==0x75917 and c['raw_result'][158]==1 and c['raw_result'][101]==0\n if c['name'] in ['c5b-undo-read'")
s=s.replace('probe_matches756','probe_matches758').replace('matches755','matches757')
s=s.replace('Second CR05 before/after/intermediate undo and seven aggregate masks exposed. Selectors, final original CR05, neighbor readbacks and individual prior restorations/H7/nativeCR0/3/4 unexposed.','CR17 before/after/restored and eight aggregate masks exposed. Forward status, selectors, neighbor readbacks and individual prior restorations/H7/nativeCR0/3/4 unexposed.')
s=s.replace('Compare759 to physical756 transaction and755 frontend','Compare759 to physical758 transaction and757 frontend').replace('second CR05 recovery/report','CR17 recovery/report')
assert not (k/'source_review.py').exists();(k/'source_review.py').write_text(s,newline='\n')
off=[0,0x8d4,0x5178,0x5290,0x52b0,0x52e4,0x5304,0x5328,0x5350,0x5378,0x5364,0x5370,0x5374]
names=['signature','return_code','prefix_cleanup_mask','horizontal_cleanup_mask','CRTC_cleanup_mask','CR00_cleanup_mask','CR02_cleanup_mask','CR03_cleanup_mask','CR05_second_cleanup_mask','CR17_cleanup_mask','CR17_before','CR17_after','CR17_restored']
schema={'passed':True,'rows':13,'columns':32,'bit_order':'MSB left white1 black0 gray background','offsets':off,'names':names,'CRTC_cleanup_mask':'bit0 CR04,bit1 CR05; full-byte own-value recovery','target_CR17':99,'limits':'Target63 is frozen source contract. Forward status, selectors, CPU, neighbors and individual prior restorations/H7 are not exposed. Eight aggregate recovery masks and CR17 triplet exposed. Final759 requires both forward and recovery success; no raw forward-status observation. No native disk persistence/full mode/Windows proof.'}
assert not (k/'optical-schema001.json').exists();(k/'optical-schema001.json').write_text(json.dumps(schema,indent=2)+'\n',newline='\n')
s=ns((old/'review_prepare.py').read_text(),'757','759')
a=s.index('off=');b=s.index("checks=",a)
s=s[:a]+'off='+repr(off)+'\n'+"b=Path('C:/xwn759/host002/bridge.bin').read_bytes()\nassert list(struct.unpack_from('<13I',b,h['bridge_symbols']['report_offsets']))==off\nassert load('optical-schema001.json')=="+repr(schema)+'\n'+s[b:]
s=s.replace("'result_bytes':612","'result_bytes':656").replace('0x5364','0x5390').replace('Second CR05 bit7 after qualified prefix/H7/CR04/05/00/02/03','CR17 bit7 clear after qualified prefix/H7/CR04/05/00/02/03 and second CR05')
s=s.replace(",'preserved_failed_host':'host_build004.py -> host001 (Windows invocation; no compilation)'",'')
s=s.replace("['prepare.py','extend_integration.py']","['prepare.py','extend_integration.py','prepare_reviews.py']")
assert not (k/'review_prepare.py').exists();(k/'review_prepare.py').write_text(s,newline='\n')
note=b'''# 759 PREPARING: native CR17 clear and own recovery

Kernel758 CLOSED PASS, pushed8847e0ef. Native759 payload/host build,169 ELF
cases and12 fresh CPU fixtures PASS/allclosed. Integration and optical checks
running; no759 XBE build/stage/launch yet.164words656bytes end5390 within
existingzero5400.13rows expose eight masks and CR17 triplet; forwardstatus
explicitly omitted. No hook or owned VM; last console state authenticated
dashboard after758. Current native watch/photo/reset readiness needed later.
NEXT outputs/native-crtc-gate759/NEXT.md. No fullmode/Windows1.6 proof.

'''
for n in ['CONTINUATION.md','STATUS.md']:
 p=k.parent/'engineering-notes'/n;p.write_bytes(note+p.read_bytes())
(k/'NEXT.md').write_text('''# Test759 preparation

Complete fresh integration/optical/source/nxdk/page/plan/link checks, freeze exact
sources, review indexed bytes, stage unique E application with readback, then
commit/push. No launch until current watch/photo/reset readiness for native hold.
One SITE request with20-second reply bound; never retry accepted/uncertain launch.
After photo preservation and user reset, collect once and audit preparation.
All758/prior runtimes CLOSED. No hook; console last authenticated at dashboard.
Forwardstatus, CPU/selectors, neighbors and prior individual recovery values are
not exposed by13rows. No native disk/fullmode/Windows proof. CR01 remains next
source-ordered operation only after this counterpart qualifies.
''',newline='\n')
print('Created759 independent delta/freeze reviewers and preparation state')
