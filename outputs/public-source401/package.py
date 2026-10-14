"""Assemble and readback-verify the separate PRIVATE source review candidate."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import zipfile

K=Path(__file__).resolve().parent
ROOT=Path('C:/xwn401/source003')
OUT=Path('C:/xwn401/package001')
sha=lambda b:hashlib.sha256(b).hexdigest()
PATTERNS={
 'machine_path':rb'(?i)(?:[A-Z]:[\\/]Users[\\/][^\s\\/]+|/home/[^/\s]+|/mnt/[cde]/(?:Codex|Users))',
 'private_ipv4':rb'\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b',
 'credential_literal_review':rb'''(?i)(?:password|passwd|ftp_pass)\s*[=:]\s*["'][^"'\r\n]+["']|\.login\(\s*["'][^\r\n]+''',
 'token_or_private_key':rb'gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
}
ALLOWED={'.py','.json','.c','.patch','.md','.txt',''}

def save(p,obj):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,indent=2);f.write('\n')

def main():
    if OUT.exists() or (ROOT/'MANIFEST.json').exists(): raise RuntimeError('Consumed package identity')
    record=json.loads((K/'source003.json').read_text())
    if not record['all_source_replays_passed']: raise RuntimeError('Source replay failed')
    for name,expected in record['input_sha256'].items():
        if sha((K.parents[1]/name).read_bytes())!=expected:raise RuntimeError('Input changed: '+name)
    files=[];hits=[];links=[]
    for p in sorted(ROOT.rglob('*')):
        if p.is_symlink(): raise RuntimeError('Symlink in export')
        if not p.is_file(): continue
        name=p.relative_to(ROOT).as_posix();data=p.read_bytes()
        # Upstream copying filenames use suffixes such as .ARM and .LIB.
        if p.suffix not in ALLOWED and not name.startswith('licenses/'):
            raise RuntimeError('Unexpected file type: '+name)
        if b'\0' in data or data.startswith(b'MZ') or '/.git/' in '/'+name:
            raise RuntimeError('Binary/history content in export')
        data.decode('utf-8')
        files.append(dict(path=name,bytes=len(data),sha256=sha(data)))
        for category,pattern in PATTERNS.items():
            for m in re.finditer(pattern,data):
                hits.append(dict(category=category,path=name,line=data[:m.start()].count(b'\n')+1))
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',data.decode()):
                if '://' in link or link.startswith('#'):continue
                dest=(p.parent/link.split('#')[0]).resolve()
                if not dest.is_relative_to(ROOT) or not dest.exists(): raise RuntimeError('Broken/outside documentation link: '+link)
                links.append(dict(source=name,target=link))
    save(K/'export-scan001.json',dict(files=len(files),hits=hits,internal_links_checked=len(links),
         scope='All allowlisted exported bytes, text/type/path/token patterns and internal Markdown links; not comprehensive clearance',
         public_ready=False))
    if any(x['category'] in ('token_or_private_key','credential_literal_review','machine_path') for x in hits):
        raise RuntimeError('Export needs content review before archive assembly; locations saved without values')
    manifest=dict(schema=1,status='PRIVATE SOURCE REVIEW CANDIDATE',public_release_ready=False,
                  files=files,excluded='No binaries, Git history, Windows media, firmware, EEPROM, hives, user files or private captures')
    save(ROOT/'MANIFEST.json',manifest)
    spec=importlib.util.spec_from_file_location('verify',ROOT/'tools/verify-package.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    verified=verifier.verify(ROOT)
    OUT.mkdir()
    names=[row['path'] for row in files]+['MANIFEST.json']
    archives=[]
    for suffix in ['','-repeat']:
        dest=OUT/('xwn-source-review401'+suffix+'.zip')
        with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name in sorted(names):
                zi=zipfile.ZipInfo(name,date_time=(2026,10,14,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
                zi.external_attr=0o100644<<16;zi.create_system=3
                z.writestr(zi,(ROOT/name).read_bytes(),compresslevel=9)
        with zipfile.ZipFile(dest) as z:
            if sorted(z.namelist())!=sorted(names):raise RuntimeError('Archive namespace mismatch')
            for name in names:
                if z.read(name)!=(ROOT/name).read_bytes():raise RuntimeError('Archive readback mismatch: '+name)
        archives.append(dict(path=str(dest),sha256=sha(dest.read_bytes()),bytes=dest.stat().st_size,entries=len(names)))
    if archives[0]['sha256']!=archives[1]['sha256']:raise RuntimeError('Nondeterministic packaging')
    save(K/'package001.json',dict(archives=archives,verified=verified,all_entries_readback=True,
        repeat_identical=True,public_release_ready=False,compiled=False,hardware_access=False,
        caveat='Identical packaging of identical inputs is not reproducible compilation or licensing clearance'))
    print(json.dumps(archives[0]))

if __name__=='__main__': main()
