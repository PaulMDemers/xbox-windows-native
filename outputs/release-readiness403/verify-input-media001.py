import hashlib,json,subprocess,zipfile
from pathlib import Path
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
media=root/'outputs/EN_WIN2000_PRO_SP4.ISO'
seven=Path('/home/paul/xbox-windows-native/toolchains/7zip/root/usr/lib/7zip/7z')
out=Path('/mnt/c/xwn403/input-media001');out.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(media)=='e3816f6e80b66ff686ead03eeafffe9daf020a5e4717b8bd4736b7c51733ba22'
names=['openhci.sys','usbd.sys','usbhub.sys','hidusb.sys','hidclass.sys','hidparse.sys','kbdhid.sys','mouhid.sys','kbdclass.sys','mouclass.sys','hid.dll','pid.dll']
with (out/'extract.log').open('w') as log:
    subprocess.run([str(seven),'x','-y','-ssc-','-o'+str(out/'compressed'),str(media)]+['I386/'+n[:-1].upper()+'_' for n in names],stdout=log,stderr=subprocess.STDOUT,check=True)
    compressed={p.name.lower():p for p in (out/'compressed').rglob('*') if p.is_file()}
    for n in names:
        p=compressed[n[:-1]+'_']
        subprocess.run([str(seven),'x','-y','-o'+str(out/'expanded'),str(p)],stdout=log,stderr=subprocess.STDOUT,check=True)
expanded={p.name.lower():p for p in (out/'expanded').rglob('*') if p.is_file()}
rows=[]
with zipfile.ZipFile('/mnt/c/xwn399/system002/xwn-private-E-720p-demo-20261014.zip') as z:
    index={n.lower():n for n in z.namelist()}
    for name in names:
        key='payload/e/winnt/system32/'+('drivers/' if name.endswith('.sys') else '')+name
        a=expanded[name].read_bytes();b=z.read(index[key])
        rows.append({'name':name,'media_sha256':hashlib.sha256(a).hexdigest(),'installed_sha256':hashlib.sha256(b).hexdigest(),'byte_identical':a==b,'source':'Owned Windows 2000 SP4 media','public_distribution':False})
result={'iso_sha256':sha(media),'seven_sha256':sha(seven),'files':rows,'all_equal':all(r['byte_identical'] for r in rows),'scope':'Input binary provenance against original supplied media; no redistribution or runtime test'}
(root/'outputs/release-readiness403/input-provenance001.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'files':len(rows),'all_equal':result['all_equal'],'mismatches':[r['name'] for r in rows if not r['byte_identical']]}))
