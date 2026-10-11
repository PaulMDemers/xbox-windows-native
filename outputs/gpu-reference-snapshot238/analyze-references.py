"""Post-observation range and retained-reference classification, no guest IO."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent

def classify(v,vram_bytes):
    assert 0<vram_bytes<2**64 and len(v['context'])==20 and len(v['current_fifo'])==14
    fifo=v['current_fifo'];ctx=v['context'];surfaces=v['surfaces'];ranges=[];invalid=[];overlaps=[]
    for i,row in enumerate(surfaces):
        addr,size,pitch,width,height=row[:5]
        valid=bool(width and height and size and size<=16*1024**2 and pitch*height<=size and addr<vram_bytes and size<=vram_bytes-addr)
        if not valid:invalid.append(i)
        else:ranges.append((i,addr,addr+size))
    for i,a,b in ranges:
        for j,c,d in ranges:
            if j>=i:break
            if a<d and c<b:overlaps.append([j,i])
    dirty=[i for i,r in enumerate(surfaces) if r[5]&3]
    color=sum(r[7] for r in surfaces);zeta=sum(r[8] for r in surfaces)
    complete=bool(v['renderer_valid'] and not v['surface_truncated'])
    queue_parser_empty=fifo[4]==fifo[5] and not fifo[6]&0xFFFC0000
    reasons=[]
    if not complete:reasons.append('surface inventory unavailable or truncated')
    if invalid:reasons.append('invalid/oversized surface ranges')
    if overlaps:reasons.append('overlapping cached surface ranges')
    if ctx[0]:reasons.append('active primitive')
    if any(ctx[1:5]):reasons.append('retained draw/inline batch lengths')
    if v['renderer_valid'] and ctx[5]:reasons.append('frontend framebuffer in use')
    if any(ctx[6:8]):reasons.append('flush/sync pending')
    if v['wait_mask']:reasons.append('PGRAPH wait bits')
    if not queue_parser_empty:reasons.append('FIFO queue/parser not empty')
    return dict(current_fifo_when=v['fifo_when'],pg_when=v['current_pg_only'][1],separate_sample_phases=True,
        producer_halted=bool(fifo[0]),queue_parser_empty=bool(queue_parser_empty),wait_mask=v['wait_mask'],
        renderer_valid=v['renderer_valid'],surface_inventory_complete=complete,surfaces=len(surfaces),dirty_indices=dirty,
        dirty_bytes=sum(surfaces[i][1] for i in dirty),retained_access_callbacks=sum(r[6] for r in surfaces),
        color_binding_present=bool(ctx[18]) if v['renderer_valid'] else None,
        zeta_binding_present=bool(ctx[19]) if v['renderer_valid'] else None,
        color_binding_matches_in_list=color,zeta_binding_matches_in_list=zeta,
        invalid_ranges=invalid,overlapping_ranges=overlaps,observed_preservation_obstacles=reasons,
        producer_close_proved=False,all_references_retired=False,ownership_qualified=False,
        limit='Different lock-phase samples; observed compatibility with legacy preservation preconditions is not an admission, fence, readback or ownership proof.')

if __name__=='__main__':
    dest=k/'reference-analysis001.json';assert not dest.exists()
    from parsing import snapshot_tuple
    root=k/'artifacts/build001/source';regs=(root/'hw/xbox/nv2a/nv2a_regs.h').read_text(encoding='utf-8')
    for name,value in [('METHOD_COUNT','0x1FFC0000'),('ERROR','0xE0000000')]:
        assert re.search(r'NV_PFIFO_CACHE1_DMA_STATE_'+name+r'\s+'+value,regs)
    vsh=k/'artifacts/analysis-inputs/vsh_regs.h'
    assert hashlib.sha256(vsh.read_bytes()).hexdigest()==json.loads((k/'candidate001-source-pins.json').read_text(encoding='utf-8'))['hw/xbox/nv2a/pgraph/vsh_regs.h']
    assert re.search(r'enum ShaderPrimitiveMode\s*\{\s*PRIM_TYPE_INVALID\s*,',vsh.read_text(encoding='utf-8'))
    rows=[]
    for case in ['dashboard001','xbe001','freeldr001']:
        t=json.loads((k/case/'trace.json').read_text(encoding='utf-8'))
        assert t['closed'] and t['passed']
        v=snapshot_tuple(t['phase_snapshot']['terminal_reply']);assert v==t['phase_snapshot']['tuple']
        rows.append(dict(case=case,**classify(v,64*1024**2)))
    dest.write_text(json.dumps(dict(passed=True,post_observation_only=True,cases=rows,physical_access=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),vram_bytes=64*1024**2,vram_scope='Configured -m64 Xbox shared RAM, not an independent runtime size read',vsh_sha256=hashlib.sha256(vsh.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(rows,indent=2))
