"""Compose a new D3D presentation sample; old rung03/07 sources stay unchanged."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1];S=W/'src/samples/graphics-ladder'
p=(S/'present.c').read_text();t=(S/'triangle.c').read_text();g=(W/'tools/graphics_present.py').read_text()
pins={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [S/'present.c',S/'triangle.c',W/'tools/graphics_present.py']}
p=p.replace('Rung 03: an owned window/clipper/primary test. No exclusive mode or mode switch.','D3D7 software rendering to an owned window/clipper/primary. No mode switch.')
p=p.replace('#define COBJMACROS','#define DIRECT3D_VERSION 0x0700\n#define COBJMACROS').replace('#include <ddraw.h>','#include <ddraw.h>\n#include <d3d.h>\n#include <tlhelp32.h>')
p=p.replace('files[3]','files[4]').replace('XWNPresent03','XWND3DPresent08d').replace('XWN DirectDraw presentation','XWN D3D presentation')
a=t.index('static const GUID d3d7=');b=t.index('static VERTEX vertices[]',a)
decl=t[a:b]+'''static DWORD enumerated,matches,enum_error;
static D3DDEVICEDESC7 selected;
static int context;
static const DWORD foreground[]={0xff0000,0x00ff00,0xffffff,0xffff00};
static const DWORD background[]={0x00ffff,0xff00ff,0x0000ff,0};
'''
p=p.replace('static HANDLE logf=',decl+'static HANDLE logf=')
p=p.replace('char b[256];wsprintfA(b,"%s=%s\\r\\n",k,v);','char b[1100];if(lstrlenA(k)+lstrlenA(v)+4>=(int)sizeof(b)){io_error=1;return;}wsprintfA(b,"%s=%s\\r\\n",k,v);')
a=t.index('static int same(');b=t.index('static int put(',a);p=p.replace('static int put(',t[a:b]+'static int put(',1)
a=t.index('static void hex(');b=t.index('static int token(',a);p=p.replace('static int token(',t[a:b]+'static int token(',1)
a=t.index('static HRESULT CALLBACK enumerate(');b=t.index('static int format(',a);p=p.replace('static int inrect(',t[a:b]+'static int inrect(',1)
a=p.index('static DWORD pattern(');b=p.index('static HRESULT CALLBACK enumerate(',a)
p=p[:a]+'''static int allowed(unsigned x,unsigned y,DWORD rgb){
 if(x>=12&&y>=12&&6*x+7*y<=724)return rgb==foreground[stage];
 if(x<=4||y<=4||6*x+7*y>=828)return rgb==background[stage];
 return rgb==foreground[stage]||rgb==background[stage];
}
'''+p[b:]
p=p.replace('after?pattern(x,y,stage):0','after?source[y*TW+x]:0')
a=p.index('static int surface(');b=p.index('static int run(',a)
p=p[:a]+'''static int surface(IDirectDrawSurface7 *s,const DDPIXELFORMAT *pf,int post){
 DDSURFACEDESC2 d;DWORD x,y,bpp=pf->dwRGBBitCount/8,bad=0;int valid,ok;char label[64];
 zero(&d,sizeof(d));d.dwSize=sizeof(d);
 if(!scall(post?"post.lock":"source.lock",IDirectDrawSurface7_Lock(s,0,&d,DDLOCK_DONOTWAIT|DDLOCK_READONLY,0)))return 0;
 valid=d.lpSurface&&d.dwWidth==TW&&d.dwHeight==TH&&d.lPitch>0&&d.lPitch<=65536&&(DWORD)d.lPitch>=TW*bpp&&d.lPitch%(LONG)bpp==0&&d.ddpfPixelFormat.dwFlags==DDPF_RGB&&d.ddpfPixelFormat.dwRGBBitCount==pf->dwRGBBitCount&&d.ddpfPixelFormat.dwRBitMask==pf->dwRBitMask&&d.ddpfPixelFormat.dwGBitMask==pf->dwGBitMask&&d.ddpfPixelFormat.dwBBitMask==pf->dwBBitMask&&d.ddpfPixelFormat.dwRGBAlphaBitMask==0&&(d.ddsCaps.dwCaps&(DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN|DDSCAPS_3DDEVICE))==(DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN|DDSCAPS_3DDEVICE)&&!(d.ddsCaps.dwCaps&(DDSCAPS_VIDEOMEMORY|DDSCAPS_PRIMARYSURFACE));
 wsprintfA(label,"%s.layout",post?"post":"source");snum(label,valid);
 wsprintfA(label,"%s.pitch",post?"post":"source");snum(label,(DWORD)d.lPitch);
 if(valid)for(y=0;y<TH;y++)for(x=0;x<TW;x++){
  BYTE *q=(BYTE*)d.lpSurface+y*d.lPitch+x*bpp;DWORD v=bpp==2?*(WORD*)q:*(DWORD*)q;
  DWORD rgb=((v&pf->dwRBitMask)==pf->dwRBitMask?0xff0000UL:0)|((v&pf->dwGBitMask)==pf->dwGBitMask?0xff00UL:0)|((v&pf->dwBBitMask)==pf->dwBBitMask?255:0);
  DWORD native=((rgb&0xff0000)?pf->dwRBitMask:0)|((rgb&0xff00)?pf->dwGBitMask:0)|((rgb&255)?pf->dwBBitMask:0);
  if((v&(pf->dwRBitMask|pf->dwGBitMask|pf->dwBBitMask))!=native||!allowed(x,y,rgb)||(post&&source[y*TW+x]!=rgb))bad++;
  if(!post)source[y*TW+x]=rgb;
 }
 ok=scall(post?"post.unlock":"source.unlock",IDirectDrawSurface7_Unlock(s,0));
 wsprintfA(label,"%s.mismatches",post?"post":"source");snum(label,bad);
 if(valid&&ok&&!bad&&!put(files[post?3:0],source,sizeof(source)))return 0;
 return valid&&ok&&!bad;
}
static int render(IDirect3DDevice7 *dev){
 VERTEX v[]={{8,8,.5f,1,0},{120,8,.5f,1,0},{8,104,.5f,1,0}};unsigned i;char label[80];HRESULT hr;
 for(i=0;i<3;i++)v[i].color=0xff000000UL|foreground[stage];
 wsprintfA(label,"s%u.vertices",stage);hex(label,(BYTE*)v,sizeof(v));
 snum("foreground",foreground[stage]);snum("background",background[stage]);
 if(!scall("clear",IDirect3DDevice7_Clear(dev,0,0,D3DCLEAR_TARGET,background[stage],1,0)))return 0;
 if(!scall("scene.begin",IDirect3DDevice7_BeginScene(dev)))return 0;
 hr=IDirect3DDevice7_DrawPrimitive(dev,D3DPT_TRIANGLELIST,D3DFVF_XYZRHW|D3DFVF_DIFFUSE,v,3,0);
 i=scall("draw",hr);return scall("scene.end",IDirect3DDevice7_EndScene(dev))&&i;
}
'''+p[b:]
p=p.replace('HMODULE mod=0;IDirectDraw7 *dd=0;','HMODULE mod=0;IDirectDraw7 *dd=0;IDirect3D7 *d3d=0;IDirect3DDevice7 *dev=0;D3DVIEWPORT7 vp={0,0,TW,TH,0,1};')
p=p.replace('d.ddsCaps.dwCaps=DDSCAPS_OFFSCREENPLAIN|DDSCAPS_SYSTEMMEMORY;','d.ddsCaps.dwCaps=DDSCAPS_OFFSCREENPLAIN|DDSCAPS_SYSTEMMEMORY|DDSCAPS_3DDEVICE;')
anchor=' if(!call("clipper.create",'
pos=p.index(anchor)
setup=''' if(!call("d3d.query",IDirectDraw7_QueryInterface(dd,&d3d7,(void**)&d3d)))goto done;
 if(!call("enum.hr",IDirect3D7_EnumDevices(d3d,enumerate,&context)))goto done;
 number("enum.count",enumerated);number("enum.matches",matches);number("enum.error",enum_error);hex("selected.caps",(BYTE*)&selected,sizeof(selected));
 if(enum_error||matches!=1||(selected.dwDevCaps&(D3DDEVCAPS_HWRASTERIZATION|D3DDEVCAPS_HWTRANSFORMANDLIGHT))||!(selected.dwDeviceRenderBitDepth&(pf.dwRGBBitCount==16?DDBD_16:DDBD_32)))goto done;
 if(!call("device.create",IDirect3D7_CreateDevice(d3d,&selected.deviceGUID,src,&dev)))goto done;
 if(!call("viewport",IDirect3DDevice7_SetViewport(dev,&vp)))goto done;
'''
states=[('z','ZENABLE','FALSE'),('zwrite','ZWRITEENABLE','FALSE'),('lighting','LIGHTING','FALSE'),('cull','CULLMODE','D3DCULL_NONE'),('fill','FILLMODE','D3DFILL_SOLID'),('shade','SHADEMODE','D3DSHADE_FLAT'),('fog','FOGENABLE','FALSE'),('alpha','ALPHABLENDENABLE','FALSE'),('alphatest','ALPHATESTENABLE','FALSE'),('dither','DITHERENABLE','FALSE'),('specular','SPECULARENABLE','FALSE'),('antialias','ANTIALIAS','D3DANTIALIAS_NONE')]
for name,state,value in states:
 setup+=f' if(!call("state.{name}",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_{state},{value})))goto done;\n'
 setup+=f' {{DWORD value=0xffffffffUL;if(!call("get.{name}",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_{state},&value)))goto done;number("value.{name}",value);if(value!={value})goto done;}}\n'
setup+=' if(!call("texture0",IDirect3DDevice7_SetTexture(dev,0,0)))goto done;\n'
for name,index,state,value in [('stage0.op',0,'COLOROP','D3DTOP_SELECTARG1'),('stage0.arg',0,'COLORARG1','D3DTA_DIFFUSE'),('stage0.alpha',0,'ALPHAOP','D3DTOP_DISABLE'),('stage1.op',1,'COLOROP','D3DTOP_DISABLE')]:
 setup+=f' if(!call("{name}",IDirect3DDevice7_SetTextureStageState(dev,{index},D3DTSS_{state},{value})))goto done;\n'
p=p[:pos]+setup+p[pos:]
p=p.replace('!surface(src,&pf,1)||!surface(src,&pf,0)','!render(dev)||!surface(src,&pf,0)')
p=p.replace('Sleep(100);if(!capture(1,p))goto done;','Sleep(100);if(!capture(1,p)||!surface(src,&pf,1))goto done;')
p=p.replace(' ok=1;\ndone:\n if(primary&&cl)',' ok=modules();number("modules.ok",ok);\ndone:\n if(primary&&cl)')
p=p.replace(' if(src)number("release.source",',' if(dev){ULONG refs=IDirect3DDevice7_Release(dev);number("release.device",refs);clean&=refs==0;}\n if(src)number("release.source",')
p=p.replace(' if(dd)number("release.ddraw",',' if(d3d)number("release.d3d",IDirect3D7_Release(d3d));\n if(dd)number("release.ddraw",')
p=p.replace('xwn-present-2','xwn-d3d-present-1').replace('text("rung","03")','text("rung","08d")').replace('owned-window-gdi-readback','rgb-software-window-gdi-readback')
p=p.replace('files[2]=fresh(prefix,"-after.bin");','files[2]=fresh(prefix,"-after.bin");files[3]=fresh(prefix,"-post.bin");').replace('i<3;i++)if(files','i<4;i++)if(files')
p=p.replace('for(i=0;i<3;i++){if(brushes[i]&&!DeleteObject(brushes[i]))code=1;if(files[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(files[i]))io_error=1;}','for(i=0;i<3;i++)if(brushes[i]&&!DeleteObject(brushes[i]))code=1;\n for(i=0;i<4;i++)if(files[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(files[i]))io_error=1;')
out=S/'d3dpresent.c';assert not out.exists();out.write_text(p,encoding='utf-8',newline='\n')
cmd=(S/'present.cmd').read_text().replace('present.exe','d3dpresent.exe');(S/'d3dpresent.cmd').write_text(cmd,encoding='utf-8',newline='\r\n')
# The independent decoder retains actual clip-union checks, not a converted pass record.
g=g.replace('rung03','D3D windowed').replace("schema='xwn-present-2', rung='03'","schema='xwn-d3d-present-1', rung='08d'").replace('owned-window-gdi-readback','rgb-software-window-gdi-readback')
a=g.index('def expected(');b=g.index('\ndef validate(',a)
g=g[:a]+'''FOREGROUND=(0xff0000,0x00ff00,0xffffff,0xffff00)
BACKGROUND=(0x00ffff,0xff00ff,0x0000ff,0)
def allowed(stage,x,y):
    if x>=12 and y>=12 and 6*x+7*y<=724:return {FOREGROUND[stage]}
    if x<=4 or y<=4 or 6*x+7*y>=828:return {BACKGROUND[stage]}
    return {FOREGROUND[stage],BACKGROUND[stage]}

def pixels(captures):
    sizes={'source':128*112*4,'post':128*112*4,'before':256*192*4,'after':256*192*4}
    if set(captures)!=set(sizes) or any(len(captures[k])!=n*4 for k,n in sizes.items()):raise ValueError('Capture extent')
    if captures['post']!=captures['source']:raise ValueError('Render target changed after presentation')
    for stage in range(4):
        n=sizes['source'];src=struct.unpack('<14336I',captures['source'][stage*n:(stage+1)*n])
        for i,rgb in enumerate(src):
            if rgb not in allowed(stage,i%128,i//128):raise ValueError('D3D source pixel')
        for kind in ('before','after'):
            n=sizes[kind];image=struct.unpack('<49152I',captures[kind][stage*n:(stage+1)*n])
            for i,rgb in enumerate(image):
                x,y=i%256,i//256
                if stage in (1,2) and 48<=x<88 and 40<=y<72:want=0xff00ff
                elif 16<=x<112 and 16<=y<96:want=src[y*128+x] if kind=='after' else 0
                else:want=255
                if rgb!=want:raise ValueError('GDI presentation/guard pixel')
    return sum(len(v) for v in captures.values())
'''+g[b:]
g=g.replace("'primary.format', 'source.create', 'clipper.create'","'primary.format', 'source.create', 'd3d.query', 'enum.hr', 'device.create', 'viewport', 'texture0', 'stage0.op', 'stage0.arg', 'stage0.alpha', 'stage1.op', 'clipper.create'")
g=g.replace("('source', 'primary', 'clipper', 'ddraw')","('source', 'primary', 'clipper', 'ddraw', 'device')")
g=g.replace("'source.write.lock', 'source.read.lock',\n                    'source.write.unlock', 'source.read.unlock', 'primary.blit'","'source.lock', 'post.lock', 'source.unlock', 'post.unlock', 'clear', 'scene.begin', 'draw', 'scene.end', 'primary.blit'")
g=g.replace("'source.write.layout',\n                    'source.read.layout', 'source.exact', 'complete'","'source.layout', 'post.layout', 'complete'")
g=g.replace("('source.write.pitch', 'source.read.pitch')","('source.pitch', 'post.pitch')")
needle="        count = integer(prefix + 'clip.count')"
g=g.replace(needle,"""        for key in ('source.mismatches','post.mismatches'):need(prefix+key,0)
        need(prefix+'foreground',FOREGROUND[stage]);need(prefix+'background',BACKGROUND[stage])
        vertices=b''.join(struct.pack('<ffffI',x,y,.5,1,0xff000000|FOREGROUND[stage]) for x,y in [(8,8),(120,8),(8,104)])
        need(prefix+'vertices',vertices.hex())
