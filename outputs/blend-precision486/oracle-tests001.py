"""Synthetic transport and arithmetic discriminators fixed before guest execution."""
import hashlib,json,struct,sys,uuid
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'tools'))
import graphics_precision as g
out=K/'oracle-tests001.json';assert not out.exists();negative=0
def images(model):
    result=[]
    for stage in g.STAGES:
        b=bytearray(struct.pack('<I',g.BG)*4096)
        for y in range(8,56):
            for x in range(8,64-y):struct.pack_into('<I',b,(y*64+x)*4,g.expected(stage,model))
        result.append(b)
    return result
def refused(fn,*args):
    global negative
    try:fn(*args)
    except (ValueError,KeyError):negative+=1
    else:raise AssertionError('negative accepted')
for model in g.MODELS:assert g.pixels(*images(model))['matching_model']==model
f={k:'0' for k in g.HRESULTS}
f.update(schema='xwn-d3d-precision-1',backend='default',scope='offscreen-rgb-software',width='64',height='64',exit='0',result='CAPTURED',end='complete',modules='1',**{'os.major':'5','os.minor':'0','os.build':'2195','window.created':'1','ddraw.load':'1','ddraw.entry':'1','ddraw.unload':'1','enum.matches':'1','enum.error':'0','enum.count':'1','vertex.stride':'20','vertex.fvf':'68','modules.ok':'1','modules.end_error':'18','release.device':'0','release.target':'0','release.ddraw':'0','release.d3d':'1','module0.path':b'C:\\WINNT\\system32\\ddraw.dll'.hex(),'module0.bytes':'4096'})
caps=bytearray(236);caps[196:212]=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356').bytes_le
for offset,value in [(76,16),(80,32),(116,256)]:struct.pack_into('<I',caps,offset,value)
f['device.caps']=caps.hex();f['vertices']=b''.join(struct.pack('<ffffI',x,y,.5,1,(a<<24)|g.FG) for a in (85,85,0,85,170,255,85) for x,y in ((8,8),(56,8),(8,56))).hex()
for i,stage in enumerate(g.STAGES):
    f.update({stage+'.valid':'1',stage+'.pitch':'256',stage+'.caps':str(0x2840),stage+'.alpha':str(g.ALPHAS[i]),stage+'.blend':str(int(i!=7)),stage+'.src':str(g.SOURCES[i]),stage+'.dest':str(g.DESTINATIONS[i])})
encode=lambda f:''.join(k+'='+v+'\r\n' for k,v in f.items()).encode()
frames=images('separate_floor256');raw=encode(f);assert g.validate(raw,frames,'default',0)['passed']
for key in f:
    bad=dict(f);del bad[key];refused(g.validate,encode(bad),frames,'default',0);refused(g.validate,raw+(key+'='+f[key]+'\r\n').encode(),frames,'default',0)
for key in g.HRESULTS:
    bad=dict(f);bad[key]='1';refused(g.validate,encode(bad),frames,'default',0)
for i in range(420):
    bad=dict(f);v=bytearray.fromhex(f['vertices']);v[i]^=1;bad['vertices']=v.hex();refused(g.validate,encode(bad),frames,'default',0)
metadata=negative
for frame in frames:
    for y in range(64):
        for x in (0,16,63):
            for channel in range(3):
                at=(y*64+x)*4+channel;frame[at]^=16;refused(g.pixels,*frames);frame[at]^=16
pixels=negative-metadata
mixed=list(frames);mixed[4]=images('combined_floor256')[4];refused(g.pixels,*mixed)
for index in range(8):refused(g.pixels,*(frames[:index]+frames[index+1:]))
out.write_text(json.dumps(dict(passed=True,models=list(g.MODELS),metadata_negatives=metadata,pixel_negatives=pixels,total_negatives=negative,modelled_images_only=True,source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),K/'graphics_precision.py']}),indent=2)+'\n')
print('PASS arithmetic model/transport negatives:',negative)
