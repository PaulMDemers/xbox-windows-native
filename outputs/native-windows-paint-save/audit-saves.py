"""Cold readback of Paint outputs and exact driver hashes; not a whole-volume audit."""
import argparse,hashlib,importlib,json,pathlib,struct
m=importlib.import_module('prepare-fixture');k=m.k
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run in ('nt5-paint-save-003','nt5-paint-pressure-001','nt5-paint-replay-001','nt5-paint-runner-001','nt5-paint-trace-001','nt5-paint-matched-001');run=m.ws/'work/runs'/a.run
assert (run/'cleanup.json').exists()
disk=run/'hdd.qcow2';f=m.SliceIO(disk);m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
w=m.Writer(f,m.fatx.open_partition(f,disk,'F'));folder=k/'artifacts'/a.run;folder.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def pixels(data):
    assert data[:2]==b'BM' and struct.unpack_from('<I',data,2)[0]==len(data)
    off=struct.unpack_from('<I',data,10)[0];header,width,height,planes,bpp,compression=struct.unpack_from('<IiiHHI',data,14)
    assert header==40 and width>0 and height>0 and planes==1 and bpp==24 and compression==0
    stride=(width*3+3)&~3;assert len(data)==off+stride*height
    return width,height,b''.join(data[off+y*stride:off+y*stride+width*3] for y in reversed(range(height)))
r=dict(scope=__doc__,run=a.run,files=[],drivers=[],complete=False)
cases=[('xwnpaint/saved-'+name+'.bmp',name+'.bmp') for name in ['blank','coords','oddwidth']]
cases += [('Documents and Settings/win2k/Desktop/'+name+'.bmp',None) for name in ['emu-scribble','fresh-scribble']]
if a.run=='nt5-paint-pressure-001':
    cases=[('Documents and Settings/win2k/My Documents/untitled.bmp',None),('xwnpaint/slow.bmp',None)]
if a.run=='nt5-paint-trace-001':
    cases=[('xwnpaint/'+name+'.bmp','scribble.bmp') for name in ['trace-save','trace-full']]
if a.run in ('nt5-paint-replay-001','nt5-paint-runner-001'):
    cases=[(f'xwnpaint/replay{i:02d}.bmp','scribble.bmp') for i in range(16)]
if a.run=='nt5-paint-matched-001':
    cases=[(f'xwnpaint/match{i:02d}.bmp','scribble.bmp') for i in range(16)]
for path,reference in cases:
    data=w.read(path);name=path.split('/')[-1];(folder/name).write_bytes(data)
    width,height,rgb=pixels(data);row=dict(path=path,bytes=len(data),sha256=sha(data),width=width,height=height,pixel_sha256=sha(rgb),complete_bmp=True)
    if reference:
        expected=pixels((k/'artifacts/images'/reference).read_bytes());row['pixels_match_input']=(width,height,rgb)==expected;assert row['pixels_match_input']
        if a.run in ('nt5-paint-trace-001','nt5-paint-matched-001'):
            row['bytes_match_input']=data==(k/'artifacts/images'/reference).read_bytes();assert row['bytes_match_input']
    else:
        assert (width,height)==(512,288);row['nonwhite_pixels']=sum(rgb[i:i+3]!=b'\xff\xff\xff' for i in range(0,len(rgb),3));assert row['nonwhite_pixels']>100
    r['files'].append(row)
for name,expected in [('xwnfatx.sys','0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336'),('xboxvnt5.sys','f8af1d8477d61ad8933962fd6347f43620f5ef1d21efe54110b94fec106986eb')]:
    actual=sha(w.read('winnt/system32/drivers/'+name));r['drivers'].append(dict(name=name,sha256=actual,matches=actual==expected));assert actual==expected
for name,path in [('system.evt','winnt/system32/config/sysevent.evt'),('application.evt','winnt/system32/config/appevent.evt')]:
    data=w.read(path);(folder/name).write_bytes(data)
if a.run in ('nt5-paint-pressure-001','nt5-paint-replay-001'):
    r['pressure_log']=w.read('xwnpaint/pressure.log').decode('ascii');(folder/'pressure.log').write_text(r['pressure_log'])
if a.run in ('nt5-paint-replay-001','nt5-paint-runner-001'):
    r['replay_log']=w.read('xwnpaint/replay.log').decode('ascii');(folder/'replay.log').write_text(r['replay_log']);assert r['replay_log'].count('CASE_PASS ')==16 and '\nPASS 16 ' in r['replay_log'] and 'FAIL_' not in r['replay_log']
if a.run=='nt5-paint-runner-001':
    r['runner_log']=w.read('xwnpaint/attempt.log').decode('ascii');assert r['runner_log']=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
    for item in json.loads((k/'runner-fixture.json').read_text())['helpers']:
        assert sha(w.read(item['path']))==item['sha256']
if a.run=='nt5-paint-matched-001':
    log=w.read('xwnpaint/matched.log').decode('ascii');(folder/'matched.log').write_text(log);r['matched_log']=log
    assert log.count('CASE_PASS ')==16 and '\nPASS 16 ' in log and 'FAIL_' not in log
    assert log.count('SEQUENCE_DONE ')==16 and log.count('WRITE_BEGIN ')==8*29
    for i in range(16):
        assert f'CASE_BEGIN_QUIET {i} 0 {i&1} ' in log
        assert f'SEQUENCE_DONE {i} 29 29 ' in log
    r['runner_log']=w.read('xwnpaint/attempt.log').decode('ascii')
    assert r['runner_log']=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
    for item in json.loads((k/'matched-fixture.json').read_text())['helpers']:
        assert sha(w.read(item['path']))==item['sha256']
r.update(complete=True,passed=True)
(k/(a.run+'-save-audit.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
