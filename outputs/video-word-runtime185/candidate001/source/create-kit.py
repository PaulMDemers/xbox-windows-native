"""Unique185 matched115 ordinary kit, settled181 parent and byte-exact guard."""
import ast,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];old=k.parent/'video-dib-runtime183';assert not (k/'Run.ps1').exists()
assert all(json.loads((old/n/'closure.json').read_text())['closed'] for n in ['control001','candidate001'])
names=['common.py','atomic_json.py','check-leases.ps1','audit.py','preflight.py','sample_analysis.py','supervise.py','inventory-devices.py','audit-package.py','Run.ps1','freeze.py','close-emulator.py','validate-inputs.py','prepare.py','review-build.py','review-pair.py']
for n in names:
 s=(old/n).read_text().replace('video-dib-runtime183','video-word-runtime185').replace('dib183','word185').replace('xwndb183','xwnws185').replace('video-dib-copy182','video-word-store184')
 s=s.replace('matched114','matched115').replace('Matched114','Matched115')
 s=s.replace('New183','New185').replace('Fresh183','Fresh185').replace('Closed183','Closed185').replace('183 inputs','185 inputs').replace('v6 ExtEscape','v7 ExtEscape')
 if n=='freeze.py':s=s.replace("build/'dib_plan.h',build/'plan-tests.c'","build/'row_store.h',build/'row-tests.c',build/'row-tests002.c'")
 if n=='sample_analysis.py':s=s.replace('v6 counters','v7 counters').replace("'6','256','128'","'7','256','128'")
 if n=='validate-inputs.py':s=s.replace("read(driver/'copy-review.json')","read(driver/'instruction-review.json')")
 if n=='review-pair.py':
  s=s.replace('candidate_hits=','candidate_fast_rows=').replace("v['hits']","v['fast_rows']")
  s=s.replace("timed_loops=sum(len(v['timed_loops'])","posttiming_checks=sum(v.get('posttiming_checks',0) for v in a['dib_samples']),timed_loops=sum(len(v['timed_loops'])")
 if n.endswith('.py'):ast.parse(s)
 (k/n).write_bytes(s.encode())
for n in ['runner.c','restart_gate.h','test-gate.c','xwnunused179.inf','sites.json']:shutil.copyfile(old/n,k/n)
(k/'artifacts').mkdir(exist_ok=False);shutil.copyfile(old/'artifacts/runner.exe',k/'artifacts/runner.exe')
s=(old/'gdi-probe.c').read_text().replace('PROBE_VERSION",6','PROBE_VERSION",7').replace('ProbeV6','ProbeV7').replace('bounded DIB copy114','scalar row stores115').replace('0x58574434','0x58574435').replace('0x42445758','0x57525758').replace('data[1]!=114','data[1]!=115').replace('for(i=14;i<32','for(i=11;i<32')
s=s.replace('before[3]&&(stage==0||stage==1)','before[3]')
s=s.replace('"FAIL_DIB_FAST_COVERAGE"','"FAIL_ROW_COVERAGE"').replace('"FAIL_DIB_TIMED_COVERAGE"','"FAIL_ROW_TIMED_COVERAGE"')
marker='    if(!snapshot(kind,1))++Failures;';assert s.count(marker)==1
s=s.replace(marker,marker+'''
    if(kind<3) {
        DWORD i,wanted;BOOL exact=TRUE;
        if(kind<2&&!blit(kind+100,Check,0,0,Screen,0,0))exact=FALSE;
        for(i=0;i<W*H&&exact;i++) {
            wanted=kind==0?(((count-1)&1)?0:0xffffff):(Input[i]&0xffffff);
            if((Pixels[i]&0xffffff)!=wanted){record("MISMATCH_POST_kind_x_y",kind,i%W,i/W);record("MISMATCH_POST_expected_actual",wanted,Pixels[i]&0xffffff,0);exact=FALSE;}
        }
        record("POST_TIMING_kind_pass",kind,exact,0);if(!exact)++Failures;
    }''')
(k/'gdi-probe.c').write_bytes(s.encode())
s=(old/'Build-Probe002.ps1').read_text().replace('Probe002','Probe001').replace('probe-build002','probe-build001');(k/'Build-Probe001.ps1').write_bytes(s.encode())
(ws/'.gitattributes').write_bytes((ws/'.gitattributes').read_bytes()+b'\n/outputs/video-word-runtime185/** -text whitespace=cr-at-eol\n')
print('Unique185 scripts/probev7 created; no fixture or guest action')
