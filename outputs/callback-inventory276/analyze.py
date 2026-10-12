"""Correlate refused CPU inventory with immutable surface graph, without admission."""
import hashlib,json,re
from pathlib import Path
from decode import decode
from backend import numbers
from proof import load_pages
import graph_extra
k=Path(__file__).resolve().parent;out=k/'emu001';root=Path('E:/xwn276/emu001');dest=out/'inventory-analysis.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));t=read(out/'trace.json');closure=read(out/'host-closure.json')
assert closure['closed'] and closure['host_exit']==0 and not closure['fallback_kill']
assert t['inventory_collection_completed'] and len(t['checkpoints'])==1 and not t['passed']
assert not t.get('terminal_request_may_be_accepted') and not list((root/'watch').iterdir())
assert t['physical_mode_restored'] and not t['remaining_breakpoint'] and not t['resumed_after_teardown']
assert not t.get('cleanup_error') and not t.get('frontend_cleanup_error')
report=numbers(t['initial_report']);assert report['state']==6 and report['reason']==14 and report['cpu0_reason']==0
cpu=decode(t['callback_inventory_report']);h=cpu['header'];assert h['count']==report['cpu0_count']
for key,value in [('epoch',report['cpu0_epoch']),('thread',report['cpu0_thread']),('worker',report['worker']),('when',report['cpu0_when']),('started',report['started']),('finished',report['finished']),('deadline',report['deadline'])]:assert h[key]==value
rows=load_pages(out,t,'initial',1,180000);ui=load_pages(out,t,'ui',1,8192)
assert len(rows)==report['rows'] and len(t['initial_pages'])==report['pages']
extra=graph_extra.inspect(rows,ui);assert extra['unknown_actor_work']==0
surfaces=[r for r in rows if r[0]==1];assert len({s[1] for s in surfaces})==len(surfaces)
stop=t['checkpoints'][0];head=stop['state_header'];pb=stop['pbkit']
known=[('current-extra-target',head[28],head[29]*head[30]),('current-depth',pb['_pb_DSAddr']&0x3ffffff,pb['_pb_DepthStencilPitch']*head[30])]
for u in range(4):known.append(('owned-texture-'+str(u),head[10+u],4096))
def match(callbacks,surfaces):
    result=[]
    for c in callbacks:
        identity,start,length,opaque,function,region,absolute=c
        found=[s for s in surfaces if s[5]==identity];assert len(found)==1
        s=found[0];assert s[2:4]==[start,length]
        result.append(dict(callback=identity,surface=s[1],start=start,bytes=length,function=function,region=region,opaque=opaque,
            flags=s[6],binding_roles=s[7],gl_texture=s[4],exact_native_ranges=[name for name,a,n in known if (a,n)==(start,length)],
            overlaps_native_ranges=[name for name,a,n in known if start<a+n and a<start+length]))
    assert {s[5] for s in surfaces if s[5]}=={c[0] for c in callbacks}
    return result
matched=match(cpu['callbacks'],surfaces);negatives=0
for i in range(len(cpu['callbacks'])):
    for col in [0,1,2]:
        changed=[r[:] for r in cpu['callbacks']];changed[i][col]^=1
        try:match(changed,surfaces)
        except AssertionError:negatives+=1
        else:raise AssertionError('Actual owner/range mutation accepted')
captures=[]
for item in stop['reads']:
    data=Path(item['private_file']).read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'];captures.append(item)
for entry in t['monitor']:
    if 'private_reply' in entry:
        data=Path(entry['private_reply']).read_bytes();assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256']
r=dict(scoped_refused_inventory_observation_passed=True,admission_passed=False,strict_passed=False,
    actual_cpu_header=h,matched_callbacks=matched,actual_owner_range_mutations_rejected=negatives,
    complete_graph_rows=len(rows),complete_graph_pages=len(t['initial_pages']),ui_pages=len(t['ui_pages']),
    extra_graph_scope=extra,native_captures_rehashed=len(captures),orderly_host_exit=0,
    no_observer_arm=True,no_guest_reuse=True,no_native_gpu_grant=True,no_release=True,
    limitations='One CPU-exclusive initial inventory before a refused boundary; no second acknowledgment or callback lifetime stability, retirement or unchanged texture reuse proved')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({a:b for a,b in r.items() if a not in ['extra_graph_scope']},indent=2))
