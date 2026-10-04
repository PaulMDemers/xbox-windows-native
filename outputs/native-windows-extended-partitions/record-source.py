"""Record and verify the isolated 0059 + extended partition/probe series."""
import pathlib,subprocess,json
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
src='/home/paul/xbox-windows-native/sources/reactos-extended';kit=root/'outputs/native-windows-extended-partitions'
def git(*args):return subprocess.check_output(['git','-C',src,*args])
base=json.loads((root/'outputs/native-windows-fatx-name-boundary/patch-check-0059.json').read_text())
old='e56f18e02d87f719cd6fbae5ce655174d4fbcde5'
git('add','boot/freeldr/freeldr/bootmgr.c','boot/freeldr/freeldr/include/xwnextended.h','boot/freeldr/freeldr/rosload.cmake','boot/freeldr/freeldr/pcat.cmake')
tree=git('write-tree').decode().strip()
p='outputs/native-windows-extended-partitions/0064-extended-read-preflight.patch'
(root/p).write_bytes(git('diff','--cached','--binary',old))
for num,result,extra in [('0063',old,[]),('0064',tree,[p])]:
 record=dict(base_commit=base['base_commit'],previous_tree=base['result_tree'] if num=='0063' else old,result_tree=result,patches=base['patches']+['outputs/native-windows-extended-partitions/0063-validated-extended-partition-table.patch']+extra)
 manifest=kit/('patch-check-'+num+'.json');manifest.write_text(json.dumps(record,indent=2)+'\n')
 subprocess.run(['python3',str(root/'tools/apply-series.py'),'--source',src,'--manifest',str(manifest),'--verify-only'],check=True)
print(tree)
