"""Independent immutable-page/owner-edge analysis. Never authorizes retirement."""
import collections, hashlib, json, re
from pathlib import Path

def numbers(text):
    return {k:int(v) for k,v in re.findall(r'(?<![\w])(\w+)=(\d+)',text)}

def decode_pages(texts,capacity):
    rows=[]; total=None
    for page,text in enumerate(texts):
        h=numbers(text)
        assert h['version']==265 and h['epoch']==1 and h['page']==page
        assert h['pages']==len(texts) and h['overflow']==0 and not h.get('invalid')
        if total is None:total=h['rows']
        assert h['rows']==total and 0<total<=capacity
        batch=re.findall(r'(?<!\w)r(\d+)=([0-9:]+)',text)
        assert len(batch)==min(256,total-page*256)
        for index,values in batch:
            assert int(index)==len(rows)
            row=list(map(int,values.split(':')))
            assert len(row)==8 and all(0<=v<2**64 for v in row)
            rows.append(row)
    assert total==len(rows) and len(texts)==(total+255)//256
    return rows

def inspect(rows,ui):
    by=collections.defaultdict(list)
    for row in rows:
        assert row[0] in set(range(1,19))|{30,31,32,33}
        by[row[0]].append(row)
    # Fixed capacities are source constants, not inferred from one successful run.
    assert len(by[3])==4 and sorted(r[1] for r in by[3])==list(range(4))
    assert len(by[6])==51200 and len({r[1] for r in by[6]})==51200
    assert len(by[7])==14 and sorted(r[1] for r in by[7])==list(range(14))
    assert len(by[8])==16 and sorted(r[1] for r in by[8])==list(range(16))
    assert len(by[10])==len(by[15])==len(by[16])==len(by[18])==1
    assert len(by[2])<=512 and len(by[4])<=516 and len(by[1])<=128
    assert len({r[1] for r in by[2]})==len(by[2])
    bindings={r[1]:r for r in by[4]};assert len(bindings)==len(by[4])
    accounts={r[1]:r for r in by[5]};assert len(accounts)==len(by[5])
    assert accounts.keys()==bindings.keys()
    cache=collections.Counter(r[2] for r in by[2]);units=collections.Counter(r[2] for r in by[3] if r[2])
    assert set(cache)|set(units)==set(bindings)
    for identity,b in bindings.items():
        assert identity and b[2]>0 and b[3]>0
        assert b[2]==cache[identity]+units[identity]
        assert accounts[identity][2:5]==[b[2],cache[identity],units[identity]]
    assert sum(units.values())<=4
    headers={r[1]:r for r in by[30]};assert len(by[30])==2 and set(headers)=={1,2}
    assert headers[1][2]==headers[2][2] and headers[1][2]>0
    uh=[r for r in ui if r[0]==30];holder=[r for r in ui if r[0]==40]
    assert len(uh)==len(holder)==1 and uh[0][1]==3
    assert holder[0][1]==uh[0][2] and holder[0][2]>0
    assert holder[0][1]!=headers[1][2]
    assert all(r[0] in [30,31,32,33,40] for r in ui)
    for group,header in [(rows,headers[1]),(rows,headers[2]),(ui,uh[0])]:
        context,units_count,attrs=header[1],header[4],header[5]
        assert 1<=units_count<=256 and 1<=attrs<=64
        integer=[r for r in group if r[0]==31 and r[1]==context]
        textures=[r for r in group if r[0]==32 and r[1]==context]
        attrib=[r for r in group if r[0]==33 and r[1]==context]
        assert len(integer)==13 and len({r[2] for r in integer})==13
        assert len(textures)==units_count*11
        assert len({(r[2],r[3]) for r in textures})==len(textures)
        assert {r[2] for r in textures}==set(range(units_count))
        assert len({r[3] for r in textures})==11
        assert len(attrib)==attrs and {r[2] for r in attrib}==set(range(attrs))
    callbacks=[[r[2:6] for r in by[17] if r[1]==phase] for phase in [0,1]]
    assert callbacks[0]==callbacks[1]
    assert not by[16][0][6]
    scan=by[15][0];assert scan[1]<scan[2] and scan[7]==0
    # Actor handles are never joined or declared completed by this observer.
    unknown=by[10][0][3]+sum(bool(r[6]) for r in by[9])
    assert unknown>=1
    return dict(collection_valid=True,texture_bindings=len(bindings),cache_edges=sum(cache.values()),
        unit_edges=sum(units.values()),unit_only_bindings=sum(not cache[i] for i in bindings),
        allocated_element_buffers=len(by[6]),live_element_entries=sum(bool(r[3]) for r in by[6]),
        shader_bindings=len(by[9]),shader_modules=len(by[11]),shader_actor_completion_unknown=unknown,
        queued_reports=len(by[12]),query_names=len(by[13])+len(by[14]),
        ui_hud_texture=holder[0][3],ui_snapshot_texture=holder[0][4],ui_last_texture=holder[0][5],
        conservative_scanout_start=scan[1],conservative_scanout_end=scan[2],
        callback_count=len(callbacks[0]),row_types={str(n):len(v) for n,v in by.items()},
        retirement_ready=False,native_gpu_grant=False,
        blockers=['shader actor completion remains unknown','HUD/snapshot holders are observed, not revoked',
                  'scanout reservation continues','no disposal or native cache/PTE/deferred-release proof',
                  'indexed buffer bindings and container attachments need separate closure review'])

def load(out,trace,kind):
    texts=[]
    for entry in trace[kind+'_pages']:
        p=out/entry['file'];data=p.read_bytes()
        assert hashlib.sha256(data).hexdigest()==entry['sha256']
        texts.append(data.decode('utf-8'))
    return decode_pages(texts,8192 if kind=='ui' else 180000)

if __name__=='__main__':
    k=Path(__file__).resolve().parent;out=k/'emu001';dest=out/'ledger-analysis.json'
    assert not dest.exists();t=json.loads((out/'trace.json').read_text());assert t['passed']
    r=inspect(load(out,t,'ledger'),load(out,t,'ui'))
    report=numbers(t['final_report'])
    assert report['accounting']==0 and report['bindings']==r['texture_bindings']
    assert report['shader_jobs_unknown']==r['shader_actor_completion_unknown']
    assert report['native_grant']==report['retirement']==0
    r.update(physical_access=False,debugger_observation=True,ordinary_qualified=False)
    dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
