"""Verify the full patch chain against the pinned base in a disposable index."""
import json,os,pathlib,subprocess,tempfile
source=pathlib.Path('/home/paul/xbox-windows-native/sources/reactos')
out=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5-interrupts')
patches=[out.parent/'native-windows-prebuild/patches/0005-native-io-cumulative.patch',out.parent/'native-windows-nt5/0006-nt5-hal-experimental.patch',out/'0007-nt5-interrupt-boundary.patch']
with tempfile.TemporaryDirectory(prefix='xwn-boundary-index-') as temp:
 env=os.environ.copy();env['GIT_INDEX_FILE']=str(pathlib.Path(temp)/'index')
 def git(*args):return subprocess.check_output(['git','-C',str(source),*map(str,args)],env=env,text=True)
 git('read-tree','afc0127e8f937ab68503d715d948844973756aa1')
 for p in patches:git('apply','--cached','--check',p);git('apply','--cached',p)
 git('diff','--cached','--check');git('diff','--exit-code')
 tree=git('write-tree').strip()
subprocess.run(['git','-C',str(source),'apply','--reverse','--check',str(patches[-1])],check=True)
report={'base':'afc0127e8f937ab68503d715d948844973756aa1','patch_order':[str(p.relative_to(out.parent)) for p in patches],
 'base_applicability':True,'current_tree_matches_full_patch_chain':True,'result_tree':tree,
 'current_tree_reverse_check':True,'whitespace_check':True}
(out/'patch-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
