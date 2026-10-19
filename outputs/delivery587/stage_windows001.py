"""Private package staging from a fresh dashboard snapshot; never deploys or launches."""
from pathlib import Path
import hashlib,json,os,shutil,sys
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import tester_bundle
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
c=json.loads((K/'capture001.json').read_text());assert c['complete'] and c['critical_unchanged']
src=Path(c['root']);mf=src/'CAPTURE-MANIFEST.json';assert sha(mf)==c['manifest_sha256'];inventory=json.loads(mf.read_text())
supp=json.loads((K/'supplement001.json').read_text());assert supp['completed']
stage=Path('C:/xwn587/windows-staging001');assert not stage.exists();stage.mkdir()
assert shutil.disk_usage('C:/').free-16*1024**2>20*1024**3
out=K/'windows-stage001.json';assert not out.exists()
r={'completed':False,'root':str(stage),'console_writes':False,'source_capture_manifest_sha256':c['manifest_sha256'],'excluded':[],'added':[],'modified_captured_files':[]}
try:
    for d in inventory['directories']:(stage/d.lstrip('/')).mkdir(parents=True,exist_ok=True)
    for name,meta in inventory['files'].items():
        p=src/name.lstrip('/');assert p.stat().st_size==meta['bytes'] and sha(p)==meta['sha256']
        if name.lower().endswith(('.sys.422used','.exe.422used')):
            r['excluded'].append({'path':name,'reason':'Inactive historical loader backup; live loader retained','sha256':meta['sha256']});continue
        assert not any(x in name.lower() for x in ('rct.exe','rollercoaster','xwn582-kit','xwn586-kit'))
        dest=stage/name.lstrip('/');os.link(p,dest)
    dep=stage/'E/xwndemo372';dep.mkdir()
    for name,row in supp['files'].items():
        p=Path(row['path']);assert sha(p)==row['sha256'];shutil.copyfile(p,dep/name);r['added'].append({'path':'E/xwndemo372/'+name,'sha256':row['sha256'],'reason':'Exact ordinary-startup dependency from same installation'})
    for folder in ('host','docs','source','licenses'):(stage/folder).mkdir()
    for name in ('tester_bundle.py','fatx_names.py'):shutil.copyfile(W/'tools'/name,stage/'host'/name)
    shutil.copyfile(K/'WINDOWS-README.txt',stage/'README.txt')
    for name in ('installation.md','display-configuration.md','tester-report-template.md','licensing.md'):
        shutil.copyfile(W/'docs'/name,stage/'docs'/name)
    shutil.copyfile(W/'src/utilities/display-settings/settings.c',stage/'source/display-settings.c')
    for p in W.glob('LICENSE*'):
        if p.is_file():shutil.copyfile(p,stage/'licenses'/p.name)
    m=tester_bundle.collect(stage,'windows-e-preview')
    m['limits']='Private same-owner E/720p installation snapshot. Includes Windows/profile/licensing data; not sanitized for public redistribution. Integrity checked, new-console boot and restore untested. No RCT game assets, EEPROM, BIOS or dashboard included.'
    plan=Path('C:/xwn587/windows-plan001.json');assert not plan.exists();plan.write_text(json.dumps(m,indent=2)+'\n')
    # Preserve exact ordinary startup bytes and its two external dependencies.
    startup='E/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'
    assert sha(stage/startup)==sha(src/startup)
    assert (dep/'display-settings.exe').is_file() and (dep/'outline-applied.txt').is_file()
    r.update(completed=True,files=len(m['files']),directories=len(m['directories']),console_bytes=sum(x['bytes'] for x in m['files'] if x['path'].startswith('E/')),plan=str(plan),plan_sha256=sha(plan),startup_unchanged=True)
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
