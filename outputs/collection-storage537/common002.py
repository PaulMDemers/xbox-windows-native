"""Narrow closed-executable selection; reuse reviewed Win32 metadata helpers."""
import importlib.util,stat
from pathlib import Path
K=Path(__file__).resolve().parent
source=K.parent/'portable-compression523/common002.py'
s=importlib.util.spec_from_file_location('storage523',source);old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
sha=old.sha;js=old.js;metadata=old.metadata;processes=old.processes;volume=old.volume;COMPACT=old.COMPACT
MINIMUM=20*1024**3;PROJECTED=64*1024**2
SPEC={
 '524':('extent-runtime524','C:/xwn524/runs/nt5-extent524-emu001/instance.json','C:/xwn524/instances/windows-native-extent524-emu001/EA3473314E6C0EA0/xemu-windows-native-extent524-emu001.exe'),
 '527-1':('dispatch-control527','C:/xwn527/emu001/instance.json','C:/xwn527/instances/dispatch527-emu001/EA3473314E6C0EA0/xemu-dispatch527-emu001.exe'),
 '527-2':('dispatch-control527','C:/xwn527/emu002/instance.json','C:/xwn527/instances/dispatch527-emu002/EA3473314E6C0EA0/xemu-dispatch527-emu002.exe'),
 '528-1':('visible-dispatch528','C:/xwn528/emu001/instance.json','C:/xwn528/instances/dispatch528-emu001/EA3473314E6C0EA0/xemu-dispatch528-emu001.exe'),
 '528-2':('visible-dispatch528','C:/xwn528/emu002/instance.json','C:/xwn528/instances/dispatch528-emu002/EA3473314E6C0EA0/xemu-dispatch528-emu002.exe')}
def validate_path(p,case):
    assert case in SPEC
    expected=Path(SPEC[case][2]);assert p.absolute()==expected.absolute() and p.resolve(strict=True)==expected.absolute()
    for component in [p,*p.parents]:assert not component.lstat().st_file_attributes&0x400,str(component)
    s=p.stat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not s.st_file_attributes&(0x4000|0x200|0x400)
    return p
def selection():
    rows=[];records={str(source):sha(source)}
    for case,(folder,instance,exe) in {'524':SPEC['524']}.items():
        fp=K.parent/folder/'final-review.json';ip=Path(instance);f=js(fp);i=js(ip)
        assert f['all_owned_processes_closed'] and (f.get('passed') or f.get('review_passed'))
        p=validate_path(Path(exe),case);assert Path(i['executable'])==p
        m=metadata(p);historic=f['private_files'][str(p)]
        if isinstance(historic,dict):historic=historic['sha256']
        assert m['sha256']==historic==i['sourceSha256'].lower()=='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'
        assert m['bytes']==191317057
        for r in [fp,ip]:records[str(r.resolve())]=sha(r)
        rows.append(dict(case=case,path=str(p),metadata=m,recorded_original_sha256=historic))
    assert len({r['path'].casefold() for r in rows})==1
    return rows,records
