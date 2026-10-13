"""Independent geometry and actual return accounting; never waives349 gates."""
import struct
def area(r):
    l,t,x,b=r;assert x>l and b>t;return (x-l)*(b-t)
def analyze(trace):
    assert trace['status']=='two_operations_captured' and trace['completed_intervals']==[12,13]
    assert trace['pending_calls']==0 and trace['armed_breakpoints_remaining']==[]
    assert trace['physical_mode_restored'] and trace['guest_resumed'] and not trace.get('teardown_error')
    assert trace['guest_memory_writes'] is False and trace['guest_register_writes'] is False
    assert len(trace['operations'])==2;result=[]
    for op in trace['operations']:
        assert op['complete'] and op['bitblt_returned'] and len(op['calls'])==26
        outer=op['arguments'];assert outer[0]==outer[5] and outer[3:5]==[960,540] and outer[8]==0xcc0020
        primary=[]
        for i in range(0,26,2):
            copy,call=op['calls'][i:i+2];assert copy['label']=='copy' and call['label']=='primary'
            for c in [copy,call]:
                assert c['returned'] and c['thread']==op['thread'] and c['process']==op['process']
                returns=[e for e in op['events'] if e['kind']=='return' and e['call']==c['index']]
                assert len(returns)==1
                reg=returns[0]['registers'];assert reg['EIP']==c['return_address'] and reg['ESP']==c['expected_return_sp'] and reg['EAX']==c['result']
            assert copy['result']==1 and copy['arguments']==call['arguments'][1:7]
            assert call['clip'] is None and call['xlate'] is None
            r=call['rect'];n=area(r)*4;d=call['destination'];s=call['source'];owners=call['owner_results'];p=call['pdev']
            assert call['arguments'][1:3]==[d['address'],s['address']]
            assert d['format']==s['format']==6
            for surf in [d,s]:
                v=struct.unpack('<12I2H',bytes.fromhex(surf['raw']))
                assert (surf['width'],surf['height'],surf['format'],surf['type'])==(v[4],v[5],v[11],v[12])
            if d['type']==s['type']==1:
                assert owners[0]['side']=='destination' and owners[1]['side']=='source' and len(owners)==2
                assert all(v['value']==p for v in owners) and call['result']==1 and call['copied_bytes']==n
                assert [d['width'],d['height']]==[1920,1080] and [s['width'],s['height']]==[1920,1080]
                shift=16 if op['id']==12 else -16
                assert [r[0]-call['source_origin'][0],r[1]-call['source_origin'][1]]==[shift,shift]
                kind='primary_to_primary'
            elif d['type']==1 and s['type']==0:
                assert len(owners)==2 and owners[0]['side']=='destination' and owners[0]['value']==p
                assert owners[1]['side']=='source' and owners[1]['value']==0 and call['result']==0xffffffff and call['copied_bytes']==0
                assert [s['width'],s['height']]==[31,27] and s['stride']==124 and s['cjBits']==3348
                kind='bitmap_to_primary'
            elif d['type']==0 and s['type']==1:
                assert len(owners)==1 and owners[0]['side']=='destination' and owners[0]['value']==0
                assert call['result']==0xffffffff and call['copied_bytes']==0
                assert [d['width'],d['height']]==[31,27] and d['stride']==124 and d['cjBits']==3348
                kind='primary_to_bitmap'
            else:raise AssertionError('Unexpected observed surface combination')
            primary.append(dict(index=call['index'],kind=kind,rect=r,source_origin=call['source_origin'],bytes=n,bitmap_identity=s['address'] if s['type']==0 else d['address'] if d['type']==0 else None))
        assert [sum(v['kind']==k for v in primary) for k in ['primary_to_primary','bitmap_to_primary','primary_to_bitmap']]==[8,3,2]
        destinations=[v['rect'] for v in primary if v['kind']!='primary_to_bitmap']
        bounds=[min(v[0] for v in destinations),min(v[1] for v in destinations),max(v[2] for v in destinations),max(v[3] for v in destinations)]
        assert [bounds[2]-bounds[0],bounds[3]-bounds[1]]==[960,540]
        for i,a in enumerate(destinations):
            for b in destinations[i+1:]:assert max(a[0],b[0])>=min(a[2],b[2]) or max(a[1],b[1])>=min(a[3],b[3]),'Overlapping destination accounting'
        assert sum(area(v) for v in destinations)==area(bounds)
        totals={k:sum(v['bytes'] for v in primary if v['kind']==k) for k in ['primary_to_primary','bitmap_to_primary','primary_to_bitmap']}
        assert totals==dict(primary_to_primary=2067564,bitmap_to_primary=6036,primary_to_bitmap=2688)
        bitmap_ids={v['bitmap_identity'] for v in primary if v['bitmap_identity']};assert len(bitmap_ids)==1
        result.append(dict(id=op['id'],destination_bounds=bounds,window_origin=[bounds[0]-outer[1],bounds[1]-outer[2]],totals=totals,calls=primary,one_shared_31_by_27_bitmap=next(iter(bitmap_ids)),destination_tile_complete=True,all_observed_eligible_primary_calls_fast=True))
    assert result[0]['window_origin']==result[1]['window_origin']
    return dict(scoped_call_accounting_passed=True,operations=result,original349_full_requested_fast_gate_still_failed=True,performance_qualified=False,physical_qualified=False,limits='Actual bounded debugger operations only. Small bitmap ownership proves primary-only ineligibility; its cursor role is not established by these arguments alone. No requalification of349, ordinary performance or new driver promotion.')
