"""Summarize retained physical samples without assuming QPC is independent."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent
def summarize(d):
    assert d['tool']=='xwn-video-clock684' and d['complete'] and d['acquisition_return']
    a=d['spaced_100ms'];b=d['burst'];assert len(a)==len(b)==65
    assert d['columns']==['pm_before','qpc','interrupt_100ns','rdtsc','pm_after']
    assert all(len(v)==5 and all(isinstance(x,int) and x>=0 for x in v) for v in a+b)
    assert all(v[0]<=0xffffffff and v[4]<=0xffffffff for v in a+b)
    elapsed=(a[-1][2]-a[0][2])/1e7;assert elapsed>0
    pm=(a[-1][0]-a[0][0])&0xffffffff
    qpc=a[-1][1]-a[0][1];tsc=a[-1][3]-a[0][3]
    assert d['qpc_frequency']>0
    status=lambda x:{'raw':x,'busy':bool(x&0x800),'terminal_mask':x&0x36}
    return {
        'interrupt_elapsed_seconds':elapsed,
        'raw_pm_delta_mod32':pm,'raw_pm_ticks_per_interrupt_second':pm/elapsed,
        'qpc_elapsed_seconds':qpc/d['qpc_frequency'],
        'tsc_ticks_per_interrupt_second':tsc/elapsed,
        'raw_pm_high_byte_observed':any(v[0]>0xffffff or v[4]>0xffffff for v in a+b),
        'spaced_pm_descents':sum(a[i][0]<a[i-1][0] for i in range(1,len(a))),
        'largest_spaced_pm_delta_mod32':max((a[i][0]-a[i-1][0])&0xffffffff for i in range(1,len(a))),
        'largest_bracket_ticks_mod32':max((v[4]-v[0])&0xffffffff for v in a+b),
        'burst_pm_delta_mod32':(b[-1][4]-b[0][0])&0xffffffff,
        'smbus_entry':status(d['smbus_entry']),'smbus_end':status(d['smbus_end']),
        'limitations':['QPC and port timer independence is not established.',
          'Interrupt clock includes scheduling; this is a rate cross-check, not calibrated microsecond accuracy.',
          'RDTSC reads are not serializing; no instruction timing claim.',
          'Kernel-context bus status does not establish native bus ownership or permission to clear pending status.',
          'No encoder transaction, native delay, native mode set or Windows boot was tested.']}
if __name__=='__main__':
    out=K/'analysis001.json';assert not out.exists()
    c=json.loads((K/'collection001.json').read_text());assert c['completed']
    data=[x['data'] for x in c['reports'].values() if x['data']['phase']=='restart_requested']
    assert len(data)==1
    r=summarize(data[0]);out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