"""+needle)
needle='    for stage in range(4):\n        prefix'
extra="""    need('enum.matches',1);need('enum.error',0);need('modules.ok',1)
    if not 1<=integer('enum.count')<=16:raise ValueError('Enumeration capacity')
    caps=bytes.fromhex(r.get('selected.caps',''))
    if len(caps)!=236:raise ValueError('Caps extent')
    # D3DDEVICEDESC7 packed ABI: dwDevCaps offset0, render bit depth172, GUID208.
    if caps[208:224]!=bytes.fromhex('605c66a47326cf11a31a00aa00b93356'):raise ValueError('Not RGB software')
    devcaps=struct.unpack_from('<I',caps,0)[0];depths=struct.unpack_from('<I',caps,172)[0]
    if devcaps&(0x80000|0x10000) or not depths&(0x400 if fmt[1]==32 else 0x800):raise ValueError('Renderer caps')
    for name,value in dict(z=0,zwrite=0,lighting=0,cull=1,fill=3,shade=1,fog=0,alpha=0,alphatest=0,dither=0,specular=0,antialias=0).items():
        need('state.'+name,'00000000');need('get.'+name,'00000000');need('value.'+name,value)
    modules=[]
    count=integer('modules');need('modules.end_error',18)
    if not 1<=count<=64:raise ValueError('Module capacity')
    for i in range(count):
        raw=bytes.fromhex(r.get(f'module{i}.path',''))
        if not raw or len(raw)>=260 or 0 in raw or not integer(f'module{i}.bytes'):raise ValueError('Module identity')
        modules.append(raw.decode('ascii'))
    if len({n.lower() for n in modules})!=count:raise ValueError('Duplicate module')
    integer('release.d3d')
"""
g=g.replace(needle,extra+needle)
a=g.index('    total = 0\n');b=g.index('    return dict(',a);g=g[:a]+'    total = pixels(captures)\n'+g[b:]
g=g.replace('display=[integer(', 'modules=modules, display=[integer(').replace("('source','before','after')","('source','before','after','post')")
g=g.replace('Owned source and GDI-observed primary pixels; no GPU/scanout/performance claim','RGB software triangle with bounded edges and exact source-to-GDI mapping; no GPU/scanout/performance claim')
out=W/'tools/graphics_d3dpresent.py';assert not out.exists();out.write_text(g,encoding='utf-8',newline='\n')
(K/'source001.json').write_text(json.dumps(dict(generated=True,inputs=pins,outputs={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in [S/'d3dpresent.c',S/'d3dpresent.cmd',out]}),indent=2)+'\n')
