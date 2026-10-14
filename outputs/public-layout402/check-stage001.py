import hashlib,json,subprocess
from pathlib import Path
names=subprocess.check_output(['git','diff','--cached','--name-only','-z']).decode().rstrip('\0').split('\0')
selected=[p for p in names if p.startswith(('src/','LICENSES/','upstream/','outputs/public-layout402/')) or p in ['tools/xwn.py','tests/test_xwn.py']]
proc=subprocess.run(['git','cat-file','--batch'],input=''.join(':'+p+'\n' for p in selected).encode(),stdout=subprocess.PIPE,check=True)
data=proc.stdout; at=0; hashes={}
for p in selected:
    end=data.index(b'\n',at); header=data[at:end].split(); assert len(header)==3,header
    size=int(header[2]); start=end+1; blob=data[start:start+size]; at=start+size+1
    assert blob==Path(p).read_bytes(),p
    hashes[p]=hashlib.sha256(blob).hexdigest()
assert at==len(data)
Path('outputs/public-layout402/stage-exact001.json').write_text(json.dumps({'files':len(hashes),'byte_exact':True,'sha256':hashes},indent=2)+'\n')
print('Exact staged files:',len(hashes))
