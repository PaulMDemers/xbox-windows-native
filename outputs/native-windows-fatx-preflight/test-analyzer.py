"""Challenge the read-only analyzer with known allocation damage and incomplete captures."""
import hashlib,json,pathlib,struct,subprocess,sys,tempfile
k=pathlib.Path(__file__).resolve().parent;source=k/'artifacts/emulator-001'
original={n:(source/n).read_bytes() for n in ['fat-metadata.bin','directories.bin','snapshot.txt']}
rows=original['directories.bin'];driver=[];others=[]
for at in range(0,len(rows),80):
 if struct.unpack_from('<I',rows,at)[0]!=2:continue
 e=rows[at+16:at+80];name=e[2:2+e[0]].decode('latin1');first,size=struct.unpack_from('<II',e,44)
 if name.lower()=='xwnfatx.sys':driver.append((at,first,size))
 elif not e[1]&16 and first and size:others.append((at,first,size))
assert len(driver)==1;offset,cluster,size=driver[0];results=[]
for case in ['clean','free-driver-chain','crosslink','missing-summary','incomplete-log']:
 with tempfile.TemporaryDirectory(prefix='xwn-preflight-test-') as temp:
  capture=pathlib.Path(temp);data={n:bytearray(b) for n,b in original.items()}
  if case=='free-driver-chain':struct.pack_into('<I',data['fat-metadata.bin'],4096+cluster*4,0)
  if case=='crosslink':struct.pack_into('<I',data['directories.bin'],others[0][0]+16+44,cluster)
  if case=='missing-summary':data['directories.bin']=data['directories.bin'][:-80]
  if case=='incomplete-log':data['snapshot.txt']=b'SNAPSHOT_COMPLETE success=0\r\n'
  for n,b in data.items():(capture/n).write_bytes(b)
  out=capture/'result.json';process=subprocess.run([sys.executable,str(k/'analyze.py'),'--capture',str(capture),'--output',str(out)],capture_output=True,text=True)
  result=json.loads(out.read_text()) if out.exists() else None
  if case=='clean':assert process.returncode==0 and result['allocation_consistent']
  elif case in ['missing-summary','incomplete-log']:assert process.returncode!=0
  else:
   assert process.returncode==0 and not result['allocation_consistent']
   kind='invalid-chain-terminal' if case=='free-driver-chain' else 'crosslink'
   assert any(e['kind']==kind for e in result['errors'])
  results.append(dict(case=case,detected_as_expected=True,errors=result['errors'][:8] if result else 'Capture rejected'))
assert all((source/n).read_bytes()==b for n,b in original.items())
r=dict(scope=__doc__,source_preserved=True,source_hashes={n:hashlib.sha256(b).hexdigest() for n,b in original.items()},cases=results,passed=True)
(k/'analyzer-tests.json').write_text(json.dumps(r,indent=2)+'\n');print('All five analyzer cases PASS; source unchanged')
