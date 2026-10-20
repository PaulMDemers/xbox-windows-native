"""Adversarial mutations of the immutable cold trace, no new runtime."""
import hashlib,json
from pathlib import Path
from trace_oracle002 import validate
K=Path(__file__).resolve().parent;out=K/'oracle-tests002.json';assert not out.exists()
build=json.loads((K/'build002.json').read_text());p=Path('C:/xwn605/pc001/cold1-002/files/xwn605/trace.txt')
text=p.read_text();lines=text.splitlines();base=build['target_image_base'];size=build['target_image_size']
positive=validate(text,base,size)
def index(kind):return next(i for i,l in enumerate(lines) if l.startswith(kind+' '))
def change(i,field,value):
 a=lines.copy();v=a[i].split();v[field]=value;a[i]=' '.join(v);return '\n'.join(a)+'\n'
ri=index('RETURN');oi=index('OBJECT');bi=index('BP');ci=index('CAP')
null_out=next(i for i,l in enumerate(lines) if l.startswith('OUTPUT ') and int(l.split()[-1],16))
width=next(i for i,l in enumerate(lines) if l.startswith('ARGS ') and l.split()[2]=='00000009')
variants={
 'missing_return':'\n'.join(lines[:ri]+lines[ri+1:])+'\n',
 'duplicate_return':'\n'.join(lines[:ri]+[lines[ri]]+lines[ri:])+'\n',
 'wrong_return_stack':change(ri,5,'00000000'),
 'unknown_thread':change(ri,2,'ffffffff'),
 'unknown_owner':change(bi,4,'00000000'),
 'null_success_output':change(null_out,4,'00000000'),
 'false_object':change(oi,2,'00000000'),
 'wrong_vtable_length':change(oi,4,'00000016'),
 'wrong_copy_width':change(width,6,'00000007'),
 'false_cap':change(ci,2,'0000001f'),
 'duplicate_cap':'\n'.join(lines[:ci]+[lines[ci]]+lines[ci:])+'\n',
 'unknown_exception':text.replace('TOTAL ','EXCEPTION c0000005 1 1\nTOTAL '),
 'missing_end':'\n'.join(lines[:-1])+'\n',
 'duplicate_end':text+lines[-1]+'\n',
}
di=index('DIB')
variants.update({
 'missing_header':'\n'.join(lines[:di]+lines[di+1:])+'\n',
 'duplicate_header':'\n'.join(lines[:di]+[lines[di]]+lines[di:])+'\n',
 'wrong_header_address':change(di,2,'00000000'),
 'false_header_status':change(di,3,'00000003'),
 'wrong_header_length':change(di,4,'00000009'),
 'wrong_stride':change(di,5,'0000001f'),
 'wrong_extent':change(di,6,'000000ff'),
 'wrong_signed_height':change(di,9,'00000008'),
 'wrong_header_bpp':change(di,10,'00180001'),
})
rejected=[]
for name,value in variants.items():
 try:validate(value,base,size)
 except (AssertionError,ValueError,KeyError,UnicodeError,IndexError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,positive=positive,rejected=rejected,trace_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Cold-trace oracle mutation controls; not new execution.'),indent=2)+'\n')
print('604 oracle positive and23 rejection controls passed')
