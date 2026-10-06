"""Paired disposable fixtures: identical nonzero allocation tails, only FATX differs."""
import importlib,json,struct,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
SIZES=[1,2,511,512,513,4095,4096,4097,8191,8192,8193,65535,65536,65537,131071,131072,131073]
def expected(i,n,round=0):return bytes((x*13+i*17+round*29)&255 for x in range(n))
def entry(w,path):
    at=1;parts=w.parts(path)
    for part in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][part.lower()][2],44)[0]
    return w.directory(at)['entries'][parts[-1].lower()]
def reader(disk):
    io=m.SliceIO(disk);return m.Writer(io,m.fatx.open_partition(io,disk,'F'))
def run(*args):subprocess.run(list(args),check=True,stdout=subprocess.DEVNULL)
def main():
    base=ws/'outputs/native-windows-fatx-forensics/artifacts/video-installer-pair004.qcow2'
    ref=json.loads((ws/'outputs/video-installer-isolation/pair004/fixture.json').read_text())
    assert m.filehash(base)==ref['fixture_sha256']
    common=base.with_name('fatx-mapped-eof-common.qcow2');assert not common.exists()
    m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
    run('qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(common));m.target=common
    w=reader(common);payloads=[];tails=[]
    startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
    data=b'@echo off\r\nC:\\xwneof01\\probe.exe\r\nexit\r\n';m.replace(w,startup,data)
    payloads.append(dict(path=startup,sha256=m.sha(data),bytes=len(data)))
    payloads.append(w.write('xwneof01/probe.exe',(k/'artifacts/probe.exe').read_bytes()))
    hives={p:m.sha(w.read('winnt/system32/config/'+p)) for p in ['system','software','default']}
    for i,n in enumerate(SIZES):
        path=f'xwneof01/input{i:02}.bin';data=expected(i,n);payloads.append(w.write(path,data))
        dc,off,e=entry(w,path);chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));last=chain[-1]
        used=n-(len(chain)-1)*w.p.cluster_size
        b=w.read_cluster(last);w.write_cluster(last,b[:used]+b'\xd7'*(w.p.cluster_size-used))
        tails.append(dict(path=path,size=n,last_cluster=last,tail_bytes=w.p.cluster_size-used,tail_byte=215))
    w.flush();fresh=reader(common)
    for row in payloads:assert m.sha(fresh.read(row['path']))==row['sha256']
    for row in tails:assert fresh.read_cluster(row['last_cluster'])[row['size']%fresh.p.cluster_size or fresh.p.cluster_size:]==b'\xd7'*row['tail_bytes']
    for p,h in hives.items():assert m.sha(fresh.read('winnt/system32/config/'+p))==h
    assert m.filehash(base)==ref['fixture_sha256']
    run('qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',base.name,str(common))
    commonhash=m.filehash(common)
    for case in ['old','fixed']:
        target=base.with_name('fatx-mapped-eof-'+case+'.qcow2');seed=ws/('work/fatx-mapped-eof-'+case+'-seed.qcow2')
        assert not target.exists() and not seed.exists()
        run('qemu-img','create','-f','qcow2','-F','qcow2','-b',str(common),str(target));m.target=target;w=reader(target)
        path='winnt/system32/drivers/xwnfatx.sys';old=w.read(path)
        assert m.sha(old)=='0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336'
        if case=='fixed':
            driver=(k.parent/'fatx-paging-eof/artifacts/xwnfatx.sys').read_bytes()
            assert m.sha(driver)=='beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd'
            m.replace(w,path,driver);w.flush()
        else:driver=old
        fresh=reader(target);assert fresh.read(path)==driver
        for row in payloads:assert m.sha(fresh.read(row['path']))==row['sha256']
        for p,h in hives.items():assert m.sha(fresh.read('winnt/system32/config/'+p))==h
        run('qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',common.name,str(target))
        run('qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed))
        run('qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed))
        r=dict(scope=__doc__,case=case,physical_access=False,parent_sha256=ref['fixture_sha256'],common_sha256=commonhash,
            fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),fatx_sha256=m.sha(driver),payloads=payloads,
            input_tails=tails,cluster_size=w.p.cluster_size,hives_unchanged=hives,expected_rounds=8,
            preserved_payloads=[p for p in ref['payloads'] if p['path']!=startup],
            limits='Pre-INF synthetic-resource emulator fixture; two audio failed-install flags inherited.')
        (k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
    assert m.filehash(common)==commonhash
    print('Paired fixtures verified; only FATX payload differs',flush=True)
if __name__=='__main__':main()
