"""Independent bytes, paired graphs and generation proof; no renderer invocation."""
import hashlib,json,re,struct
from pathlib import Path
import oracle,terminal,graph_base,graph_extra
from decode import validate_graph
from backend import validate_report,numbers

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

def qualify(out,root):
    t=json.loads((out/'trace.json').read_text());assert t['passed'] and t['owner_boundaries_completed']
    assert t['terminal_phase']==33 and t['physical_mode_restored'] and not t['remaining_breakpoint']
    assert t['orderly_quit_sent'] and not t.get('cleanup_error') and not t.get('frontend_cleanup_error')
    reports=[validate_report(t[key],epoch) for epoch,key in [(1,'initial_report'),(2,'terminal_report')]]
    assert reports[0]['worker']==reports[1]['worker'] and reports[0]['cpu0_thread']==reports[1]['cpu0_thread']
    assert reports[1]['started']>reports[0]['finished']
    ui=load_pages(out,t,'ui',1,8192);graphs=[];analyses=[]
    for epoch,key in [(1,'initial'),(2,'terminal')]:
        rows=load_pages(out,t,key,epoch,180000);graphs.append(rows)
        assert all(r[0] in set(range(1,19))|{30,31,32,33}|set(range(50,71)) for r in rows)
        boundary=validate_graph(rows,epoch,t['checkpoints'][0]['state_header'][10:14])
        a=graph_base.inspect([r for r in rows if r[0]<50],[r for r in ui if r[0]<50])
        e=graph_extra.inspect(rows,ui);assert e['unknown_actor_work']==0
        assert a['texture_bindings']==reports[epoch-1]['bindings']
        analyses.append(dict(base=a,extension=e,boundary278=boundary))
    assert analyses[0]['extension']['native_contexts']==analyses[1]['extension']['native_contexts']
    watch=(root/'watch/terminal273.bin').read_bytes();life=terminal.decode(watch)
    assert struct.unpack_from('<16Q',watch)[9]==reports[0]['worker']
    assert all(w['live'] and not w['has_free'] for w in life['watches'])
    initial={r[1]:r for r in graphs[0] if r[0]==3};final={r[1]:r for r in graphs[1] if r[0]==3}
    accounts=[{r[1]:r for r in g if r[0]==5} for g in graphs]
    bindings=[{r[1]:r for r in g if r[0]==4} for g in graphs]
    captures=[];ctx=int(analyses[0]['extension']['native_contexts']['1']);worker=reports[0]['worker']
    for u in range(4):
        w=life['watches'][u];identity=w['identity']
        assert initial[u][2]==final[u][2]==identity
        assert initial[u][3]==0,'Initial unit must be disabled'
        assert accounts[0][identity][2:5]==[2,1,1] and accounts[1][identity][2:5]==[2,1,1]
        phys=t['checkpoints'][0]['state_header'][18+u]
        pair=[snapshot((root/f'watch/unit-{u}-stage-{stage}.bin').read_bytes(),u,stage,phys,worker,ctx) for stage in [0,1]]
        a,b=pair
        assert a['header'][4:6]==b['header'][4:6]==(w['generation'],identity)
        assert a['header'][6]==b['header'][6]==bindings[0][identity][3]==bindings[1][identity][3]
        assert a['key']==b['key'] and a['source']==b['source'] and a['rgba']==b['rgba']
        captures.append(dict(unit=u,generation=w['generation'],identity=identity,gl_name=a['header'][6],source_sha256=hashlib.sha256(a['source']).hexdigest(),rgba_sha256=hashlib.sha256(a['rgba']).hexdigest(),draw_time_before=a['header'][9],draw_time_after=b['header'][9]))
    return dict(scoped_unchanged_guest_reuse_passed=True,life=life,graphs=analyses,captures=captures,release_installed=False,native_gpu_grant=False,performance_qualified=False)

if __name__=='__main__':
    k=Path(__file__).resolve().parent;out=k/'emu001';dest=out/'reuse-proof.json';assert not dest.exists()
    try:r=qualify(out,Path('E:/xwn278/emu001'))
    except Exception as e:r=dict(scoped_unchanged_guest_reuse_passed=False,error=repr(e))
    dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
