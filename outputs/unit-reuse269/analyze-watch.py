"""Independent bounded binary/sequence parser; missing guest reuse is a failure."""
import hashlib,json,re,struct
from pathlib import Path
MAX=2*1024*1024
def decode(raw):
    assert len(raw)>=192
    h=struct.unpack_from('<24Q',raw)
    assert h[0:2]==(0x3936324e5758,269) and h[2] in (0,1) and h[3]<4
    assert h[4]==h[3]+1 and h[5] and h[6] and h[7]>0
    assert 0<h[11]<=MAX and h[13]<=4096 and h[10]+h[11]<=64*1024*1024
    assert h[12]+h[13]<=64*1024*1024 and 0<h[14]<=MAX and 0<h[15]<=MAX
    assert h[17]==h[14]*h[15]*4 and h[17]<=MAX and 0<h[18]<=256
    assert h[19]==1 and h[20]==0 and h[21] and h[22] and h[23]==1
    lengths=[h[18],h[11],h[13],h[17]];assert len(raw)==192+sum(lengths)
    parts=[];pos=192
    for n in lengths:parts.append(raw[pos:pos+n]);pos+=n
    return h,parts
def inspect(folder,units,worker,context,terminal_error):
    assert terminal_error==0
    initial={};later={};files={}
    for p in sorted(folder.glob('unit-*-stage-*.bin')):
        raw=p.read_bytes();h,parts=decode(raw);u=h[3];stage=h[2]
        assert p.name==f'unit-{u}-stage-{stage}.bin'
        assert h[5]==units[u]['binding_identity'] and h[6]==units[u]['gl_texture']
        assert h[21]==worker and h[22]==context
        dest=initial if stage==0 else later;assert u not in dest;dest[u]=(h,parts)
        files[p.name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'part_sha256':[hashlib.sha256(x).hexdigest() for x in parts]}
    assert set(initial)=={0,1,2,3}
    events=[];dead=set();seen=set();armed=False
    for seq,p in enumerate(sorted(folder.glob('event-*.txt'))):
        assert seq<128 and p.name==f'event-{seq:03d}.txt'
        r={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',p.read_text())}
        assert set(r)=={'seq','kind','unit','identity','code','thread'} and r['seq']==seq and r['thread']==worker
        u=r['unit'];assert u<4
        if r['kind']==1:assert seq==0 and not armed and r['identity']==0 and r['code']==0;armed=True
        else:
            assert armed and r['identity']==units[u]['binding_identity'] and u not in dead
            if r['kind']==2:
                assert u not in seen and r['code']&255 in [1,2] and r['code']>>8<4
                seen.add(u)
            elif r['kind']==3:assert r['code']>0
            elif r['kind']==4:
                assert events and events[-1]['kind']==3 and events[-1]['unit']==u and events[-1]['code']==1
                dead.add(u)
            else:raise AssertionError(('failure/overflow/unknown event',r))
        events.append(r)
    assert armed and set(later)==seen
    comparisons=[]
    for u in range(4):
        if u not in later:comparisons.append({'unit':u,'actual_reuse':False,'unchanged':False});continue
        a,ap=initial[u];b,bp=later[u]
        # Refcount can legitimately vary. Every content/key/shape/lifetime field
        # below and every independently parsed byte is checked separately.
        fields=[4,5,6,8,9,10,11,12,13,14,15,16,17,18,21,22]
        changes=[i for i in fields if a[i]!=b[i]]
        equal=[x==y for x,y in zip(ap,bp)]
        comparisons.append({'unit':u,'actual_reuse':True,'unchanged':not changes and all(equal),'changed_header_fields':changes,'key_source_palette_rgba_equal':equal})
    return {'observation_parse_pass':True,'all_four_actual_reuse':len(seen)==4,
        'all_four_unchanged':all(c['unchanged'] for c in comparisons),'comparisons':comparisons,
        'actual_bind_count':len(seen),'final_destroyed_units':sorted(dead),'events':events,'files':files,
        'normal_guest_binds_only':True,'release_installed':False,'native_gpu_grant':False,
        'cpu_source_double_sample_limitation':'Matching source copies detect observed changes, not arbitrary ABA writes or CPU-exclusive post-resume ownership.',
        'independent_final_frame_correctness':False,'ordinary_qualified':False}
if __name__=='__main__':
    k=Path(__file__).resolve().parent;o=k/'emu001'
    t=json.loads((o/'trace.json').read_text());assert t['passed']
    seal=json.loads((o/'watch-seal.json').read_text());assert seal['acknowledged'] and seal['cpu_stopped']
    import importlib.util
    spec=importlib.util.spec_from_file_location('base',k/'analyze-base.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    rows=base.load(o,t,'ledger');byid={r[1]:r for r in rows if r[0]==4}
    units={r[1]:{'binding_identity':r[2],'gl_texture':byid[r[2]][3]} for r in rows if r[0]==3}
    report=(o/'watch-terminal.txt').read_text();n=base.numbers(report)
    contexts=[r for r in rows if r[0]==51 and r[1]==1];assert len(contexts)==1
    f=Path(json.loads((o/'watch-location.json').read_text())['path'])
    result=inspect(f,units,base.numbers(t['final_report'])['worker'],contexts[0][3],n['reuse269_error'])
    dest=o/'watch-analysis.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
