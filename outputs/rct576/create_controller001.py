"""MIT. New physical controller, using proven transport and qualified575 helper."""
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'rct565'
p=K/'controller001.py';assert not p.exists()
s=(old/'controller004.py').read_text().replace('565','576').replace('stage004.json','stage001.json')
s=s.replace("KIT='/E/xwn576-kit';RESULT='/E/xwn576'", "KIT='/E/xwn575-kit';RESULT='/E/xwn575'")
s=s.replace("USED=KIT+'/startup-used.cmd'", "USED=KIT+'/startup-used576.cmd'")
s=s.replace('C:\\\\xwn576', 'C:\\\\xwn575').replace('run576.exe','run575.exe')
s=s.replace("{'xwn576','xwn576-kit'}", "{'xwn575','xwn575-kit'}")
s=s.replace("assert 'xwn576' not", "assert 'xwn575' not").replace("if 'xwn576' in", "if 'xwn575' in")
s=s.replace("for p,h in read(K/'transport-package003.json')['pins'].items():assert m.sha(Path(p).read_bytes())==h,p\n    ", '')
begin=s.index('def boot_work_closed():');end=s.index('\ndef startup(',begin)
s=s[:begin]+'''def boot_work_closed():
    prior=read(K.parent/'rct575/final001.json')
    assert prior['closed'] and prior['input_qualified'] and prior['cleanup_qualified']
    assert read(K.parent/'rct565/final001.json')['closed']
    assert read(K/'dashboard001.json')['completed']
    assert read(K.parent/'rct566/transfer001.json')['passed']

'''+s[end:]
s=s.replace("assert space['free_bytes']-q['total_bytes']>=128*1024**2", "assert space['admitted'] and space['package_bytes']==q['total_bytes'] and space['projected_remaining_bytes']>=128*1024**2")
s=s.replace("m.write_json(out,r)\n    with m.connect(timeout=15) as f:", "m.write_json(out,r)\n    deadline=time.monotonic()+3500\n    with m.connect(timeout=15) as f:",1)
s=s.replace('import importlib.util,json,shutil,sys','import importlib.util,json,shutil,sys,time')
s=s.replace("            f.storbinary('STOR '+n,io.BytesIO(b),65536)", """            started=time.monotonic()
            for offset in range(0,max(1,len(b)),32768):
                if time.monotonic()>deadline or time.monotonic()-started>600:raise TimeoutError('Bounded chunked stage')
                f.storbinary(('STOR ' if offset==0 else 'APPE ')+n,io.BytesIO(b[offset:offset+32768]),1024)
                if offset%1048576==0:
                    r['current_upload']=dict(path=n,sent=min(offset+32768,len(b)),bytes=len(b));m.write_json(out,r)""")
s=s.replace('watched_game_seconds=180','native_pc_control=575,unattended=True')
oldpaths="paths=list(dict.fromkeys(FILES+list(st['staged'])+list(game_rows)+[USED]+extra+['/E/winnt/system32/'+n for n in q['runtime_module_pins']]))"
newpaths="""# Full directory inventory, selected payload contents. New files always collected.
    selected=[n for n in game_rows if n not in st['staged'] or n.lower().endswith(('/rct.exe','/data/game.cfg','/data/css0.dat','.sv4','.sv6'))]
    paths=list(dict.fromkeys(FILES+[KIT+'/owner.json',KIT+'/run575.exe']+selected+[USED]+extra+['/E/winnt/system32/'+n for n in q['runtime_module_pins']]))
    r['collection_scope']='Whole game directory inventory; selected executable/config/CSS0/saves/new files and all result files. Other retail contents not rehashed after execution.'
    r['selected_paths']=paths;m.write_json(out,r)"""
assert oldpaths in s;s=s.replace(oldpaths,newpaths)
p.write_bytes(s.encode())
p=K/'controller_host001.py';assert not p.exists()
s=(old/'controller_host006.py').read_text().replace('565','576').replace('controller004.py','controller001.py').replace('stage004.json','stage001.json').replace('controller-host006.json','controller-host001.json').replace('run576.exe','run575.exe')
s=s.replace("assert command.startswith('STOR ') and blocksize==65536;n=command[5:];self.files[n]=stream.read();self.calls.append(('put',n))", "assert command.startswith(('STOR ','APPE ')) and blocksize==1024;n=command[5:];data=stream.read();self.files[n]=(self.files.get(n,b'')+data if command.startswith('APPE ') else data);self.calls.append(('put',n))")
s=s.replace("dict(free_bytes=0 if mode=='low-space' else 1024**3)", "dict(admitted=mode!='low-space',package_bytes=30,projected_remaining_bytes=1024**3)")
p.write_bytes(s.encode())
p=K/'audit001.py';assert not p.exists()
s=(old/'audit005.py').read_text().replace('565','576').replace('stage004.json','stage001.json').replace('collection002.json','collection001.json').replace("destination='/E/xwn576-kit/startup-used.cmd'", "destination='/E/xwn575-kit/startup-used576.cmd'")
p.write_bytes(s.encode())
p=K/'registry_review001.py';assert not p.exists()
s=(old/'registry_review005.py').read_text().replace('stage004.json','stage001.json').replace('collection002.json','collection001.json');p.write_bytes(s.encode())
p=K/'supervise001.py';assert not p.exists()
s=(old/'supervise004.py').read_text().replace('565','576').replace('supervisor004','supervisor001').replace('controller004.py','controller001.py')
s=s.replace('LIMITS=dict(stage=3600,launch=300,collect=1200)','LIMITS=dict(stage=3600,launch=900,collect=900)')
s=s.replace("([sys.executable,'-B',str(K/'resume_stage004.py')] if action=='stage' else [sys.executable,'-B',str(K/'controller001.py'),action])", "[sys.executable,'-B',str(K/'controller001.py'),action]")
p.write_bytes(s.encode())
