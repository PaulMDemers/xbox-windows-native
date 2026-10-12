"""Complete the remaining source edit after preserved preparation001 anchor refusal."""
import difflib,hashlib,json,pathlib,subprocess,shutil
K=pathlib.Path(__file__).resolve().parent
out=pathlib.Path('/home/paul/xbox-windows-native/build/hd-reservation300-build001')
private=pathlib.Path('/mnt/e/xwn300/prior-source001');assert not private.exists()
assert json.loads((K/'source-review001.json').read_text())['status']=='failed'
assert not (K/'source-review002.json').exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
snap={};changes={};private.mkdir(parents=True)
roots={'reactos':out/'source','cromwell':out/'cromwell'}
expected={'reactos':'53e9aedc58152d03116c00579185000483379837','cromwell':'d8de181fb893f0360e8e8e947b5768b25101e678'}
originals={}
for label,root in roots.items():
 assert subprocess.check_output(['git','-C',str(root),'write-tree'],text=True).strip()==expected[label]
 names=subprocess.check_output(['git','-C',str(root),'diff','--name-only']).decode().splitlines()
 names+=subprocess.check_output(['git','-C',str(root),'ls-files','--others','--exclude-standard']).decode().splitlines()
 if label=='cromwell':names+=['boot/LoadReactOS.c']
 for n in sorted(set(names)):
  p=root/n;b=p.read_bytes();q=private/label/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b);assert q.read_bytes()==b
  snap[label+'/'+n]=sha(b)
  got=subprocess.run(['git','-C',str(root),'show',':'+n],capture_output=True)
  assert got.returncode==0 or n=='sdk/include/reactos/drivers/xbox/xwn_hd_layout.h'
  originals[label,n]=got.stdout if got.returncode==0 else b''
for n in ['prepare-source.py','source-review001.json']:
 shutil.copyfile(K/n,private/n);snap[n]=sha((K/n).read_bytes())
(K/'prior-source001.json').write_text(json.dumps(dict(private=str(private),files=snap),indent=2)+'\n')
p=roots['cromwell']/'boot/LoadReactOS.c';s=p.read_text()
anchor='\tif (mbHeader == NULL)\n\t\treturn;\n\n\t/* Save needed values'
assert s.count(anchor)==1
s=s.replace(anchor,'''\tif (mbHeader == NULL)
\t\treturn;
#ifdef XWN_HD_RESERVATION
\tif (xbox_ram != 64) {
\t\tprintk("HD reservation requires a 64 MB console.\\n");
\t\treturn;
\t}
#endif

\t/* Save needed values''');p.write_text(s)
r=dict(status='source_prepared',resume_of='source-review001.json',original_failure_preserved=True,changes={},trees={})
for label,root in roots.items():
 diff=[]
 for (l,n),before in originals.items():
  if l!=label:continue
  after=(root/n).read_bytes();r['changes'][label+'/'+n]=dict(before=sha(before),after=sha(after))
  diff.extend(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+n if before else '/dev/null',tofile='b/'+n))
 (K/(label+'-reservation.patch')).write_text(''.join(diff))
 subprocess.run(['git','-C',str(root),'add','-A'],check=True)
 r['trees'][label]=subprocess.check_output(['git','-C',str(root),'write-tree'],text=True).strip()
r['patches']={p.name:sha(p.read_bytes()) for p in K.glob('*-reservation.patch')}
(K/'source-review002.json').write_text(json.dumps(r,indent=2)+'\n');print('Prepared exact source; prior failed anchor preserved')
