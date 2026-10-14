"""SPDX-License-Identifier: MIT
Guarded boot-mode selector for the existing E installation. Never launches Xbox.
Only dashboard E paths are allowed. Keep the policy with the matching package.
"""
import argparse,ftplib,hashlib,io,json,os
from pathlib import Path

TARGET='/E/Applications/XWNEBoot/default.xbe'
ALLOWED={TARGET,'/E/Applications/XWNEBoot/freeldr.sys',
         '/E/Applications/XWNEBoot/rosload.exe','/E/Applications/XWNEBoot/loader/xboxbvid.dll',
         '/E/winnt/system32/xwnown.dll','/E/winnt/system32/drivers/xboxvnt5.sys'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def require(v,msg):
    if not v:raise ValueError(msg)
def read_json(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save_new(p,r):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
def fetch(ftp,path):
    require(path in ALLOWED,'Path outside E display allowlist');out=io.BytesIO()
    def take(b):
        require(out.tell()+len(b)<=1024*1024,'Unexpected file size');out.write(b)
    ftp.retrbinary('RETR '+path,take,65536);return out.getvalue()
def store(ftp,data):
    require(0<len(data)<1024*1024,'Invalid launcher size')
    for at in range(0,len(data),32768):
        ftp.storbinary(('STOR ' if at==0 else 'APPE ')+TARGET,io.BytesIO(data[at:at+32768]),1024)
    require(fetch(ftp,TARGET)==data,'Launcher readback mismatch')
def validate_policy(policy):
    require(policy['target']==TARGET and set(policy['prerequisites'])==ALLOWED-{TARGET},'Wrong installation/policy')
    require(set(policy['profiles'])=={'720p','1080i'},'Unexpected profile set')
    for row in list(policy['profiles'].values())+list(policy['prerequisites'].values()):
        require(len(row['sha256'])==64 and all(c in '0123456789abcdef' for c in row['sha256']) and 0<row['bytes']<1024*1024,'Invalid pin')
def inspect(ftp,policy):
    validate_policy(policy)
    for path,row in policy['prerequisites'].items():
        b=fetch(ftp,path);require(len(b)==row['bytes'] and sha(b)==row['sha256'],'Prerequisite mismatch: '+path)
    current=fetch(ftp,TARGET);modes=[n for n,r in policy['profiles'].items() if len(current)==r['bytes'] and sha(current)==r['sha256']]
    require(len(modes)==1,'Unrecognized current launcher; no write permitted')
    return modes[0],current
def apply(ftp,policy,mode,data,receipt):
    validate_policy(policy);require(mode in policy['profiles'],'Unknown mode');row=policy['profiles'][mode]
    require(len(data)==row['bytes'] and sha(data)==row['sha256'],'Local launcher does not match policy')
    current,old=inspect(ftp,policy);receipt=Path(receipt)
    require(not receipt.exists(),'Receipt already exists; never overwrite a rollback')
    receipt.mkdir(parents=True);(receipt/'before.xbe').write_bytes(old)
    require((receipt/'before.xbe').read_bytes()==old,'Rollback readback failed')
    save_new(receipt/'intent.json',dict(target=TARGET,from_mode=current,to_mode=mode,before_sha256=sha(old),after_sha256=sha(data),no_boot=True))
    mutation_started=False
    try:
        # Recheck immediately before the sole remote mutation.
        require(inspect(ftp,policy)==(current,old),'Remote state changed')
        if old!=data:
            mutation_started=True;store(ftp,data)
        save_new(receipt/'result.json',dict(applied=True,changed=old!=data,readback_sha256=sha(fetch(ftp,TARGET)),no_boot=True))
    except BaseException as exc:
        error=dict(applied=False,error=type(exc).__name__,rollback_verified=False)
        if mutation_started:
            try:store(ftp,old);error['rollback_verified']=True
            except BaseException as restore_error:error['restore_error']=type(restore_error).__name__
        save_new(receipt/'result.json',error);raise
    return dict(mode=mode,receipt=str(receipt),reboot_required=True,no_boot=True)
def restore(ftp,policy,receipt):
    receipt=Path(receipt);intent=read_json(receipt/'intent.json');old=(receipt/'before.xbe').read_bytes()
    require(intent['target']==TARGET and sha(old)==intent['before_sha256'],'Invalid rollback receipt')
    require(not (receipt/'restore-result.json').exists(),'Restore already recorded')
    mode,current=inspect(ftp,policy)
    require(sha(current) in [intent['before_sha256'],intent['after_sha256']],'Another profile change occurred')
    require(sha(old)==policy['profiles'][intent['from_mode']]['sha256'],'Rollback not in policy')
    store(ftp,old);save_new(receipt/'restore-result.json',dict(restored=True,sha256=sha(old),no_boot=True))
    return dict(restored=True,mode=intent['from_mode'],no_boot=True)
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['inspect','apply','restore']);p.add_argument('--policy',type=Path,required=True)
    p.add_argument('--profile',choices=['720p','1080i']);p.add_argument('--launcher',type=Path);p.add_argument('--receipt',type=Path);a=p.parse_args()
    policy=read_json(a.policy);validate_policy(policy)
    if a.action=='apply':require(a.profile and a.launcher and a.receipt,'apply needs profile, launcher and fresh receipt')
    if a.action=='restore':require(a.receipt,'restore needs receipt')
    with ftplib.FTP() as ftp:
        ftp.connect(os.environ['XWN_FTP_HOST'],timeout=15);ftp.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        if a.action=='inspect':mode,b=inspect(ftp,policy);r=dict(mode=mode,sha256=sha(b),target=TARGET,no_boot=True)
        elif a.action=='apply':r=apply(ftp,policy,a.profile,a.launcher.read_bytes(),a.receipt)
        else:r=restore(ftp,policy,a.receipt)
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
