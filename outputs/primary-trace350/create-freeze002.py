from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'freeze002.py';assert not dest.exists()
s=(K/'freeze.py').read_text();old="""for name,m in read(K/'sites002.json')['modules'].items():
    if name=='replay.exe':continue
    key='E/winnt/system32/'+name;assert f['protected'][key]==m['sha256'],name"""
new="""providers=read(K/'provider-preflight001.json');assert providers['passed'] and providers['prepared_fixture_sha256']==f['fixture_sha256']
for name,m in read(K/'sites002.json')['modules'].items():assert providers['modules'][name]['sha256']==m['sha256'],name
pins[(K/'provider-preflight001.json').relative_to(W).as_posix()]=sha(K/'provider-preflight001.json')"""
assert s.count(old)==1;dest.write_bytes(s.replace(old,new).encode())
