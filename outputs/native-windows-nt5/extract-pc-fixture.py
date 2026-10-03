"""Extract a stopped PC fixture read-only and discard its reproducible RAW copy."""
import hashlib,json,pathlib,re,struct,subprocess
ROOT=pathlib.Path('/home/paul/xbox-windows-native')
VM=ROOT/'fixtures/pc-win2000'
workspace=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out=workspace/'outputs/native-windows-nt5'
target=out/'installed-files'
if (VM/'qmp.sock').exists():raise SystemExit('Stop the owned VM before extracting its persistent disk')
if target.exists():raise SystemExit('Refusing to overwrite a prior extraction')
raw=VM/'extraction.raw'
if raw.exists():raise SystemExit('Refusing to overwrite a prior extraction RAW')
disk=VM/'win2000.qcow2'
files=['boot.ini','ntldr','ntdetect.com','WINNT/system32/config/system','WINNT/system32/config/system.log',
       'WINNT/system32/ntoskrnl.exe','WINNT/system32/hal.dll','WINNT/system32/bootvid.dll',
       'WINNT/setupact.log','WINNT/setuperr.log']
files += ['WINNT/system32/drivers/'+n+'.sys' for n in ['atapi','intelide','pciide','pci','isapnp','disk','classpnp','ntfs','fastfat','scsiport','mountmgr','ftdisk','dmio','dmload','partmgr','ksecdd']]
target.mkdir()
try:
    subprocess.run(['qemu-img','convert','-O','raw',str(disk),str(raw)],check=True)
    with raw.open('rb') as stream:mbr=stream.read(512)
    assert mbr[510:512]==b'\x55\xaa'
    parts=[]
    for i in range(4):
        entry=mbr[446+16*i:462+16*i]
        parts.append({'index':i+1,'boot_flag':entry[0],'type':entry[4],'start_lba':struct.unpack_from('<I',entry,8)[0],'sectors':struct.unpack_from('<I',entry,12)[0]})
    cmd=[str(ROOT/'toolchains/7zip/root/usr/lib/7zip/7z'),'x','-y','-ssc-',f'-o{target}',str(raw),*files]
    result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,check=True)
    (out/'pc-extraction.log').write_text(result.stdout)
    redactions=[]
    for log in (target/'WINNT').glob('*.log'):
        original=log.read_bytes()
        clean,count=re.subn(rb'(?i)\b[A-Z0-9]{5}(?:-[A-Z0-9]{5}){4}\b',b'[REDACTED PRODUCT ID]',original)
        if count:
            redactions.append({'file':str(log.relative_to(target)),'count':count,'original_sha256':hashlib.sha256(original).hexdigest()})
            log.write_bytes(clean)
    records={str(p.relative_to(target)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in target.rglob('*') if p.is_file()}
    required=['WINNT/system32/config/system','WINNT/system32/ntoskrnl.exe','WINNT/system32/hal.dll','boot.ini']
    actual_names={name.casefold() for name in records}
    assert all(n.casefold() in actual_names for n in required),records.keys()
    with disk.open('rb') as stream:disk_hash=hashlib.file_digest(stream,'sha256').hexdigest()
    report={'disk':str(disk),'disk_sha256':disk_hash,'partition_table':parts,'files':records,
            'missing_optional_files':sorted(name for name in files if name.casefold() not in actual_names), 'raw_copy_removed_after_extraction':True,'log_redactions':redactions}
    (out/'pc-extraction.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'files':len(records),'partitions':parts},indent=2))
finally:
    assert raw.resolve().is_relative_to(VM.resolve())
    raw.unlink(missing_ok=True)
