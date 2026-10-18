"""Create original alpha control from the retained owned triangle sample."""
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
s=(W/'src/samples/graphics-ladder/triangle.c').read_text()
def change(a,b):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,b)
change('Rung07: enumerated RGB D3D7 device, owned offscreen clear/triangle readback.','Rung08c: enumerated RGB software device, diffuse-alpha blend controls.')
change('No primary surface, mode change, texture, depth buffer, or hardware claim.','No primary surface, mode change, texture, depth buffer, or hardware claim.')
verts=',\n '.join('{%s,%s,.5f,1,0x%02xff00ff}'%(x,y,a) for a in (0,85,170,255,85) for x,y in ((8,8),(56,8),(8,56)))
change('static VERTEX vertices[]={{8,8,.5f,1,0xff40c080},{56,8,.5f,1,0xff40c080},{8,56,.5f,1,0xff40c080}};',
 'static VERTEX vertices[]={\n '+verts+'};\nstatic const char *const stages[]={"clear","a0","a85","a170","a255","disabled"};\nstatic const char *const suffixes[]={"-clear.bin","-a0.bin","-a85.bin","-a170.bin","-a255.bin","-disabled.bin"};\nstatic const DWORD alphas[]={0,0,85,170,255,85};\nstatic HANDLE captures[6];')
change('static HANDLE log_file=INVALID_HANDLE_VALUE,clear_file=INVALID_HANDLE_VALUE,draw_file=INVALID_HANDLE_VALUE;','static HANDLE log_file=INVALID_HANDLE_VALUE;')
change('int ok=0,scene=0,clean=1;ULONG refs;','int ok=0,scene=0,clean=1;ULONG refs;DWORD i,value;char key[80];')
anchor=' hex("device.caps",(BYTE*)&selected,sizeof(selected));'
change(anchor,' if(!(selected.dpcTriCaps.dwSrcBlendCaps&D3DPBLENDCAPS_SRCALPHA)||!(selected.dpcTriCaps.dwDestBlendCaps&D3DPBLENDCAPS_INVSRCALPHA))goto done;\n'+anchor)
change('HR("stage0.alpha",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_ALPHAOP,D3DTOP_DISABLE));','HR("stage0.alpha",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_ALPHAOP,D3DTOP_SELECTARG1));HR("stage0.alpha_arg",IDirect3DDevice7_SetTextureStageState(dev,0,D3DTSS_ALPHAARG1,D3DTA_DIFFUSE));')
a=s.index(' HR("clear",IDirect3DDevice7_Clear');b=s.index(' ok=modules();',a)
s=s[:a]+''' RS("state.src",D3DRENDERSTATE_SRCBLEND,D3DBLEND_SRCALPHA);RS("state.dest",D3DRENDERSTATE_DESTBLEND,D3DBLEND_INVSRCALPHA);
 for(i=0;i<6;i++){
  DWORD enabled=i==5?FALSE:TRUE;
  wsprintfA(key,"%s.alpha",stages[i]);number(key,alphas[i]);
  wsprintfA(key,"%s.set_blend",stages[i]);RS(key,D3DRENDERSTATE_ALPHABLENDENABLE,enabled);
  value=0xeeeeeeee;wsprintfA(key,"%s.get_blend",stages[i]);HR(key,IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_ALPHABLENDENABLE,&value));wsprintfA(key,"%s.blend",stages[i]);number(key,value);if(value!=enabled)goto done;
  value=0xeeeeeeee;wsprintfA(key,"%s.get_src",stages[i]);HR(key,IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_SRCBLEND,&value));wsprintfA(key,"%s.src",stages[i]);number(key,value);if(value!=D3DBLEND_SRCALPHA)goto done;
  value=0xeeeeeeee;wsprintfA(key,"%s.get_dest",stages[i]);HR(key,IDirect3DDevice7_GetRenderState(dev,D3DRENDERSTATE_DESTBLEND,&value));wsprintfA(key,"%s.dest",stages[i]);number(key,value);if(value!=D3DBLEND_INVSRCALPHA)goto done;
  wsprintfA(key,"%s.clear_hr",stages[i]);HR(key,IDirect3DDevice7_Clear(dev,0,0,D3DCLEAR_TARGET,0x0000ff00,1.0f,0));
  if(i){
   wsprintfA(key,"%s.begin",stages[i]);HR(key,IDirect3DDevice7_BeginScene(dev));scene=1;
   wsprintfA(key,"%s.draw",stages[i]);HR(key,IDirect3DDevice7_DrawPrimitive(dev,D3DPT_TRIANGLELIST,D3DFVF_XYZRHW|D3DFVF_DIFFUSE,vertices+3*(i-1),3,0));
   hr=IDirect3DDevice7_EndScene(dev);scene=0;wsprintfA(key,"%s.end",stages[i]);number(key,(DWORD)hr);if(hr!=DD_OK)goto done;
  }
  if(!snapshot(target,captures[i],stages[i]))goto done;
 }
'''+s[b:]
change('OSVERSIONINFOA os;int code=1;','OSVERSIONINFOA os;int code=1;DWORD i;')
change(' SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);',' for(i=0;i<6;i++)captures[i]=INVALID_HANDLE_VALUE;\n SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);')
change('clear_file=fresh(prefix,"-clear.bin");draw_file=fresh(prefix,"-draw.bin");if(clear_file==INVALID_HANDLE_VALUE||draw_file==INVALID_HANDLE_VALUE)goto done;','for(i=0;i<6;i++){captures[i]=fresh(prefix,suffixes[i]);if(captures[i]==INVALID_HANDLE_VALUE)goto done;}')
change(' if(clear_file!=INVALID_HANDLE_VALUE&&!CloseHandle(clear_file))io_error=1;\n if(draw_file!=INVALID_HANDLE_VALUE&&!CloseHandle(draw_file))io_error=1;',' for(i=0;i<6;i++)if(captures[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(captures[i]))io_error=1;')
s=s.replace('xwn-d3d-triangle-1','xwn-d3d-blend-1').replace('XWND3DTriangle07','XWND3DBlend08c').replace('XWN D3D triangle','XWN D3D blend')
p=W/'src/samples/graphics-ladder/blend.c';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
cmd=(W/'src/samples/graphics-ladder/depth.cmd').read_bytes().replace(b'depth',b'blend');(p.with_suffix('.cmd')).write_bytes(cmd)
