import difflib,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'hd-phase344';out=K/'probe';assert not out.exists();out.mkdir()
pins={}
for name in ['gdi-probe.c','text-cases.c','large_cases.c','large_oracle.h','build.py','review-build.py']:
    old=(P/name).read_text();s=old
    if name=='build.py':s=s.replace('/mnt/e/xwn344','/mnt/e/xwn348/probe')
    if name=='review-build.py':s=s.replace('ws=k.parents[1]','ws=k.parents[2]')
    if name=='large_cases.c':
        at='static BOOL lg_pixels('
        addition='''/* New348 coverage packets are outside the timed interval. */
static BOOL pc_capture(DWORD data[32]) {
 DWORD i;zero(data,128);
 if(ExtEscape(Screen,0x58574438,0,NULL,128,(LPSTR)data)!=1 ||
    data[0]!=0x50435758 || data[1]!=348 || data[2]!=128 || data[3]>1 || data[11])return FALSE;
 for(i=12;i<32;i++)if(data[i])return FALSE;
 return TRUE;
}
static void pc_emit(DWORD id,DWORD phase,const DWORD data[32]) {
 DWORD i;record("PRIMARY348_PACKET",id,phase,1);
 for(i=0;i<32;i++)record(phase?"PRIMARY348_AFTER":"PRIMARY348_BEFORE",id,i,data[i]);
}
'''
        assert s.count(at)==1;s=s.replace(at,addition+at)
        s=s.replace('DWORD phases[2][32];','DWORD phases[2][32],primary[2][32];')
        assert s.count('!lg_phase(phases[0])')==1 and s.count('!lg_phase(phases[1])')==1
        s=s.replace('!lg_phase(phases[0])','!lg_phase(phases[0])||!pc_capture(primary[0])')
        s=s.replace('!lg_phase(phases[1])','!lg_phase(phases[1])||!pc_capture(primary[1])')
        needle='lg_phase_emit(id,0,phases[0]);lg_phase_emit(id,1,phases[1]);'
        assert s.count(needle)==1;s=s.replace(needle,needle+'\n        pc_emit(id,0,primary[0]);pc_emit(id,1,primary[1]);')
    (out/name).write_text(s);pins[name]=dict(parent_sha256=hashlib.sha256((P/name).read_bytes()).hexdigest(),sha256=hashlib.sha256((out/name).read_bytes()).hexdigest())
    if old!=s:(out/(name+'.patch')).write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='344/'+name,tofile='348/probe/'+name)))
(out/'source-review.json').write_text(json.dumps(dict(inputs=pins,only_probe_change='Additional read-only348 before/after packets outside timing; original operations/oracles unchanged',runtime=False),indent=2)+'\n')
