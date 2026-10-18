"""Create the new depth sample from the preserved triangle source; no execution."""
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
s=(W/'src/samples/graphics-ladder/triangle.c').read_text(encoding='utf-8')
def replace(a,b):
    global s
    assert s.count(a)==1,a
    s=s.replace(a,b)
replace('Rung07: enumerated RGB D3D7 device, owned offscreen clear/triangle readback.', 'Rung08b: enumerated RGB software device, owned depth buffer and order controls.')
replace('No primary surface, mode change, texture, depth buffer, or hardware claim.', 'No primary surface, mode change, texture, stencil, or hardware claim.')
replace('static VERTEX vertices[]={{8,8,.5f,1,0xff40c080},{56,8,.5f,1,0xff40c080},{8,56,.5f,1,0xff40c080}};', '''static VERTEX vertices[]={
 {8,8,.25f,1,0xff40c080},{56,8,.25f,1,0xff40c080},{8,56,.25f,1,0xff40c080},
 {8,8,.75f,1,0xffc04080},{56,8,.75f,1,0xffc04080},{8,56,.75f,1,0xffc04080}};
static DDPIXELFORMAT formats[64],depth_format;
static DWORD format_count,format_error,format_index=0xffffffff;
static const char *const stages[]={"clear","far_near","near_far","no_z","zero_z"};
static const char *const suffixes[]={"-clear.bin","-far-near.bin","-near-far.bin","-no-z.bin","-zero-z.bin"};
static HANDLE captures[5];''')
replace('static HANDLE log_file=INVALID_HANDLE_VALUE,clear_file=INVALID_HANDLE_VALUE,draw_file=INVALID_HANDLE_VALUE;', 'static HANDLE log_file=INVALID_HANDLE_VALUE;')
anchor='static int modules(void)'
replace(anchor,'''static int acceptable(const DDPIXELFORMAT *p){return p->dwSize==sizeof(*p)&&p->dwFlags==DDPF_ZBUFFER&&p->dwFourCC==0&&(p->dwZBufferBitDepth==16||p->dwZBufferBitDepth==24||p->dwZBufferBitDepth==32)&&p->dwStencilBitDepth==0&&p->dwStencilBitMask==0;}
static HRESULT CALLBACK depth_enum(DDPIXELFORMAT *p,void *ctx){if(ctx!=&context||!p||p->dwSize!=sizeof(*p)||format_count>=64){format_error=1;return D3DENUMRET_CANCEL;}formats[format_count]=*p;if(format_index==0xffffffff&&acceptable(p)){format_index=format_count;depth_format=*p;}format_count++;return D3DENUMRET_OK;}
'''+anchor)
replace('IDirectDrawSurface7 *target=0;', 'IDirectDrawSurface7 *target=0,*depth=0,*attached_check=0;')
replace('int ok=0,scene=0,clean=1;ULONG refs;', 'int ok=0,scene=0,clean=1,attached=0;ULONG refs;DWORD i,j;char key[80];DDSCAPS2 caps;')
replace(' HR("device.create",IDirect3D7_CreateDevice(d3d,&selected.deviceGUID,target,&dev));', ''' HR("formats.hr",IDirect3D7_EnumZBufferFormats(d3d,&selected.deviceGUID,depth_enum,&context));number("formats.count",format_count);number("formats.error",format_error);number("formats.selected",format_index);
 for(i=0;i<format_count;i++){wsprintfA(key,"format%lu",i);hex(key,(BYTE*)&formats[i],sizeof(formats[i]));}
 if(format_error||format_index==0xffffffff)goto done;
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;s.dwWidth=s.dwHeight=64;s.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_ZBUFFER;s.ddpfPixelFormat=depth_format;
 HR("depth.create",IDirectDraw7_CreateSurface(dd,&s,&depth,0));
 zero(&s,sizeof(s));s.dwSize=sizeof(s);HR("depth.desc",IDirectDrawSurface7_GetSurfaceDesc(depth,&s));
 number("depth.width",s.dwWidth);number("depth.height",s.dwHeight);number("depth.caps",s.ddsCaps.dwCaps);hex("depth.format",(BYTE*)&s.ddpfPixelFormat,sizeof(s.ddpfPixelFormat));
 if(s.dwWidth!=64||s.dwHeight!=64||!same(&s.ddpfPixelFormat,&depth_format,sizeof(depth_format))||(s.ddsCaps.dwCaps&(DDSCAPS_SYSTEMMEMORY|DDSCAPS_ZBUFFER))!=(DDSCAPS_SYSTEMMEMORY|DDSCAPS_ZBUFFER)||(s.ddsCaps.dwCaps&(DDSCAPS_PRIMARYSURFACE|DDSCAPS_VIDEOMEMORY)))goto done;
 HR("depth.attach",IDirectDrawSurface7_AddAttachedSurface(target,depth));attached=1;
 zero(&caps,sizeof(caps));caps.dwCaps=DDSCAPS_ZBUFFER;
 HR("depth.get_attached",IDirectDrawSurface7_GetAttachedSurface(target,&caps,&attached_check));number("depth.identity",attached_check==depth);
 if(attached_check!=depth)goto done;
 number("depth.release_query",IDirectDrawSurface7_Release(attached_check));attached_check=0;
 HR("device.create",IDirect3D7_CreateDevice(d3d,&selected.deviceGUID,target,&dev));''')
