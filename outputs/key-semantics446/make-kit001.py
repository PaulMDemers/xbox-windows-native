"""Create a distinct diagnostic kit from closed444; never modify the parent."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'sprites444'
names=['runner.c','build001.py','binary-review001.py','prepare001.py','cold002.py','cold003.py','login001.py','run001.py','independent001.py','preflight001.py']
for name in names:
    p=K/name
    assert not p.exists()
    s=(old/name).read_text(encoding='utf-8').replace('sprites444','key-semantics446').replace('xwn444','xwn446').replace('run444','run446').replace('XWN444','XWN446')
    if name=='runner.c':
        s=s.replace('Six isolated','Two isolated').replace('"default index8 r04di","hel index8 r04si","default rgb565 r04d6","hel rgb565 r04s6","default rgb32 r04d3","hel rgb32 r04s3"','"default keyd","hel keys"').replace('"r04di","r04si","r04d6","r04s6","r04d3","r04s3"','"keyd","keys"').replace('sprites.exe','keyprobe.exe').replace('SPRITES.EXE','KEYPROBE.EXE').replace('i<6','i<2').replace('completed==6','completed==2').replace('number("schema",444)','number("schema",446)')
    elif name=='build001.py':
        s=s.replace('/sprites.exe','/keyprobe.exe').replace('23fcd2208b74a80feaf55d6a52be1b4a34a4138da859fa10bc06d5867862776f','0fcbc34e3d18339aa0f4a7bfe1d2e8852846a697469e7a591d97456863b3649c')
    elif name=='binary-review001.py':
        s=s.replace("Path('//wsl.localhost/Ubuntu'+row['path'])","Path(row['path'])").replace('E:/xwn425','/mnt/e/xwn425')
    elif name=='independent001.py':
        s=s.replace('20<len(selected)<60','len(selected)==20')
    elif name=='run001.py':
        s=s.replace('import argparse,datetime,json,os,socket,subprocess,sys,time','import argparse,datetime,json,os,socket,subprocess,sys,time\nfrom launch_gate import launch')
        s=s.replace('proc=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)',"proc=launch(K/'preflight001.json',K,P,'key-semantics446-pc001',cmd,popen=subprocess.Popen,env=env,stdout=log,stderr=subprocess.STDOUT)")
    elif name=='preflight001.py':
        s=s.replace('import hashlib,json,shutil,sys','import hashlib,json,shutil,sys,time\nfrom launch_gate import publish')
        s=s.replace("W/'tools/graphics_sprites.py'","W/'tools/graphics_keyprobe.py'")
        s=s.replace("pins={str(p):sha(p) for p in files}","files += [K/n for n in ['ntfs-preparation001.json','ntfs-cold0-002.json','build001.json','sample-build001.json','binary-review001.json','gate-tests001.json']]\nfiles += [W/'src/samples/graphics-ladder/keyprobe.c',W/'src/samples/graphics-ladder/keyprobe.cmd',W/'tools/build-graphics-samples.py',W/'tests/test_graphics_keyprobe.py']\npins={str(p.resolve()):sha(p) for p in files}")
        start=s.index('record=dict(passed=True')
        s=s[:start]+'''assert json.loads((K/'gate-tests001.json').read_text())['passed'] is True
record=dict(schema=1,attempt='key-semantics446-pc001',fixture=str(Path(prep['path']).resolve()),completed=True,passed=True,finished_ns=time.time_ns(),files=pins,
 fixture_files={str(Path(prep['path'])/'disk.qcow2'):prep['child_sha256'],str(Path(prep['path'])/'probe.img'):prep['floppy_sha256'],prep['source']:prep['source_sha256']})
publish(out,record);print('Completed preflight published:',len(pins),'dependencies')
'''
    p.write_text(s,encoding='utf-8',newline='\n')
print('New kit created, no guest preparation or launch.')
