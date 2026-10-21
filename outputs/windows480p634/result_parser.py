"""Strict ordered receipt parser; no renderer or guest implementation imports."""
def analyze(blob):
    expected=[('case',634),('begin.tick',None),('mode.query',1),('mode.width',720),('mode.height',480),('mode.bpp',32),('mode.frequency',None),('mode.expected',1),('screen.width',720),('screen.height',480),('window.class',1),('window.created',1),('dd.create',0),('dd.cooperative',0),('dd.primary',0),('dd.lock',0),('primary.width',720),('primary.height',480),('primary.pitch',2880),('primary.bpp',32),('primary.geometry',1),('primary.unlock',1),('draw.client',1)]
    for i in range(3):
        expected.append(('draw.upload',1))
        if i:expected.append(('draw.overlap',1))
        expected.extend([('draw.flush',1),('draw.readback',1),('readback.flush',1),('pass%d.mismatches'%i,0)])
    expected.extend([('failures',0),('complete',1),('end.tick',None),('restart.lookup',1),('restart.privilege',1),('restart.requesting',1),('restart.accepted',1)])
    result={'passed':False}
    try:
        assert isinstance(blob,bytes) and len(blob)<=16384 and blob.endswith(b'\r\n'),'missing/oversized/incomplete receipt'
        lines=blob.decode('ascii').split('\r\n')[:-1];assert len(lines)==len(expected),'record count'
        values={}
        for line,(key,want) in zip(lines,expected):
            k,s=line.split('=');assert k==key and s.isascii() and s.isdigit(),'record schema/order'
            v=int(s);assert 0<=v<=0xffffffff and (want is None or v==want),(key,v,want)
            values[key]=v
        assert 1<=values['mode.frequency']<=240,'frequency'
        elapsed=(values['end.tick']-values['begin.tick'])&0xffffffff
        assert 12000<=elapsed<=600000,'probe clock bound'
        result.update(passed=True,values=values,probe_elapsed_ms=elapsed,records=len(lines))
    except (AssertionError,UnicodeError,ValueError,AttributeError) as e:result['reason']=str(e)
    return result
