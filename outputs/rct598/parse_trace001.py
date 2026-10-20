"""Parse API entries; deliberately do not classify requests as resolutions/calls."""
from collections import Counter

def parse(text,imagebase,imagesize):
    lines=text.splitlines();assert lines and lines[-1].startswith('END ')
    calls=[];arms=[];images=[];ends=[];modules=[];threads=[]
    for line in lines:
        p=line.split();kind=p[0]
        if kind in ['LOAD','PROC','ORD']:
            assert len(p)==5
            tid,caller,module=(int(x,16) for x in p[1:4])
            value=int(p[4],16) if kind=='ORD' else bytes.fromhex(p[4]).decode('cp1252')
            assert tid and 0<=module<=0xffffffff
            if kind=='LOAD':assert module==0
            calls.append(dict(kind=kind,thread=tid,caller=hex(caller),module=hex(module),value=value,main_image_caller=imagebase<=caller<imagebase+imagesize))
        else:
            assert len(p)==4 and kind in ['ARM','IMAGE','DLL','THREAD','END'],line
            values=[int(x,16) for x in p[1:]]
            {'ARM':arms,'IMAGE':images,'DLL':modules,'THREAD':threads,'END':ends}[kind].append(values)
    assert len(images)==1 and images[0][0]==imagebase
    assert len(arms)==2 and sorted(r[0] for r in arms)==[0,1]
    assert {r[1] for r in arms}=={0xc460f0,0xc460f4}
    assert len(ends)==1 and ends[0]==[0,len(calls),0] and calls
    main=[r for r in calls if r['main_image_caller']]
    return dict(passed=True,total_entry_requests=len(calls),main_image_requests=len(main),other_caller_requests=len(calls)-len(main),
                calling_threads=len({r['thread'] for r in calls}),library_requests=dict(Counter(r['value'] for r in main if r['kind']=='LOAD')),
                named_export_requests=dict(Counter(r['value'] for r in main if r['kind']=='PROC')),ordinal_requests=[r for r in main if r['kind']=='ORD'],
                arms=arms,dll_load_events=modules,threads=threads,calls=calls,scope='Actual API-entry arguments only. A GetProcAddress name does not establish successful resolution or invocation; DLL load events alone do not establish rendering or acceleration.')
