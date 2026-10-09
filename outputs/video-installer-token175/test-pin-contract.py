"""Exercise actual observer pin function against cold PE and damaged/unavailable identities."""
import ast,hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=k/'trace.py';tree=ast.parse(source.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='pin')
meta=json.loads((k/'sites.json').read_text());pe=pefile.PE(str(k/'artifacts/ntdll.dll'));base=pe.OPTIONAL_HEADER.ImageBase
site=next(v for v in meta['sites'] if v['name']=='LdrInitializeThunk')
class Image:
    def __init__(self):self.data=bytearray(pe.get_memory_mapped_image());self.header_missing=False
    def read(self,a,n):
        off=a-base
        if self.header_missing and off<4096:raise AssertionError('E14')
        assert 0<=off and off+n<=len(self.data)
        return bytes(self.data[off:off+n])
image=Image();loader=None
ns=dict(pes={'ntdll.dll':pe},g=image,struct=struct,kernel=None,review=meta,r={'pins':[]},
        u32=lambda a:struct.unpack('<I',image.read(a,4))[0],module_at=lambda a,w:loader)
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),ns)
checks=[]
def attempt(label,expected):
    try:ns['pin'](site,{});passed=True
    except AssertionError:passed=False
    assert passed==expected,label;checks.append(dict(case=label,pin_accepted=passed))
attempt('early loader inventory unavailable but exact metadata/resident code',True)
loader=dict(name='ntdll.dll',base=base,size=pe.OPTIONAL_HEADER.SizeOfImage)
attempt('actual loader plus exact metadata/code',True)
image.header_missing=True;attempt('actual loader and code with nonresident header',True)
loader=None;attempt('no loader and nonresident header',False)
image.header_missing=False
nt=struct.unpack_from('<I',image.data,60)[0];image.data[nt+8]^=1
attempt('uninitialized loader and wrong timestamp',False);image.data[nt+8]^=1
image.data[site['rva']]^=1;attempt('correct metadata but changed resident code',False)
image.data[site['rva']]^=1
dest=k/'pin-contract-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,checks=checks,guest_access=False,
    pins={'trace.py':sha(source),'sites.json':sha(k/'sites.json'),'test-pin-contract.py':sha(Path(__file__))}),indent=2)+'\n')
print('6 actual-function identity/residency contract checks PASS; no guest')
