"""Strict ordered receipt parser; no renderer or guest implementation imports."""
def analyze(blob):
    expected=[('case',642),('begin.tick',None),('mode.query',1),('mode.width',720),('mode.height',480),('mode.bpp',32),('mode.frequency',None),('mode.expected',1),('screen.width',720),('screen.height',480),('window.class',1),('window.created',1),('dd.create',0),('dd.cooperative',0),('dd.primary',0),('dd.describe',0),('primary.flags',None),('primary.width',720),('primary.height',480),('primary.pitch',2880),('primary.bpp',32),('primary.geometry',1),]
    mini_keys=[]
    for i in range(3):
        expected.append(('draw.upload',1))
        if i:expected.append(('draw.overlap',1))
        expected.extend([('draw.flush',1),('draw.readback',1),('readback.flush',1),('pass%d.mismatches'%i,0)])
    expected.extend([('input.seed_created',1),('input.seed_written',1),('input.deadline_ms',300000),('input1.started',1),('input1.closed',1),('input1.exit_query',1),('input1.exit_code',0),('input1.readback',1),('input1.bytes',None),('input1.matches',1),('input2.started',1),('input2.closed',1),('input2.exit_query',1),('input2.exit_code',0),('input2.readback',1),('input2.bytes',None),('input2.unchanged',1),('input.complete',1)])
    expected.extend([('failures',0),('complete',1),('end.tick',None),('restart.lookup',1),('restart.privilege',1),('restart.requesting',1),('restart.accepted',1)])
    result={'passed':False}
    try:
        assert isinstance(blob,bytes) and len(blob)<=16424 and blob.endswith(b'\r\n'),'missing/oversized/incomplete receipt'
        lines=blob.decode('ascii').split('\r\n')[:-1]
        pairs=[line.split('=') for line in lines]
        mini=[(k,int(v)) for k,v in pairs if k.startswith('miniport.')]
        assert mini and mini[0][0]=='miniport.enumerate' and mini[0][1] in [0,1],'miniport enumeration'
        if mini[0][1]==0:assert mini==[('miniport.enumerate',0)]
        else:
            assert len(mini)>=3 and mini[1][0]=='miniport.open' and mini[1][1] in [0,1]
            if mini[1][1]==0:assert len(mini)==3 and mini[2][0]=='miniport.error' and mini[2][1]>0
            else:
                assert mini[2][0]=='miniport.query' and mini[2][1] in [0,1] and mini[3][0]=='miniport.bytes'
                if mini[2][1]==0:assert len(mini)==5 and mini[4][0]=='miniport.error' and mini[4][1]>0
                else:assert mini[3:]==[('miniport.bytes',80),('miniport.width',720),('miniport.height',480),('miniport.pitch',2880),('miniport.bpp',32),('miniport.geometry',1)]
        at=next(i for i,(key,_) in enumerate(expected) if key=='draw.upload')
        expected[at:at]=mini+[('draw.client',1)]
        assert len(lines)==len(expected),'record count' 
        values={}
        for line,(key,want) in zip(lines,expected):
            k,s=line.split('=');assert k==key and s.isascii() and s.isdigit(),'record schema/order'
            v=int(s);assert 0<=v<=0xffffffff and (want is None or v==want),(key,v,want)
            values[key]=v
        assert 1<=values['mode.frequency']<=240,'frequency'
        assert values['primary.flags']&0x100e==0x100e,'descriptor fields absent'
        assert values['input1.bytes'] in [7,9] and values['input2.bytes']==values['input1.bytes'],'input lengths'
        elapsed=(values['end.tick']-values['begin.tick'])&0xffffffff
        assert 12000<=elapsed<=600000,'probe clock bound'
        result.update(passed=True,values=values,probe_elapsed_ms=elapsed,records=len(lines))
    except (AssertionError,UnicodeError,ValueError,AttributeError,IndexError,TypeError) as e:result['reason']=str(e)
    return result
