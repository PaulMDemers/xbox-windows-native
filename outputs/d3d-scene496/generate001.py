"""Construct original combined sample from pinned project-owned control functions."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];S=W/'src/samples/graphics-ladder'
t=(S/'transform.c').read_text();texture=(S/'texture.c').read_text();depth=(S/'depth.c').read_text()
out=S/'scene.c';assert not out.exists()
t=t.replace('Rung09a: actual XYZ world/view/projection transforms with offscreen readback.','Rung09b: owned XYZ textured triangles, explicit depth and offscreen controls.')
t=t.replace('No primary surface, mode change, texture, depth buffer, or hardware claim.','No primary surface, mode change, lighting or hardware claim.')
t=t.replace('typedef struct {float x,y,z;DWORD color;} VERTEX;','typedef struct {float x,y,z,u,v;} VERTEX;').replace('sizeof(VERTEX)==16','sizeof(VERTEX)==20')
a=t.index('static VERTEX vertices[]');b=t.index('typedef char matrix_size',a)
t=t[:a]+'''static VERTEX vertices[]={
 {-.875f,.75f,1.25f,0,0},{.625f,.75f,1.25f,1,0},{-.875f,-.75f,1.25f,0,1},
 {-.25f,.75f,1.5f,0,0},{1.25f,.75f,1.5f,1,0},{-.25f,-.75f,1.5f,0,1}};
static HANDLE source_before=INVALID_HANDLE_VALUE,source_after=INVALID_HANDLE_VALUE;
static DDPIXELFORMAT texture_formats[64],texture_format,depth_formats[64],depth_format;
static DWORD texture_count,texture_error,texture_index=0xffffffff;
static DWORD depth_count,depth_error,depth_index=0xffffffff,current_texture;
'''+t[b:]
helpers=texture[texture.index('static int acceptable'):texture.index('#define HR')]
for a,b in [('acceptable','texture_acceptable'),('format_count','texture_count'),('format_error','texture_error'),('format_index','texture_index'),('formats[','texture_formats[')]:helpers=helpers.replace(a,b)
a=helpers.index('static DWORD texel');b=helpers.index('static int texture_bytes',a)
helpers=helpers[:a]+'''static DWORD texel(DWORD x,DWORD y){
 static const DWORD colors[2][4]={{0x206040,0x40c080,0x608020,0x80a060},{0x802060,0xc04080,0xa06020,0xe08040}};
 return colors[current_texture][(y/4)*2+x/4]|((texture_format.dwFlags&DDPF_ALPHAPIXELS)?0xff000000:0);
}
'''+helpers[b:]
zh=depth[depth.index('static int acceptable'):depth.index('static int modules')]
for a,b in [('acceptable','depth_acceptable'),('format_count','depth_count'),('format_error','depth_error'),('format_index','depth_index'),('formats[','depth_formats[')]:zh=zh.replace(a,b)
t=t.replace('#define HR',helpers+zh+'#define HR',1)
a=t.index('static int transformed(');b=t.index('static int run(',a)
t=t[:a]+'''static int transformed(IDirect3DDevice7 *dev,IDirectDrawSurface7 *target,IDirectDrawSurface7 **textures){
 static const char *const names[]={"far_near","near_far","no_z","zero_z","camera_move"};
 D3DMATRIX world,view,projection,readback;D3DVIEWPORT7 vp={0,0,64,64,0,1},got;
 unsigned j;char key[80],stem[80];HRESULT hr;DWORD enabled=stage==2?0:1,actual;int scene=0,ok=0;
 identity(&world);identity(&view);identity(&projection);
 world._41=stage==4?-.125f:.125f;view._42=-.125f;
 projection._33=2;projection._34=1;projection._43=-2;projection._44=0;
 wsprintfA(key,"s%u.name",stage);text(key,names[stage]);
 wsprintfA(key,"s%u.vertices",stage);hex(key,(BYTE*)vertices,sizeof(vertices));
#define SH(label,expr) do{wsprintfA(key,"s%u." label,stage);HR(key,expr);}while(0)
 SH("state_z.set",IDirect3DDevice7_SetRenderState(dev,D3DRENDERSTATE_ZENABLE,enabled));
 actual=0xffffffff;SH("state_z.get",IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_ZENABLE,&actual));
 wsprintfA(key,"s%u.z_enabled",stage);number(key,actual);if(actual!=enabled)goto done;
 wsprintfA(key,"s%u.clear_z",stage);number(key,stage==3?0:1);
 SH("clear.viewport",IDirect3DDevice7_SetViewport(dev,&vp));
 SH("clear",IDirect3DDevice7_Clear(dev,0,0,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0x00102030,stage==3?0.0f:1.0f,0));
 wsprintfA(stem,"s%u.clear_capture",stage);if(!snapshot(target,clear_file,stem))goto done;
 SH("viewport.set",IDirect3DDevice7_SetViewport(dev,&vp));zero(&got,sizeof(got));SH("viewport.get",IDirect3DDevice7_GetViewport(dev,&got));
 wsprintfA(key,"s%u.viewport",stage);hex(key,(BYTE*)&vp,sizeof(vp));wsprintfA(key,"s%u.viewport_readback",stage);hex(key,(BYTE*)&got,sizeof(got));if(!same(&vp,&got,sizeof(vp)))goto done;
#define MATRIX(label,kind,m) do{wsprintfA(key,"s%u." label,stage);hex(key,(BYTE*)&m,sizeof(m));SH(label ".set",IDirect3DDevice7_SetTransform(dev,kind,&m));zero(&readback,sizeof(readback));SH(label ".get",IDirect3DDevice7_GetTransform(dev,kind,&readback));wsprintfA(key,"s%u." label "_readback",stage);hex(key,(BYTE*)&readback,sizeof(readback));if(!same(&readback,&m,sizeof(m)))goto done;}while(0)
 MATRIX("world",D3DTRANSFORMSTATE_WORLD,world);MATRIX("view",D3DTRANSFORMSTATE_VIEW,view);MATRIX("projection",D3DTRANSFORMSTATE_PROJECTION,projection);
 SH("scene.begin",IDirect3DDevice7_BeginScene(dev));scene=1;
 for(j=0;j<2;j++){
  DWORD index=stage==0?1-j:j;wsprintfA(key,"s%u.draw%u.index",stage,j);number(key,index);
  wsprintfA(key,"s%u.draw%u.texture",stage,j);HR(key,IDirect3DDevice7_SetTexture(dev,0,textures[index]));
  wsprintfA(key,"s%u.draw%u.hr",stage,j);HR(key,IDirect3DDevice7_DrawPrimitive(dev,D3DPT_TRIANGLELIST,D3DFVF_XYZ|D3DFVF_TEX1,vertices+index*3,3,0));
 }
 hr=IDirect3DDevice7_EndScene(dev);scene=0;wsprintfA(key,"s%u.scene.end",stage);number(key,(DWORD)hr);if(hr!=DD_OK)goto done;
 wsprintfA(stem,"s%u.draw_capture",stage);if(!snapshot(target,draw_file,stem))goto done;
 wsprintfA(key,"s%u.complete",stage);number(key,1);ok=1;
 done:if(scene){number("cleanup.end_scene",(DWORD)IDirect3DDevice7_EndScene(dev));ok=0;}return ok;
#undef MATRIX
#undef SH
}
'''+t[b:]
t=t.replace('IDirectDrawSurface7 *target=0;','IDirectDrawSurface7 *target=0,*textures[2]={0,0},*depth=0,*attached_check=0;')
t=t.replace('int ok=0,clean=1;ULONG refs;','int ok=0,clean=1,attached=0;ULONG refs;DWORD i;char key[80];DDSCAPS2 caps;')
t=t.replace('D3DFVF_XYZ|D3DFVF_DIFFUSE','D3DFVF_XYZ|D3DFVF_TEX1')
z=depth[depth.index(' HR("formats.hr"'):depth.index(' HR("device.create"')]
for a,b in [('"formats.','"zformats.'),('"format%','"zformat%'),('format_count','depth_count'),('format_error','depth_error'),('format_index','depth_index'),('formats[','depth_formats[')]:z=z.replace(a,b)
t=t.replace(' HR("device.create"',z+' HR("device.create"',1)
x=texture[texture.index(' HR("formats.hr"'):texture.index('\n RS("state.z"')]
for a,b in [('"formats.','"tformats.'),('"format%','"tformat%'),('format_count','texture_count'),('format_error','texture_error'),('format_index','texture_index'),('formats[','texture_formats[')]:x=x.replace(a,b)
x=x.replace(' HR("texture.create",IDirectDraw7_CreateSurface(dd,&s,&texture,0));if(!texture_bytes(texture,source_before,"source_before",1))goto done;', ''' for(current_texture=0;current_texture<2;current_texture++){
  wsprintfA(key,"texture%lu.create",current_texture);HR(key,IDirectDraw7_CreateSurface(dd,&s,&textures[current_texture],0));
  wsprintfA(key,"source%lu.before",current_texture);if(!texture_bytes(textures[current_texture],source_before,key,1))goto done;
 }
''')
t=t.replace('\n RS("state.clipping"',x+'\n RS("state.clipping"',1)
t=t.replace('D3DRENDERSTATE_ZENABLE,FALSE','D3DRENDERSTATE_ZENABLE,D3DZB_TRUE').replace('D3DRENDERSTATE_ZWRITEENABLE,FALSE','D3DRENDERSTATE_ZWRITEENABLE,TRUE')
t=t.replace(' RS("state.z",',' RS("state.zfunc",D3DRENDERSTATE_ZFUNC,D3DCMP_LESS);RS("state.z",',1)
a=t.index(' HR("texture0"');b=t.index(' ok=modules()',a)
ts=texture[texture.index(' HR("texture0"'):texture.index(' HR("clear"')]
ts=ts.replace('HR("texture0",IDirect3DDevice7_SetTexture(dev,0,texture));','')
# Upgrade actual stage-state operations to set/get/value triples.
import re
ts=re.sub(r'HR\("([^"\n]+)",IDirect3DDevice7_SetTextureStageState\(dev,(\d+),([^,]+),([^\)]+)\)\)',r'TSS("\1",\2,\3,\4)',ts)
t=t[:a]+'''#define TSS(label,unit,state,value) do{DWORD actual=0xffffffff;HR(label,IDirect3DDevice7_SetTextureStageState(dev,unit,state,value));HR("get." label,IDirect3DDevice7_GetTextureStageState(dev,unit,state,&actual));number("value." label,actual);if(actual!=(DWORD)(value))goto done;}while(0)
'''+ts+''' for(stage=0;stage<5;stage++)if(!transformed(dev,target,textures))goto done;
 number("stages",stage);
 for(current_texture=0;current_texture<2;current_texture++){
  wsprintfA(key,"source%lu.after",current_texture);if(!texture_bytes(textures[current_texture],source_after,key,0))goto done;
 }
 HR("texture.unbind",IDirect3DDevice7_SetTexture(dev,0,0));
'''+t[b:]
t=t.replace(' if(target){refs=', ''' for(i=0;i<2;i++)if(textures[i]){refs=IDirectDrawSurface7_Release(textures[i]);wsprintfA(key,"release.texture%lu",i);number(key,refs);clean&=refs==0;}
 if(attached_check)IDirectDrawSurface7_Release(attached_check);
 if(attached){hr=IDirectDrawSurface7_DeleteAttachedSurface(target,0,depth);number("depth.detach",(DWORD)hr);clean&=hr==DD_OK;}
 if(depth){refs=IDirectDrawSurface7_Release(depth);number("release.depth",refs);clean&=refs==0;}
 if(target){refs=''')
t=t.replace('text("schema","xwn-d3d-transform-1")','text("schema","xwn-d3d-scene-1")').replace('offscreen-xyz-transforms-rgb-software','offscreen-xyz-texture-depth-rgb-software').replace('XWND3DTransform09a','XWND3DScene09b').replace('XWN D3D transforms','XWN D3D scene')
t=t.replace(' text("schema",', ''' source_before=fresh(prefix,"-source-before.bin");source_after=fresh(prefix,"-source-after.bin");if(source_before==INVALID_HANDLE_VALUE||source_after==INVALID_HANDLE_VALUE)goto done;
 text("schema",''')
t=t.replace(' if(io_error)code=4;', ''' if(source_before!=INVALID_HANDLE_VALUE&&!CloseHandle(source_before))io_error=1;
 if(source_after!=INVALID_HANDLE_VALUE&&!CloseHandle(source_after))io_error=1;
 if(io_error)code=4;''')
assert 'XYZRHW' not in t and 'transformed(dev,target,textures)' in t
out.write_bytes(t.encode())
(S/'scene.cmd').write_bytes((S/'transform.cmd').read_bytes().replace(b'transform',b'scene').replace(b'r09ad',b'r09bd').replace(b'r09as',b'r09bs'))
print('Generated new scene source; no build/run.')
