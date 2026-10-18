"""Create the new texture sample from the frozen, qualified triangle source."""
from pathlib import Path
W=Path(__file__).resolve().parents[2]
p=W/'src/samples/graphics-ladder/texture.c'
assert not p.exists()
s=(W/'src/samples/graphics-ladder/triangle.c').read_text(encoding='utf-8')
s=s.replace('Rung07: enumerated RGB D3D7 device, owned offscreen clear/triangle readback.', 'Rung08a: enumerated RGB D3D7 software device and owned point-sampled texture.')
s=s.replace('No primary surface, mode change, texture, depth buffer, or hardware claim.', 'No primary surface, mode change, depth buffer, or hardware claim.')
s=s.replace('DWORD color;', 'float u,v;').replace('sizeof(VERTEX)==20', 'sizeof(VERTEX)==24')
s=s.replace('static VERTEX vertices[]={{8,8,.5f,1,0xff40c080},{56,8,.5f,1,0xff40c080},{8,56,.5f,1,0xff40c080}};', 'static VERTEX vertices[]={{8,8,.5f,1,0,0},{56,8,.5f,1,1,0},{8,56,.5f,1,0,1},{8,56,.5f,1,0,1},{56,8,.5f,1,1,0},{56,56,.5f,1,1,1}};')
s=s.replace('static DWORD enumerated', 'static HANDLE source_before=INVALID_HANDLE_VALUE,source_after=INVALID_HANDLE_VALUE;\nstatic DDPIXELFORMAT formats[64],texture_format;\nstatic DWORD format_count,format_error,format_index=0xffffffff;\nstatic DWORD enumerated')
at=s.index('#define HR(')
s=s[:at]+r'''
static int acceptable(const DDPIXELFORMAT *p){return p->dwSize==sizeof(*p)&&(p->dwFlags==DDPF_RGB||p->dwFlags==(DDPF_RGB|DDPF_ALPHAPIXELS))&&p->dwFourCC==0&&p->dwRGBBitCount==32&&p->dwRBitMask==0xff0000&&p->dwGBitMask==0xff00&&p->dwBBitMask==0xff&&p->dwRGBAlphaBitMask==((p->dwFlags&DDPF_ALPHAPIXELS)?0xff000000:0);}
static HRESULT CALLBACK texture_enum(DDPIXELFORMAT *p,void *ctx){if(ctx!=&context||!p||p->dwSize!=sizeof(*p)||format_count>=64){format_error=1;return D3DENUMRET_CANCEL;}formats[format_count]=*p;if(format_index==0xffffffff&&acceptable(p)){format_index=format_count;texture_format=*p;}format_count++;return D3DENUMRET_OK;}
static DWORD texel(DWORD x,DWORD y){return ((32+x*24)<<16)|((32+y*24)<<8)|(((x^y)&1)?224:32)|((texture_format.dwFlags&DDPF_ALPHAPIXELS)?0xff000000:0);}
static int texture_bytes(IDirectDrawSurface7 *surface,HANDLE file,const char *stem,int upload){DDSURFACEDESC2 s;HRESULT hr;DWORD x,y;int good=0;char key[80];zero(&s,sizeof(s));s.dwSize=sizeof(s);hr=IDirectDrawSurface7_Lock(surface,0,&s,DDLOCK_WAIT|(upload?0:DDLOCK_READONLY),0);wsprintfA(key,"%s.lock",stem);number(key,(DWORD)hr);if(hr!=DD_OK)return 0;
 wsprintfA(key,"%s.pitch",stem);number(key,(DWORD)s.lPitch);wsprintfA(key,"%s.caps",stem);number(key,s.ddsCaps.dwCaps);wsprintfA(key,"%s.format",stem);hex(key,(BYTE*)&s.ddpfPixelFormat,sizeof(s.ddpfPixelFormat));
 if(s.dwWidth==8&&s.dwHeight==8&&s.lpSurface&&s.lPitch>=32&&s.lPitch<=4096&&same(&s.ddpfPixelFormat,&texture_format,sizeof(texture_format))&&(s.ddsCaps.dwCaps&(DDSCAPS_TEXTURE|DDSCAPS_SYSTEMMEMORY))==(DDSCAPS_TEXTURE|DDSCAPS_SYSTEMMEMORY)&&!(s.ddsCaps.dwCaps&(DDSCAPS_PRIMARYSURFACE|DDSCAPS_VIDEOMEMORY|DDSCAPS_MIPMAP))){good=1;for(y=0;y<8;y++){DWORD *row=(DWORD*)((BYTE*)s.lpSurface+y*s.lPitch);if(upload)for(x=0;x<8;x++)row[x]=texel(x,y);if(!put(file,row,32)){good=0;break;}}}
 hr=IDirectDrawSurface7_Unlock(surface,0);wsprintfA(key,"%s.unlock",stem);number(key,(DWORD)hr);wsprintfA(key,"%s.valid",stem);number(key,good);return good&&hr==DD_OK;
}
''' + s[at:]
s=s.replace('IDirectDrawSurface7 *target=0;', 'IDirectDrawSurface7 *target=0,*texture=0;')
s=s.replace('ULONG refs;', 'ULONG refs;DWORD i;char key[64];')
s=s.replace('D3DFVF_XYZRHW|D3DFVF_DIFFUSE', 'D3DFVF_XYZRHW|D3DFVF_TEX1')
anchor=' HR("viewport",IDirect3DDevice7_SetViewport(dev,&vp));'
addition=r'''
 HR("formats.hr",IDirect3DDevice7_EnumTextureFormats(dev,texture_enum,&context));number("formats.count",format_count);number("formats.error",format_error);number("formats.selected",format_index);
 for(i=0;i<format_count;i++){wsprintfA(key,"format%lu",i);hex(key,(BYTE*)&formats[i],sizeof(formats[i]));}
 if(format_error||format_index==0xffffffff)goto done;
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;s.dwWidth=s.dwHeight=8;s.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_TEXTURE;s.ddpfPixelFormat=texture_format;
 HR("texture.create",IDirectDraw7_CreateSurface(dd,&s,&texture,0));if(!texture_bytes(texture,source_before,"source_before",1))goto done;
'''
s=s.replace(anchor,anchor+addition)
s=s.replace('IDirect3DDevice7_SetTexture(dev,0,0)', 'IDirect3DDevice7_SetTexture(dev,0,texture)',1)
s=s.replace('D3DTSS_COLORARG1,D3DTA_DIFFUSE', 'D3DTSS_COLORARG1,D3DTA_TEXTURE')
anchor=' HR("clear",IDirect3DDevice7_Clear'
at=s.index(anchor)
s=s[:at]+r'''
 HR("stage0.min",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_MINFILTER,D3DTFN_POINT));HR("stage0.mag",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_MAGFILTER,D3DTFG_POINT));HR("stage0.mip",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_MIPFILTER,D3DTFP_NONE));HR("stage0.u",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_ADDRESSU,D3DTADDRESS_CLAMP));HR("stage0.v",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_ADDRESSV,D3DTADDRESS_CLAMP));HR("stage0.coord",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_TEXCOORDINDEX,0));HR("stage0.transform",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_TEXTURETRANSFORMFLAGS,D3DTTFF_DISABLE));
''' +s[at:]
s=s.replace('vertices,3,0)', 'vertices,6,0)')
s=s.replace(' ok=modules();', ' if(!texture_bytes(texture,source_after,"source_after",0))goto done;\n HR("texture.unbind",IDirect3DDevice7_SetTexture(dev,0,0));\n ok=modules();')
s=s.replace(' if(target){', ' if(texture){refs=IDirectDrawSurface7_Release(texture);number("release.texture",refs);clean&=refs==0;}\n if(target){')
s=s.replace('text("schema","xwn-d3d-triangle-1")', 'text("schema","xwn-d3d-texture-1")')
s=s.replace('XWND3DTriangle07', 'XWND3DTexture08a').replace('XWN D3D triangle', 'XWN D3D texture')
s=s.replace(' text("schema"', ' source_before=fresh(prefix,"-source-before.bin");source_after=fresh(prefix,"-source-after.bin");if(source_before==INVALID_HANDLE_VALUE||source_after==INVALID_HANDLE_VALUE)goto done;\n text("schema"')
s=s.replace(' if(io_error)code=4;', ' if(source_before!=INVALID_HANDLE_VALUE&&!CloseHandle(source_before))io_error=1;\n if(source_after!=INVALID_HANDLE_VALUE&&!CloseHandle(source_after))io_error=1;\n if(io_error)code=4;')
p.write_text(s,encoding='utf-8',newline='\n')
cmd=(W/'src/samples/graphics-ladder/triangle.cmd').read_text().replace('triangle','texture')
cmd=cmd.replace('"%~dp0texture.exe"', 'if exist "%~2-source-before.bin" goto exists\nif exist "%~2-source-after.bin" goto exists\n"%~dp0texture.exe"')
p.with_suffix('.cmd').write_text(cmd,encoding='utf-8',newline='\n')
