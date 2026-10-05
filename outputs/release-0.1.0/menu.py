"""Add a manual Windows item at the root of the observed UnleashX menu."""
import datetime, hashlib, io, json, os, pathlib, sys, xml.etree.ElementTree as ET
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from capture import FTP, get, DEST, KIT, STAGE
sha=lambda b:hashlib.sha256(b).hexdigest()
config='/C/Dashboard/config.xml';backup='/C/Dashboard/config.win010.bak';temp='/C/Dashboard/config.win010.new'
target=r'E:\Applications\XWNFBoot\default.xbe'
report=KIT/'menu-install.json'
assert not report.exists(), 'Existing operation: inspect instead of blindly repeating'
assert json.loads((KIT/'capture-summary.json').read_text())['baseline_checks']
def put(f,p,data):
    f.storbinary('STOR '+p,io.BytesIO(data),1024)
    assert get(f,p)==data,p
def absent(f,p):
    try: get(f,p)
    except Exception as e:
        from ftplib import error_perm
        if isinstance(e,error_perm) and str(e).startswith('550'):return
        raise
    raise AssertionError('Preserve existing '+p)
def parse(b):return ET.fromstring(b.rstrip(b'\x00'))
with FTP() as f:
    f.connect('192.168.50.242',timeout=20);f.login('xbox',os.environ['XWN_FTP_PASSWORD'])
    before=get(f,config)
    assert before==(STAGE/'C/Dashboard/config.xml').read_bytes(), 'Config changed since release capture'
    assert get(f,'/E/Applications/XWNFBoot/default.xbe')==(STAGE/'E/Applications/XWNFBoot/default.xbe').read_bytes()
    root=parse(before);menu=root.find('Menu');assert menu is not None
    assert not any((i.text or '').strip().lower()=='windows' or i.get('Action','').lower()==target.lower() for i in menu.findall('Item'))
    assert before.count(b'<Menu>')==1
    newline=b'\r\n' if b'\r\n' in before else b'\n'
    addition=newline+b'\t\t<Item Action="'+target.encode()+b'">Windows</Item>'
    after=before.replace(b'<Menu>',b'<Menu>'+addition,1)
    changed=parse(after);items=changed.find('Menu').findall('Item')
    assert len([i for i in items if i.text=='Windows' and i.get('Action')==target])==1
    changed.find('Menu').remove(items[0])
    assert ET.tostring(changed)==ET.tostring(root), 'Unrelated menu/settings changed'
    absent(f,backup);absent(f,temp)
    local=DEST/'dashboard-menu';local.mkdir(exist_ok=True)
    (local/'config-before.xml').write_bytes(before);(local/'config-after.xml').write_bytes(after)
    r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),config=config,backup=backup,
           staged=temp,action=target,label='Windows',root_level=True,before_sha256=sha(before),after_sha256=sha(after),
           local_backup=str(local/'config-before.xml'),automatic_launch=False,console_restarted=False,installed=False)
    def save():report.write_text(json.dumps(r,indent=2)+'\n')
    save();put(f,temp,after)
    assert get(f,config)==before,'Concurrent config change'
    f.rename(config,backup)
    try:f.rename(temp,config)
    except Exception:
        f.rename(backup,config);r['rolled_back']=True;save();raise
    assert get(f,config)==after and get(f,backup)==before
    r.update(installed=True,readback_verified=True,reload_visibility='Pending next dashboard reload/user observation')
    save();print(json.dumps(r,indent=2))
