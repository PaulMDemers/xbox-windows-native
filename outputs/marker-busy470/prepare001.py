"""New host-only busy predicate; preserve every old marker and result."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'entry-marker465'
assert not (K/'marker.S').exists()
r=json.loads((K.parent/'physical-status469/status-source-review.json').read_text());assert r['physical_status']==0x808
s=(P/'marker.S').read_text();assert s.count('test eax, 0xfffff7ef')==2 and s.count('test eax, 0x800')==2
s=s.replace('test eax, 0xfffff7ef','test eax, 0xfffff7e7').replace('test eax, 0x800','test eax, 0x808')
assert s.replace('test eax, 0xfffff7e7','test eax, 0xfffff7ef').replace('test eax, 0x808','test eax, 0x800')==(P/'marker.S').read_text()
(K/'marker.S').write_text(s);(K/'invoke.S').write_bytes((P/'invoke.S').read_bytes())
s=(P/'test.c').read_text()
def sub(a,b):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,b)
sub('        idle_reads++;','''        idle_reads++;
        if(mode==38)return 0x8;
        if(mode==40)return 0x808;
        if(mode==47)return 0x8;
        if(idle_reads<4) {
            if(mode==32)return 0x8;
            if(mode==36)return 0x808;
            if(mode==37)return 0x818;
        }''')
sub('    completion_reads++;','''    completion_reads++;
    if(mode==39)return 0x8;
    if(mode==41)return 0x818;
    if(mode>=42 && mode<=46) {
        static const unsigned errors[]={0x809,0x80a,0x80c,0x828,0x848};
        return errors[mode-42];
    }
    if(mode==48)return 0x808;
    if(completion_reads<4) {
        if(mode==33)return 0x8;
        if(mode==32 || mode==34 || mode==49 || mode==50)return 0x808;
        if(mode==35)return 0x818;
    }''')
sub('    writes++;assert(cli_seen && !active);','    writes++;assert(cli_seen && !active && !(r[8]&0x808));')
sub('    if(tscs==1)return clock_value=1000;','''    if(tscs==1)return clock_value=1000;
    if(mode==47 && tscs>=4)return 64001000;
    if(mode==48 && completion_reads>=2)return 64001000;''')
sub('expected[32]={1,1,3,4,5,5,3,4,5,6,6,6,6,7,3,4,5,5,5,1,1,5,1,2,2,2,2,2,2,7,6,1}',
    'expected[51]={1,1,3,4,5,5,3,4,5,6,6,6,6,7,3,4,5,5,5,1,1,5,1,2,2,2,2,2,2,7,6,1,1,1,1,1,1,1,3,4,3,4,5,5,5,5,5,6,6,1,1}')
s=s.replace('mode<32','mode<51').replace('stage=mode==22||mode==28?2:1','stage=mode==22||mode==28||mode==49?2:1').replace('PASS 32 actual','PASS 51 actual')
sub('        char name[40];','''        if(mode==38 || mode==40)assert(!writes && r[9]==4096);
        if(mode==39 || mode==41)assert(writes==4 && r[9]==4096 && r[6]==0);
        if(mode>=42 && mode<=46)assert(r[5]==5 && writes==4 && !r[6]);
        if(mode==47)assert(!writes && r[5]==6);
        if(mode==48)assert(writes==4 && r[5]==6);
        char name[40];''')
(K/'test.c').write_text(s)
s=(P/'host001.py').read_text().replace('xwn465','xwn470').replace('PASS 32','PASS 51').replace('actual_cases=32,immutable_repeat_cases=32','actual_cases=51,immutable_repeat_cases=51')
(K/'host001.py').write_text(s)
(K/'Host001.ps1').write_text((P/'Host001.ps1').read_text().replace('entry-marker465','marker-busy470'))
