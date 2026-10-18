"""Synthetic transport/pixel negatives, before any guest execution."""
import hashlib,json,struct,sys,unittest
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_triangle as g
out=K/'oracle-tests001.json';assert not out.exists()
suite=unittest.defaultTestLoader.discover(str(W/'tests'),pattern='test_graphics_triangle.py')
result=unittest.TextTestRunner(verbosity=2).run(suite);assert result.wasSuccessful()
f={k:'0' for k in g.HRESULTS}
f.update(schema='xwn-d3d-triangle-1',backend='default',scope='offscreen-rgb-software',width='64',height='64',exit='0',result='CAPTURED',end='complete')
f.update({'os.major':'5','os.minor':'0','os.build':'2195','window.created':'1','ddraw.load':'1','ddraw.entry':'1','ddraw.unload':'1','enum.matches':'1','enum.error':'0','enum.count':'1','vertex.stride':'20','vertex.fvf':'68','clear_capture.valid':'1','draw_capture.valid':'1','modules.ok':'1','modules.end_error':'18','release.device':'0','release.target':'0','release.ddraw':'0','release.d3d':'1','modules':'1','clear_capture.pitch':'256','draw_capture.pitch':'256','clear_capture.caps':str(0x2840),'draw_capture.caps':str(0x2840),'module0.path':b'C:\\WINNT\\system32\\ddraw.dll'.hex(),'module0.bytes':'4096'})
old=g.decode((K.parent/'d3d-discovery455/pc001-r06d.txt').read_bytes())
f['device.caps']=old['d0.raw']
f['vertices']=b''.join(struct.pack('<ffffI',x,y,.5,1,0xff40c080) for x,y in [(8,8),(56,8),(8,56)]).hex()
a=struct.pack('<I',g.BG)*4096;b=bytearray(a)
for y in range(8,56):
 for x in range(8,64-y):struct.pack_into('<I',b,(y*64+x)*4,g.FG)
encode=lambda f:(''.join(k+'='+v+'\r\n' for k,v in f.items())).encode()
raw=encode(f);assert g.validate(raw,a,b,'default',0)['passed'];rejected=0
def refuse(r=raw,c=a,d=b,backend='default',code=0):
 global rejected
 try:g.validate(r,c,d,backend,code)
 except (ValueError,KeyError,UnicodeError):rejected+=1
 else:raise AssertionError('negative accepted')
for key in f:
 bad=dict(f);del bad[key];refuse(encode(bad));refuse(raw+(key+'='+f[key]+'\n').encode())
for key in g.HRESULTS:
 bad=dict(f);bad[key]='1';refuse(encode(bad))
for key,value in [('module0.path',b'C:\\..\\ddraw.dll'.hex()),('enum.matches','2'),('modules','65'),('clear_capture.pitch','255'),('draw_capture.caps','64'),('exit','1'),('modules.ok','0'),('vertex.fvf','0')]:
 bad=dict(f);bad[key]=value;refuse(encode(bad))
for index in range(60):
 bad=dict(f);v=bytearray.fromhex(f['vertices']);v[index]^=1;bad['vertices']=v.hex();refuse(encode(bad))
for n in range(0,len(raw),17):refuse(raw[:n])
refuse(code=1);refuse(backend='hel');refuse(c=a[:-1]);refuse(d=b+b'\0')
record=dict(passed=True,synthetic_transport_rejections=rejected,synthetic_pixel_mutations_rejected=8192,unit_tests=result.testsRun,oracle_sha256=hashlib.sha256((W/'tools/graphics_triangle.py').read_bytes()).hexdigest(),scope='Synthetic frames/module metadata; capability bytes from closed455. No runtime evidence.')
out.write_text(json.dumps(record,indent=2)+'\n');print(record)
