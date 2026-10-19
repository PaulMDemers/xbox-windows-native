"""MIT. Compose new source once; retain prior qualified samples unchanged."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent; W=K.parents[1]; S=W/'src/samples/graphics-ladder'
scene=(S/'scene.c').read_text(encoding='utf-8')
present=(S/'d3dpresent.c').read_text(encoding='utf-8')
out=S/'scenepresent.c';assert not out.exists()
pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [S/'scene.c',S/'d3dpresent.c']}
# Adapt the proven owned-window/clip-union code. New names cannot shadow target.
block=present[present.index('static int inrect('):present.index('static int surface(')]
block=block.replace('stage==1||stage==2','stage==1||stage==2')
block=block.replace('x>=48&&x<88&&y>=40&&y<72','x>=24&&x<48&&y>=24&&y<48')
block=block.replace('x>=16&&x<112&&y>=16&&y<96','x>=8&&x<56&&y>=8&&y<56')
block=block.replace('source[y*TW+x]','visible_source[y*64+x]')
block=block.replace('h==target','h==child').replace('target=CreateWindowA','child=CreateWindowA')
block=block.replace('16,16,96,80','8,8,48,48').replace('48,40,40,32','24,24,24,24')
block=block.replace('return target&&cover','return child&&cover')
block=block.replace('XWND3DPresent08d','XWNScenePresent09c').replace('XWN D3D presentation','XWN combined 3D scene')
block=block.replace('files[after?2:1]','screens[after?1:0]')
block=block.replace('origin.x+16','origin.x+8').replace('origin.x+112','origin.x+56').replace('origin.y+16','origin.y+8').replace('origin.y+96','origin.y+56')
import re
block=re.sub(r'\bCW\b','PW',block);block=re.sub(r'\bCH\b','PH',block)
decl='''
#define PW 80
#define PH 80
static HWND panel,child,cover;
static HBRUSH brushes[3];
static int cancelled;
static HANDLE screens[2]={INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE};
static HANDLE post_file=INVALID_HANDLE_VALUE;
static DWORD visible_source[64*64],screen[PW*PH];
static void snum(const char *key,DWORD value){char label[96];wsprintfA(label,"p.s%u.%s",stage,key);number(label,value);}
static int scall(const char *key,HRESULT hr){snum(key,(DWORD)hr);return hr==DD_OK;}
'''
scene=scene.replace(' * Rung09b: owned XYZ textured triangles, explicit depth and offscreen controls.\n * No primary surface, mode change, lighting or hardware claim.',' * Rung09c: combined XYZ/texture/depth scene and clipped window presentation.\n * RGB32 desktop required. No mode change, lighting or hardware claim.')
at=scene.index('static int texture_acceptable(');scene=scene[:at]+decl+block+scene[at:]
# Snapshot already copies only defined rows. Preserve its original metadata.
scene=scene.replace('if(!put(file,(BYTE*)s.lpSurface+y*s.lPitch,256)){good=0;break;}',
 '''{DWORD x;DWORD *row=(DWORD*)((BYTE*)s.lpSurface+y*s.lPitch);
 if(file==draw_file)for(x=0;x<64;x++)visible_source[y*64+x]=row[x]&0xffffffUL;
 if(!put(file,row,256)){good=0;break;}}''')
# Declaration must precede snapshot.
scene=scene.replace('static DWORD visible_source[64*64],screen[PW*PH];','static DWORD screen[PW*PH];')
scene=scene.replace('static int format(', 'static DWORD visible_source[64*64];\nstatic int format(',1)
scene=scene.replace('DDSCAPS2 caps;','DDSCAPS2 caps;IDirectDrawSurface7 *primary=0;IDirectDrawClipper *cl=0;HWND owner=0;DDPIXELFORMAT pf;',1)
anchor=' for(stage=0;stage<5;stage++)if(!transformed(dev,target,textures))goto done;'
assert anchor in scene
scene=scene.replace(anchor,''' zero(&s,sizeof(s));s.dwSize=sizeof(s);HR("p.mode",IDirectDraw7_GetDisplayMode(dd,&s));
 number("p.mode.width",s.dwWidth);number("p.mode.height",s.dwHeight);number("p.mode.bits",s.ddpfPixelFormat.dwRGBBitCount);
 if(s.dwWidth<640||s.dwHeight<480||s.ddpfPixelFormat.dwRGBBitCount!=32)goto done;
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS;s.ddsCaps.dwCaps=DDSCAPS_PRIMARYSURFACE;
 HR("p.primary.create",IDirectDraw7_CreateSurface(dd,&s,&primary,0));
 zero(&pf,sizeof(pf));pf.dwSize=sizeof(pf);HR("p.primary.format",IDirectDrawSurface7_GetPixelFormat(primary,&pf));hex("p.format",(BYTE*)&pf,sizeof(pf));
 if(pf.dwFlags!=DDPF_RGB||pf.dwRGBBitCount!=32||pf.dwRBitMask!=0xff0000||pf.dwGBitMask!=0xff00||pf.dwBBitMask!=255||pf.dwRGBAlphaBitMask)goto done;
 HR("p.clipper.create",IDirectDraw7_CreateClipper(dd,0,&cl,0));HR("p.clipper.hwnd",IDirectDrawClipper_SetHWnd(cl,0,child));
 HR("p.clipper.gethwnd",IDirectDrawClipper_GetHWnd(cl,&owner));number("p.clipper.owner",owner==child);if(owner!=child)goto done;
 HR("p.primary.clipper",IDirectDrawSurface7_SetClipper(primary,cl));
 for(stage=0;stage<5;stage++){
  POINT p={0,0};RECT rect,from={0,0,64,64},to;int moved=stage>=2;char label[80];
  if(!SetWindowPos(cover,HWND_TOP,0,0,0,0,SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE|((stage==1||stage==2)?SWP_SHOWWINDOW:SWP_HIDEWINDOW)))goto done;
  if(!SetWindowPos(panel,HWND_TOPMOST,moved?144:64,moved?112:64,PW,PH,SWP_SHOWWINDOW))goto done;
  pump(100);if(cancelled)goto done;
  if(!RedrawWindow(panel,0,0,RDW_INVALIDATE|RDW_ERASE|RDW_ALLCHILDREN|RDW_UPDATENOW)||!GdiFlush())goto done;
  if(!ClientToScreen(panel,&p)||!GetClientRect(panel,&rect)||rect.right!=PW||rect.bottom!=PH||p.x!=(moved?144:64)||p.y!=(moved?112:64))goto done;
  snum("origin.x",(DWORD)p.x);snum("origin.y",(DWORD)p.y);snum("cover",stage==1||stage==2);
  snum("cover.visible",IsWindowVisible(cover)!=0);snum("cover.above",GetWindow(child,GW_HWNDPREV)==cover);
  if((IsWindowVisible(cover)!=0)!=(stage==1||stage==2)||GetWindow(child,GW_HWNDPREV)!=cover)goto done;
  if(!capture(0,p)||!clip(cl,p)||!transformed(dev,target,textures))goto done;
  to.left=p.x;to.top=p.y;to.right=p.x+64;to.bottom=p.y+64;
  if(!scall("primary.blit",IDirectDrawSurface7_Blt(primary,&to,target,&from,DDBLT_DONOTWAIT,0))||!GdiFlush())goto done;
  Sleep(100);if(!capture(1,p))goto done;
  wsprintfA(label,"p.s%u.post",stage);if(!snapshot(target,post_file,label))goto done;
  snum("complete",1);pump(750);if(cancelled)goto done;
 }''')
scene=scene.replace('done:\n if(dev)', '''done:
 if(primary&&cl){hr=IDirectDrawSurface7_SetClipper(primary,0);number("p.primary.detach",(DWORD)hr);clean&=hr==DD_OK;}
 if(primary){refs=IDirectDrawSurface7_Release(primary);number("p.release.primary",refs);clean&=refs==0;}
 if(cl){refs=IDirectDrawClipper_Release(cl);number("p.release.clipper",refs);clean&=refs==0;}
 if(dev)''')
scene=scene.replace('WNDCLASSA cls;HWND w=0;','unsigned i;HWND w=0;')
scene=scene.replace('text("schema","xwn-d3d-scene-1")','text("schema","xwn-scene-present-1")').replace('"offscreen-xyz-texture-depth-rgb-software"','"windowed-xyz-texture-depth-rgb-software"')
a=scene.index(' zero(&cls,sizeof(cls));');b=scene.index('\ndone:',a)
scene=scene[:a]+''' screens[0]=fresh(prefix,"-screen-before.bin");screens[1]=fresh(prefix,"-screen-after.bin");post_file=fresh(prefix,"-post.bin");
 if(screens[0]==INVALID_HANDLE_VALUE||screens[1]==INVALID_HANDLE_VALUE||post_file==INVALID_HANDLE_VALUE)goto done;
 if(windows()){w=panel;}number("window.created",w!=0);if(w&&run(w,backend))code=0;
'''+scene[b:]
scene=scene.replace(' if(w&&!DestroyWindow(w))code=1;', ''' if(panel&&!DestroyWindow(panel))code=1;
 for(i=0;i<3;i++)if(brushes[i]&&!DeleteObject(brushes[i]))code=1;
 for(i=0;i<2;i++)if(screens[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(screens[i]))io_error=1;
 if(post_file!=INVALID_HANDLE_VALUE&&!CloseHandle(post_file))io_error=1;''')
out.write_text(scene,encoding='utf-8',newline='\n')
cmd=(S/'scene.cmd').read_text(encoding='utf-8').replace('scene.exe','scenepresent.exe').replace('scene.cmd','scenepresent.cmd').replace('graphics_scene.py','graphics_scenepresent.py')
for suffix in ('source-before','source-after','screen-before','screen-after','post'):
 cmd=cmd.replace('"%~dp0scenepresent.exe"',f'if exist "%~2-{suffix}.bin" goto exists\n"%~dp0scenepresent.exe"')
(S/'scenepresent.cmd').write_text(cmd,encoding='utf-8',newline='\n')
(K/'source001.json').write_text(json.dumps(dict(inputs=pins,output_sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
