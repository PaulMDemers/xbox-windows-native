"""Run under WSL: retain exact source bytes independently of the working checkout."""
import hashlib, io, json, pathlib, subprocess, tarfile
root=pathlib.Path('/home/paul/xbox-windows-native')
out=pathlib.Path('/mnt/e/Codex-archive/xbox-windows-native/0.1.0')
kit=pathlib.Path(__file__).resolve().parent
target=out/'xwn-0.1.0-native-sources.tar.gz'
assert not target.exists(), 'Do not replace a preserved source bundle'
manifest={}
components=[('reactos-extended',root/'sources/reactos-extended',root/'sources/reactos-extended'),
            ('cromwell-physical-f',root/'sources/cromwell',root/'build/cromwell-physical-f-001')]
def git(src,*args):return subprocess.check_output(['git','-C',str(src),*args])
with tarfile.open(target.with_suffix('.partial'),'w:gz',compresslevel=6) as archive:
    for name,repository,source in components:
        paths=git(repository,'ls-files','-z').decode().rstrip('\0').split('\0')
        assert not git(repository,'ls-files','--others','--exclude-standard').strip(), 'Untracked sources need explicit review'
        m=dict(base=git(repository,'rev-parse','HEAD').decode().strip(),source=str(source),files={})
        for rel in paths:
            p=source/rel
            assert p.is_file() or p.is_symlink(), str(p)
            if p.is_symlink():
                m['files'][rel]=dict(symlink=str(p.readlink()))
            else:
                data=p.read_bytes();m['files'][rel]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
            archive.add(p,arcname=name+'/'+rel,recursive=False)
        if repository==source:
            data=git(repository,'diff','--binary','HEAD');info=tarfile.TarInfo(name+'/WORKTREE.patch');info.size=len(data)
            archive.addfile(info,io.BytesIO(data))
        manifest[name]=m
    data=json.dumps(manifest,indent=2).encode();info=tarfile.TarInfo('SOURCE-MANIFEST.json');info.size=len(data)
    archive.addfile(info,io.BytesIO(data))
target.with_suffix('.partial').rename(target)
with tarfile.open(target,'r:gz') as archive:
    for member in archive:
        if '/' not in member.name or member.name.endswith('/WORKTREE.patch'):continue
        component,rel=member.name.split('/',1);info=manifest[component]['files'][rel]
        if member.issym(): assert member.linkname==info['symlink']
        else:
            data=archive.extractfile(member).read()
            assert len(data)==info['bytes'] and hashlib.sha256(data).hexdigest()==info['sha256']
h=hashlib.sha256()
with target.open('rb') as stream:
    for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
report=dict(path='E:/Codex-archive/xbox-windows-native/0.1.0/'+target.name,
            bytes=target.stat().st_size,sha256=h.hexdigest(),readback_verified=True,
            components={name:dict(base=m['base'],files=len(m['files']),source=m['source']) for name,m in manifest.items()},
            scope='Exact source snapshot; not a clean-room rebuild verification or toolchain archive')
(kit/'native-source-bundle.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
