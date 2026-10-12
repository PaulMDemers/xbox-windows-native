"""Independent bytes, paired graphs and generation proof; no renderer invocation."""
import hashlib,json,re,struct
from pathlib import Path
import oracle,terminal,graph_base,graph_extra
from decode import validate_graph
from backend import numbers

def vertices():
    b=bytearray()
    for x,y in [(32,32),(80,80)]:
        q=[(x,y,0,0),(x+16,y,16,0),(x+16,y+8,16,8),(x,y+8,0,8)]
        for i in [0,1,2,0,2,3]:
            a,c,u,v=q[i];b+=struct.pack('<8f',a,c,.1,1,u,v,0,1)
    return bytes(b)

def pages(texts,epoch,capacity):
    rows=[];total=None
    for page,text in enumerate(texts):
        h=numbers(text)
        assert h['version']==265 and h['epoch']==epoch and h['page']==page
        assert h['pages']==len(texts) and h['overflow']==0 and not h.get('invalid')
        if total is None:total=h['rows']
        assert 0<total<=capacity and h['rows']==total
        batch=re.findall(r'(?<!\w)r(\d+)=([0-9:]+)',text)
        assert len(batch)==min(256,total-page*256)
        for index,values in batch:
            assert int(index)==len(rows)
            row=list(map(int,values.split(':')))
            assert len(row)==8 and all(0<=v<2**64 for v in row);rows.append(row)
    assert len(rows)==total and len(texts)==(total+255)//256
    return rows

def snapshot(data,unit,stage,physical,worker,context):
    assert len(data)>=192
    h=struct.unpack_from('<24Q',data)
    assert h[:4]==(terminal.MAGIC,273,stage,unit)
    assert all(h[i]>0 for i in [4,5,6,7])
    assert h[10:18]==(physical,512,0,0,16,8,0x8058,512)
    assert 0<h[18]<=1024 and h[19:24]==(1,0,worker,context,1)
    assert len(data)==192+h[18]+512+512
    key=data[192:192+h[18]];source=data[192+h[18]:192+h[18]+512];rgba=data[-512:]
    expected=oracle.blocks()[unit][256:768]
    assert source==expected,'Independent source pixels'
    want=bytes(v for i in range(0,512,4) for v in [expected[i+2],expected[i+1],expected[i],expected[i+3]])
    assert rgba==want,'Independent GL RGBA pixels'
    return dict(header=h,key=key,source=source,rgba=rgba)

def load_pages(out,t,key,epoch,cap):
    texts=[]
    for p in t[key+'_pages']:
        b=(out/p['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==p['sha256'];texts.append(b.decode())
    return pages(texts,epoch,cap)

def initial_snapshots(root,t,result,candidate):
    worker=result['records'][0][10];context=int(result['graphs'][0]['extension']['native_contexts']['1']);captures=[]
    for u in range(4):
        physical=t['checkpoints'][0]['state_header'][18+u]
        a,b=[snapshot((root/f'watch/unit-{u}-stage-{stage}.bin').read_bytes(),u,stage,physical,worker,context) for stage in [0,2]]
        edge=result['unbound_edges']['selected'][u]
        assert a['header'][4:7]==b['header'][4:7] and a['header'][5:7]==(edge['identity'],edge['gl_name'])
        assert a['header'][7]==2 and b['header'][7]==(1 if candidate else 2)
        assert a['header'][8:]==b['header'][8:]
        assert a['key']==b['key'] and a['source']==b['source'] and a['rgba']==b['rgba']
        captures.append(dict(unit=u,generation=a['header'][4],identity=edge['identity'],gl_name=edge['gl_name'],
            before_refs=a['header'][7],after_refs=b['header'][7],source_sha256=hashlib.sha256(a['source']).hexdigest(),rgba_sha256=hashlib.sha256(a['rgba']).hexdigest()))
    return dict(independent_pre_post_snapshots_passed=True,candidate=candidate,captures=captures)

def resumed(root,t,initial_result,final_result,candidate):
    first=initial_snapshots(root,t,initial_result,candidate)
    data=(root/'watch/terminal273.bin').read_bytes();life=terminal.decode(data)
    worker=final_result['records'][1][10];context=int(final_result['graphs'][0]['extension']['native_contexts']['1'])
    assert struct.unpack_from('<16Q',data)[9]==worker
    assert life['sequence']==8 and life['runs']==4 and life['captures']==15
    # Both modes have one decrement and one actual guest bind per identity.
    # The candidate's decrement removes refs2 ->1 before any guest bind;
    # the control's ordinary replacement decrement is refs3 ->2.
    runs=[struct.unpack_from('<8Q',data,768+64*i) for i in range(4)]
    assert {r[4] for r in runs}==set(range(4))
    assert all(r[3]==3 and r[5]==(2 if candidate else 3) and r[7]==1 for r in runs)
    binds=[]
    for u,w in enumerate(life['watches']):
        assert w['live']==w['has_bind']==w['binds']==w['decrements']==1 and not w['has_free']
        e=struct.unpack_from('<20Q',data,128+u*160)[8:14];binds.append(e)
        assert e[4]==u and e[5]>>8==u and e[5]&255 in (1,2)
        run=next(r for r in runs if r[4]==u);assert run[0]<e[0]
        capture=first['captures'][u];assert (w['identity'],w['generation'])==(capture['identity'],capture['generation'])
        physical=t['checkpoints'][0]['state_header'][18+u]
        a,b=[snapshot((root/f'watch/unit-{u}-stage-{stage}.bin').read_bytes(),u,stage,physical,worker,context) for stage in [0,1]]
        assert a['header'][4:]==b['header'][4:] and a['header'][7]==2
        assert a['key']==b['key'] and a['source']==b['source'] and a['rgba']==b['rgba']
    if candidate:assert max(r[0] for r in runs)<min(b[0] for b in binds)
    return dict(life=life,captures=first['captures'],actual_release_decrements=4 if candidate else 0,
        actual_guest_binds=4,independent_three_snapshot_equality=True,candidate=candidate)

def qualify(out,root):
    import checks
    t=json.loads((out/'trace.json').read_text());candidate=out.name.startswith('candidate')
    assert t['passed'] and t['owner_boundaries_completed'] and t['terminal_phase']==33 and len(t['checkpoints'])==3
    assert t['physical_mode_restored'] and not t['remaining_breakpoint'] and t['orderly_quit_sent']
    assert not t.get('cleanup_error') and not t.get('frontend_cleanup_error')
    assert all(v['pixel_check']['passed'] for v in t['checkpoints'])
    groups=[load_pages(out,t,f'stage{i}',i,180000) for i in range(1,4)];ui=load_pages(out,t,'ui',1,8192)
    allocations=t['checkpoints'][0]['state_header'][10:14]
    a=checks.initial(t['initial_report'],groups[:2],ui,allocations,candidate)
    b=checks.final(t['initial_report'],t['terminal_report'],groups,ui,allocations,candidate)
    reuse=resumed(root,t,a,b,candidate)
    return dict(scoped_unchanged_guest_reuse_passed=True,initial=a,terminal=b,reuse=reuse,
        release_installed=candidate,actual_release_executed=candidate,native_gpu_grant=False,performance_qualified=False)

