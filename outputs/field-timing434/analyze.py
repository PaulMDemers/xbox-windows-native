"""Retained actual sample analysis; preserve non-wrap regressions explicitly."""
import hashlib,json,statistics,struct
from pathlib import Path
from decode import decode,terminal
K=Path(__file__).resolve().parent;P=Path('C:/xwn434/physical001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=K/'analysis001.json';assert not out.exists()
    r=json.loads((K/'physical001-collection.json').read_text());assert r['completed']
    for n,f in r['files'].items():assert sha(P/n)==f['sha256']
    terminal((P/'result.dat').read_bytes());rows=[];negative=0
    for stage in range(3):
        data=(P/f'raster-{stage}.dat').read_bytes();m=decode(data,stage)
        values=list(struct.iter_unpack('<QIQI',data[1024:]))
        # This is an explicitly selected low-word-wrap analysis, not a field-ID decoder.
        wraps=[];other=[]
        for i in range(1,len(values)):
            prior=values[i-1][1];current=values[i][1]
            if current<prior:
                if (prior&0xffff)>500 and (current&0xffff)<10:wraps.append(i)
                else:other.append(dict(index=i,prior=prior,current=current,
                    time_ticks=values[i][0],read_start_end=[values[i][0],values[i][2]]))
        periods=[(values[j][0]-values[i][0])*1000/m['frequency'] for i,j in zip(wraps,wraps[1:])]
        cycles=[]
        for i,j in zip(wraps,wraps[1:]):
            raw=[v[1] for v in values[i:j]]
            cycles.append(dict(first_index=i,last_index=j-1,low16_min=min(v&65535 for v in raw),
                low16_max=max(v&65535 for v in raw),samples=j-i))
        cr=m['crtc'];mm=m['mmio'];active=cr['0x12']+((cr['0x7']&2)<<7)+((cr['0x7']&64)<<3)+((cr['0x25']&2)<<9)+1
        bits16=[v[1]&65535 for v in values if v[1]&65536]
        rows.append(dict(stage=stage,samples=len(values),low_word_wraps=len(wraps),
            wrap_period_ms=periods,period_median_ms=statistics.median(periods),cycles=cycles,
            other_raw_decreases=other,bit16_set_low_word_range=[min(bits16),max(bits16)],
            other_high_bits_observed=hex(sum({v[1]&0xfffe0000 for v in values})),
            legacy_pitch_bytes=(cr['0x13']+((cr['0x19']&224)<<3))*8,
            crtc_active_lines=active,output_active_lines=mm['0x680800']+1,
            double_scan=bool(cr['0x9']&128),cell_height_low5=cr['0x9']&31,
            scan_div2=bool(cr['0x17']&4),address_div2=bool(cr['0x17']&8),
            nv04_named_yscale_bit=bool(mm['0x680880']&16),
            bit16_interpretation='Correlates with blanking; not identified as field parity',
            parity_proved=False))
        for word in [0,1,2,3,4,5,6,7,8,11,12,17,20,21,28,29,55,93]:
            q=bytearray(data);at=512+word*4;v=struct.unpack_from('<I',q,at)[0]
            struct.pack_into('<I',q,at,v^0x80000000)
            try:decode(q,stage)
            except ValueError:negative+=1
            else:raise AssertionError(('actual mutation accepted',stage,word))
    report=dict(passed=True,scope='Actual read-only register observations; no parity or visual PASS',
        captures_rehashed=len(r['files']),samples=sum(x['samples'] for x in rows),
        actual_transport_mutations_rejected=negative,modes=rows,
        static_registers_unchanged_within_each_capture=True,
        framebuffer_check='Native same-helper pixel comparisons before/after; no independent framebuffer files in434',
        known_limits=['Raw counter reports CRTC position, not memory fetch address',
          'No independently documented field-ID bit found; no inferred bit treated as proof',
          'One internal backward sample in1080i is preserved separately, not counted as a cycle wrap',
          'Cycle sampling uncertainty includes roughly14.5us between samples; not an analog sync capture'])
    out.write_text(json.dumps(report,indent=2)+'\n');print({k:report[k] for k in ['passed','samples','actual_transport_mutations_rejected']})
if __name__=='__main__':main()