replace('RS("state.z",D3DRENDERSTATE_ZENABLE,FALSE);RS("state.zwrite",D3DRENDERSTATE_ZWRITEENABLE,FALSE);', 'RS("state.z",D3DRENDERSTATE_ZENABLE,D3DZB_TRUE);RS("state.zwrite",D3DRENDERSTATE_ZWRITEENABLE,TRUE);RS("state.zfunc",D3DRENDERSTATE_ZFUNC,D3DCMP_LESS);')
start=s.index(' HR("clear",IDirect3DDevice7_Clear');end=s.index(' ok=modules();',start)
s=s[:start]+''' for(i=0;i<5;i++){
  DWORD enabled=i==3?D3DZB_FALSE:D3DZB_TRUE;D3DVALUE z=i==4?0.0f:1.0f;
  wsprintfA(key,"%s.z_enabled",stages[i]);number(key,enabled);wsprintfA(key,"%s.clear_z",stages[i]);number(key,i==4?0:1);
  wsprintfA(key,"%s.state_z",stages[i]);RS(key,D3DRENDERSTATE_ZENABLE,enabled);
  wsprintfA(key,"%s.clear_hr",stages[i]);HR(key,IDirect3DDevice7_Clear(dev,0,0,D3DCLEAR_TARGET|D3DCLEAR_ZBUFFER,0x00102030,z,0));
  if(i){
   wsprintfA(key,"%s.begin",stages[i]);HR(key,IDirect3DDevice7_BeginScene(dev));scene=1;
   for(j=0;j<2;j++){
    DWORD index=i==1?(1-j):j;wsprintfA(key,"%s.draw%lu.index",stages[i],j);number(key,index);
    wsprintfA(key,"%s.draw%lu.hr",stages[i],j);HR(key,IDirect3DDevice7_DrawPrimitive(dev,D3DPT_TRIANGLELIST,D3DFVF_XYZRHW|D3DFVF_DIFFUSE,vertices+3*index,3,0));
   }
   hr=IDirect3DDevice7_EndScene(dev);scene=0;wsprintfA(key,"%s.end",stages[i]);number(key,(DWORD)hr);if(hr!=DD_OK)goto done;
  }
  if(!snapshot(target,captures[i],stages[i]))goto done;
 }
'''+s[end:]
replace(' if(target){refs=IDirectDrawSurface7_Release(target);', ''' if(attached_check)IDirectDrawSurface7_Release(attached_check);
 if(attached){hr=IDirectDrawSurface7_DeleteAttachedSurface(target,0,depth);number("depth.detach",(DWORD)hr);clean&=hr==DD_OK;}
 if(depth){refs=IDirectDrawSurface7_Release(depth);number("release.depth",refs);clean&=refs==0;}
 if(target){refs=IDirectDrawSurface7_Release(target);''')
replace('OSVERSIONINFOA os;int code=1;', 'OSVERSIONINFOA os;int code=1;DWORD i;')
replace(' SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);', ' for(i=0;i<5;i++)captures[i]=INVALID_HANDLE_VALUE;\n SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);')
replace('clear_file=fresh(prefix,"-clear.bin");draw_file=fresh(prefix,"-draw.bin");if(clear_file==INVALID_HANDLE_VALUE||draw_file==INVALID_HANDLE_VALUE)goto done;', 'for(i=0;i<5;i++){captures[i]=fresh(prefix,suffixes[i]);if(captures[i]==INVALID_HANDLE_VALUE)goto done;}')
s=s.replace('xwn-d3d-triangle-1','xwn-d3d-depth-1').replace('XWND3DTriangle07','XWND3DDepth08b').replace('XWN D3D triangle','XWN D3D depth')
replace(' if(clear_file!=INVALID_HANDLE_VALUE&&!CloseHandle(clear_file))io_error=1;\n if(draw_file!=INVALID_HANDLE_VALUE&&!CloseHandle(draw_file))io_error=1;', ' for(i=0;i<5;i++)if(captures[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(captures[i]))io_error=1;')
p=W/'src/samples/graphics-ladder/depth.c';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
s=(W/'src/samples/graphics-ladder/triangle.cmd').read_text(encoding='utf-8').replace('triangle','depth').replace('if exist "%~2-draw.bin" goto exists','\n'.join('if exist "%~2-'+n+'.bin" goto exists' for n in ['far-near','near-far','no-z','zero-z']))
(p.with_suffix('.cmd')).write_text(s,encoding='utf-8',newline='\n')
p=W/'tools/build-graphics-samples.py';s=p.read_text(encoding='utf-8').replace("'triangle', 'texture')", "'triangle', 'texture', 'depth')");p.write_text(s,encoding='utf-8',newline='\n')
with (W/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n/outputs/d3d-depth480/** -text whitespace=cr-at-eol\n')
