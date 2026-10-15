import json,hashlib,zipfile,subprocess
from pathlib import Path
root=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');out=Path('/mnt/c/xwn403/input-media003');out.mkdir(parents=True,exist_ok=False)
seven='/home/paul/xbox-windows-native/toolchains/7zip/root/usr/lib/7zip/7z'
rows=json.loads((root/'outputs/release-readiness403/input-provenance002.json').read_text())['files']
names=[r['name'] for r in rows if not r['byte_identical']]
media_records=json.loads((root/'outputs/native-windows-nt5/supplied-media.json').read_text())
print('media_metadata_shape',type(media_records).__name__,flush=True)
with (out/'extract.log').open('w') as log:
    for iso in ['EN_WIN2000_PRO_SP4.ISO','Windows 2000 (SP4).iso']:
        media=root/'outputs'/iso;d=out/('retail' if iso.startswith('EN_') else 'oem')
        subprocess.run([seven,'x','-y','-ssc-','-o'+str(d/'compressed'),str(media),'I386/DRIVER.CAB','I386/SP4.CAB']+['I386/'+n[:-1].upper()+'_' for n in names],stdout=log,stderr=subprocess.STDOUT,check=True)
        for archive in (d/'compressed').rglob('*'):
            if not archive.is_file():continue
            dst=d/'expanded'/archive.name
            command=[seven,'x','-y','-ssc-','-o'+str(dst),str(archive)]
            if archive.suffix.lower()=='.cab':command+=names
            subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
found=[]
for p in out.glob('*/expanded/**/*'):
    if p.is_file():
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        for r in rows:
            if r['installed_sha256']==h:
                found.append({'name':r['name'],'media_path':str(p.relative_to(out)),'sha256':h})
record={'matches':found,'unresolved':[n for n in names if not any(r['name']==n for r in found)],'media_sha256':{n:hashlib.sha256((root/'outputs'/n).read_bytes()).hexdigest() for n in ['EN_WIN2000_PRO_SP4.ISO','Windows 2000 (SP4).iso']},'scope':'Exact owned-media provenance; original002 mismatches retained; no redistribution'}
(root/'outputs/release-readiness403/input-provenance003.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
