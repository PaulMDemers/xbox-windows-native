"""Only bounded scalar telemetry changes relative to exact compiled260."""
from pathlib import Path
def apply(root):
    path=root/'hw/xbox/nv2a/pgraph/gl/surface.c'
    text=path.read_text()
    old='''    if (site>=13 || qatomic_read(&surface257_count[site])>=257) return;
    unsigned index=qatomic_fetch_inc(&surface257_count[site]);
    if(index>=256) {
        if(index==256) trace_nv2a_lifecycle244(99,qemu_clock_get_ns(QEMU_CLOCK_REALTIME),qemu_get_thread_id(),site,index,0);
        return;
    }'''
    new='''    if (site>=13) return;
    unsigned limit=site==11 ? 4096 : 256;
    unsigned index=surface262_claim(&surface257_count[site],limit);
    if(index>=limit) {
        if(index==limit) trace_nv2a_lifecycle244(99,qemu_clock_get_ns(QEMU_CLOCK_REALTIME),qemu_get_thread_id(),site,index,0);
        return;
    }'''
    assert text.count(old)==1
    text=text.replace(old,new)
    anchor='static unsigned surface257_count[13];'
    assert text.count(anchor)==1
    text=text.replace(anchor,Path(__file__).with_name('telemetry-counter.c').read_text()+'\n'+anchor)
    path.write_text(text)
