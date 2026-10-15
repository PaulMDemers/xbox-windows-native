import hashlib,json,os,subprocess,urllib.request,time
from pathlib import Path
root=Path('/home/paul/xbox-windows-native/release-readiness403-dependencies001')
root.mkdir(exist_ok=False)
report={'anonymous':True,'sources':{},'downloads':{}}
env=os.environ.copy()
env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL='/dev/null',GIT_TERMINAL_PROMPT='0',GIT_ASKPASS='/bin/false')
for k in list(env):
    if k.startswith('GIT_CONFIG_KEY_') or k.startswith('GIT_CONFIG_VALUE_') or k=='GIT_CONFIG_COUNT':del env[k]
for name,url,commit in [('reactos','https://github.com/DistroHopper39B/reactos.git','afc0127e8f937ab68503d715d948844973756aa1'),('cromwell','https://github.com/PaulMDemers/cromwell.git','9fc54d0c7cbed7bc3c70373642d833684853011f')]:
    dest=root/name
    subprocess.run(['git','init','--bare','-q',str(dest)],check=True,env=env)
    with (root/(name+'.log')).open('w') as log:
        r=subprocess.run(['git','-c','credential.helper=','-c','http.extraHeader=','-c','core.askPass=','-c','http.version=HTTP/1.1','-C',str(dest),'fetch','--depth=1',url,commit],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600)
    row={'url':url,'commit':commit,'exit_code':r.returncode}
    if not r.returncode:
        row['resolved_commit']=subprocess.check_output(['git','-C',str(dest),'rev-parse','FETCH_HEAD'],env=env,text=True).strip()
        row['tree']=subprocess.check_output(['git','-C',str(dest),'rev-parse','FETCH_HEAD^{tree}'],env=env,text=True).strip()
        assert row['resolved_commit']==commit
    report['sources'][name]=row
    (root/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(name,row,flush=True)
url='https://download.reactos.org/reactos/RosBE-Unix/2.2.1/RosBE-Unix-2.2.1.tar.bz2'
try:
    h=hashlib.sha256();count=0
    with urllib.request.urlopen(url,timeout=45) as response,(root/'RosBE-Unix-2.2.1.tar.bz2').open('xb') as out:
        final=response.url
        while chunk:=response.read(1024**2):
            count+=len(chunk)
            if count>512*1024**2:raise ValueError('Download size bound')
            h.update(chunk);out.write(chunk)
    report['downloads']['rosbe']={'url':url,'final_url':final,'bytes':count,'sha256':h.hexdigest(),'matches_pin':h.hexdigest()=='d720c0a77dc08c6da3929fd282de3fe7af6d697b6fb104889a0362e770742565'}
except Exception as e:report['downloads']['rosbe']={'url':url,'error':repr(e)}
(root/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['downloads'],flush=True)
