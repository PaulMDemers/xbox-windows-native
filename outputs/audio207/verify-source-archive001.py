"""Read full archive and replay the final patch in a fresh owned source subset."""
import hashlib,json,pathlib,subprocess,tarfile
k=pathlib.Path(__file__).resolve().parent
archive=k/'artifacts/corresponding-source001/reactos0016.tar.gz'
with archive.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
assert digest=='0855bd035eda24d9c41fe020a7a129edfea8380cc8f4c94ba2f0972e63a1f8d4'
dest=k.parents[2]/'work/source-review001';dest.mkdir(exist_ok=False)
prefix='reactos0016/drivers/wdm/audio/drivers/ac97/'
count=0;total=0
with tarfile.open(archive,'r:gz') as tar:
    for member in tar:
        count+=1
        if member.isfile():
            stream=tar.extractfile(member);data=stream.read();assert len(data)==member.size
            total+=len(data)
            if member.name.startswith(prefix):
                relative=pathlib.PurePosixPath(member.name).relative_to('reactos0016')
                assert '..' not in relative.parts
                out=dest.joinpath(*relative.parts);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
patch=k/'0210-waveonly-cumulative.patch'
subprocess.run(['git','apply','--check',str(patch)],cwd=dest,check=True)
subprocess.run(['git','apply',str(patch)],cwd=dest,check=True)
pins=json.loads((k/'source-build004.json').read_text())
for name,h in pins['sources'].items():
    assert hashlib.sha256((dest/'drivers/wdm/audio/drivers/ac97'/name).read_bytes()).hexdigest()==h,name
r=dict(passed=True,archive_sha256=digest,members=count,file_bytes=total,patched_driver_files_verified=len(pins['sources']),base_tree=pins['base_tree'],patch_sha256=hashlib.sha256(patch.read_bytes()).hexdigest())
out=k/'source-archive-review001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
