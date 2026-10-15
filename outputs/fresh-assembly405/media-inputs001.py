"""Recover missing boot/input files from the SAME supplied customized ISO."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn405/media001');assert not P.exists();P.mkdir()
sys.path.insert(0,str(W/'work/python-packages'));import pycdlib,pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
iso=W/'outputs/Windows 2000 (SP4).iso';assert sha(iso)=='75ae5e4980e074377d3f0c2ab2e82dff0e3f80400da13c8e2d5a1479d2ccda1f'
names=['pciide.sys','openhci.sys','usbd.sys','usbhub.sys','hidusb.sys','hidclass.sys','hidparse.sys','kbdhid.sys','mouhid.sys','kbdclass.sys','mouclass.sys','hid.dll','pid.dll','hidserv.exe']
seven='/home/paul/xbox-windows-native/toolchains/7zip/root/usr/lib/7zip/7z'
cd=pycdlib.PyCdlib();cd.open(str(iso));archives=[]
for n in names:
    compressed=n[:-1].upper()+'_';dest=P/compressed
    try:cd.get_record(iso_path='/I386/'+compressed+';1')
    except pycdlib.pycdlibexception.PyCdlibException:continue
    cd.get_file_from_iso(str(dest),iso_path='/I386/'+compressed+';1');archives.append(dest)
cd.close()
for n in ['SP4.CAB','DRIVER.CAB']:
    p=Path('/mnt/c/xwn404/media-structure001/customized-sp4-oem-en')/n
    pin=next(v for v in json.loads((W/'outputs/clean-media404/media-structure001.json').read_text()) if v['id']=='customized-sp4-oem-en')
    assert sha(p)==next(v['sha256'] for v in pin['archives'] if v['name']==n);archives.append(p)
with (P/'extract.log').open('xb') as log:
    for archive in archives:
        cmd=[seven,'x','-y','-ssc-','-o'+str(P/'expanded'/archive.name),str(archive)]
        if archive.suffix.lower()=='.cab':cmd+=names
        subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT)
rows=[]
for name in names:
    choices=[]
    for p in (P/'expanded').rglob('*'):
        if p.is_file() and p.name.lower()==name:
            pe=pefile.PE(str(p));v=pe.VS_FIXEDFILEINFO[0];version=[v.FileVersionMS>>16,v.FileVersionMS&65535,v.FileVersionLS>>16,v.FileVersionLS&65535];pe.close()
            choices.append(dict(path=str(p),sha256=sha(p),version=version))
    assert choices,name
    version=max(v['version'] for v in choices);best=[v for v in choices if v['version']==version]
    assert len({v['sha256'] for v in best})==1,(name,'ambiguous equal-version media files')
    rows.append(dict(name=name,selected=best[0],candidates=choices))
(K/'media-inputs001.json').write_text(json.dumps(dict(iso_sha256=sha(iso),files=rows),indent=2)+'\n')
print('Same-ISO boot/input candidates',len(rows))
