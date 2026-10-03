"""Read-only patch applicability check using a disposable Git index."""
import json,os,pathlib,subprocess,tempfile
source=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos')
out=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5')
patches=[out.parent/'native-windows-prebuild/patches/0005-native-io-cumulative.patch',out/'0006-nt5-hal-experimental.patch']
with tempfile.TemporaryDirectory(prefix='xwn-index-') as temp:
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(pathlib.Path(temp)/'index')
    def git(*args):subprocess.run(['git','-C',str(source),*map(str,args)],env=env,check=True)
    git('read-tree','afc0127e8f937ab68503d715d948844973756aa1')
    for patch in patches:
        git('apply','--cached','--check',patch);git('apply','--cached',patch)
    git('diff','--cached','--check')
subprocess.run(['git','-C',str(source),'apply','--reverse','--check',str(patches[-1])],check=True)
report={'base':'afc0127e8f937ab68503d715d948844973756aa1','patch_order':[p.name for p in patches],
        'base_applicability':True,'current_tree_reverse_check':True,'whitespace_check':True}
(out/'patch-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
