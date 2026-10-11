"""Derive a channel-identification helper without changing the driver or its lifecycle calls."""
import pathlib,hashlib,json
k=pathlib.Path(__file__).resolve().parent
p=k.parent/'audio207/probe-installed.c';s=p.read_text()
s=s.replace('#include <mmsystem.h>','#include <mmsystem.h>\n#include "waveform.h"')
s=s.replace('static short Samples[48000*2*2];','static short Samples[CHANNEL001_FRAMES*2];')
a=s.index('    /* Different deterministic');b=s.index('    h.lpData=',a)
s=s[:a]+'''    unsigned mask = cycle % 3 + 1;
    rec("PHASE_MASK",cycle,mask);
    rec("PHASE_BEGIN_MS",cycle,GetTickCount());
    for(i=0;i<CHANNEL001_FRAMES;i++) {
        Samples[2*i]=channel001_sample(i,0,mask);
        Samples[2*i+1]=channel001_sample(i,1,mask);
    }
'''+s[b:]
s=s.replace('elapsed<1500','elapsed<2500').replace('pos.u.sample!=96000','pos.u.sample!=CHANNEL001_FRAMES')
s=s.replace('"AUDIO207_BEGIN"','"CHANNEL001_BEGIN"').replace('"AUDIO207_END",12','"CHANNEL001_END",6')
s=s.replace('i<12;i++){BOOL reset=(i%3)==1;','i<6;i++){BOOL reset=FALSE;')
assert 'i<12' not in s and 'Samples[2*i+1]=channel001_sample' in s
with (k/'probe.c').open('x') as f:f.write(s)
(k/'source-origin.json').write_text(json.dumps({'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'driver_changed':False,'schedule':[1,2,3,1,2,3],'mask_bits':'1 left, 2 right','frames_per_phase':144000,'tone_frames':96000,'silence_frames':48000},indent=2)+'\n')
