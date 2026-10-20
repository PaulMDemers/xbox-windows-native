"""Independently decode original control's COFF symbols; no guest self-report trust."""
import hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'binary-ranges001.json';assert not out.exists()
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
build=json.loads((K/'build001.json').read_text());row=next(v for v in build['rows'] if v['path'].endswith('/subject.exe'))
p=Path(row['path'].replace('/mnt/c/','C:/'));data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
pe=pefile.PE(data=data);offset=pe.FILE_HEADER.PointerToSymbolTable;count=pe.FILE_HEADER.NumberOfSymbols
assert offset>0 and 0<count<10000 and offset+count*18+4<=len(data)
sbase=offset+count*18;length=struct.unpack_from('<I',data,sbase)[0];assert 4<=length and sbase+length<=len(data)
need=['_arith619','_arith_end619','_copy619','_copy_end619'];found={};i=0
while i<count:
 off=offset+i*18;name=data[off:off+8];value,section,typ,storage,aux=struct.unpack_from('<IhHBB',data,off+8)
 if name[:4]==b'\0'*4:
  index=struct.unpack_from('<I',name,4)[0];assert 4<=index<length
  end=data.index(b'\0',sbase+index,sbase+length);name=data[sbase+index:end]
 else:name=name.rstrip(b'\0')
 text=name.decode('ascii')
 if text in need:
  assert text not in found and 1<=section<=len(pe.sections) and storage==2
  sec=pe.sections[section-1];assert sec.Characteristics&0x20000000 and value<sec.Misc_VirtualSize
  found[text]=pe.OPTIONAL_HEADER.ImageBase+sec.VirtualAddress+value
 assert i+1+aux<=count;i+=1+aux
assert set(found)==set(need)
ranges=[found[n] for n in need];assert ranges[0]<ranges[1]<=ranges[2]<ranges[3]
out.write_text(json.dumps(dict(passed=True,subject_sha256=row['sha256'],ranges=ranges,symbols=found,scope='Independent PE/COFF symbol decoding of original assembly ranges.'),indent=2)+'\n')
print(json.dumps(found))
