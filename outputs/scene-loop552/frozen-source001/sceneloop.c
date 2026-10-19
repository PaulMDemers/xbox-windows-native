/* SPDX-License-Identifier: MIT
 * Rung09e: 160 repeated software frames with phase timing and resource observations.
 * RGB32 offscreen render with explicit native-format CPU staging. No mode change, lighting or hardware claim.
 */
#define WINVER 0x0500
#define _WIN32_WINNT 0x0500
#define DIRECTDRAW_VERSION 0x0700
#define DIRECT3D_VERSION 0x0700
#define COBJMACROS
#include <windows.h>
#include <tlhelp32.h>
#include <ddraw.h>
#include <d3d.h>
static const GUID dd7={0x15e65ec0,0x3b9c,0x11d2,{0xb9,0x2f,0,0x60,0x97,0x97,0xea,0x5b}};
static const GUID d3d7={0xf5049e77,0x4861,0x11d2,{0xa4,7,0,0xa0,0xc9,6,0x29,0xa8}};
static const GUID rgb={0xa4665c60,0x2673,0x11cf,{0xa3,0x1a,0,0xaa,0,0xb9,0x33,0x56}};
typedef struct {float x,y,z,u,v;} VERTEX;
typedef char vertex_size[(sizeof(VERTEX)==20)?1:-1];
typedef char caps_size[(sizeof(D3DDEVICEDESC7)==236)?1:-1];
static VERTEX vertices[]={
 {-.875f,.75f,1.25f,0,0},{.625f,.75f,1.25f,1,0},{-.875f,-.75f,1.25f,0,1},
 {-.25f,.75f,1.5f,0,0},{1.25f,.75f,1.5f,1,0},{-.25f,-.75f,1.5f,0,1}};
static HANDLE source_before=INVALID_HANDLE_VALUE,source_after=INVALID_HANDLE_VALUE;
static DDPIXELFORMAT texture_formats[64],texture_format,depth_formats[64],depth_format;
static DWORD texture_count,texture_error,texture_index=0xffffffff;
static DWORD depth_count,depth_error,depth_index=0xffffffff,current_texture;
typedef char matrix_size[(sizeof(D3DMATRIX)==64)?1:-1];
typedef char viewport_size[(sizeof(D3DVIEWPORT7)==24)?1:-1];
static unsigned stage;
static HANDLE log_file=INVALID_HANDLE_VALUE,clear_file=INVALID_HANDLE_VALUE,draw_file=INVALID_HANDLE_VALUE;
static DWORD enumerated,matches,enum_error;
static D3DDEVICEDESC7 selected;
static int io_error,context,measuring;
static void zero(void *p,DWORD n){BYTE *b=p;while(n--)*b++=0;}
static int eq(const char *a,const char *b){return lstrcmpA(a,b)==0;}
static int same(const void *a,const void *b,DWORD n){const BYTE *x=a,*y=b;while(n--)if(*x++!=*y++)return 0;return 1;}
static int put(HANDLE h,const void *p,DWORD n){DWORD w=0;if(!WriteFile(h,p,n,&w,0)||w!=n||!FlushFileBuffers(h)){io_error=1;return 0;}return 1;}
static void text(const char *key,const char *v){char b[1100];if(measuring)return;if(lstrlenA(key)+lstrlenA(v)+4>=(int)sizeof(b)){io_error=1;return;}wsprintfA(b,"%s=%s\r\n",key,v);put(log_file,b,lstrlenA(b));}
static void number(const char *key,DWORD v){char b[32];wsprintfA(b,"%lu",v);text(key,b);}
static void hex(const char *key,const BYTE *p,DWORD n){static const char d[]="0123456789abcdef";char b[1041];DWORD i;if(n>520){io_error=1;return;}for(i=0;i<n;i++){b[2*i]=d[p[i]>>4];b[2*i+1]=d[p[i]&15];}b[n*2]=0;text(key,b);}
static int token(const char **cursor,char *out,unsigned cap){const char *p=*cursor;unsigned n=0;int q=0;while(*p==' '||*p=='\t')p++;if(!*p){*cursor=p;return 0;}if(*p=='"'){q=1;p++;}while(*p&&(q?*p!='"':(*p!=' '&&*p!='\t'))){if(*p=='"'||n+1>=cap)return -1;out[n++]=*p++;}if(q){if(*p!='"')return -1;p++;if(*p&&*p!=' '&&*p!='\t')return -1;}out[n]=0;*cursor=p;return n?1:-1;}
static HANDLE fresh(const char *prefix,const char *suffix){char b[256];if(lstrlenA(prefix)+lstrlenA(suffix)>=256)return INVALID_HANDLE_VALUE;lstrcpyA(b,prefix);lstrcatA(b,suffix);return CreateFileA(b,GENERIC_WRITE,FILE_SHARE_READ,0,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,0);}
static HRESULT CALLBACK enumerate(char *description,char *name,D3DDEVICEDESC7 *caps,void *ctx){(void)description;(void)name;if(ctx!=&context||!caps||++enumerated>16){enum_error=1;return D3DENUMRET_CANCEL;}if(same(&caps->deviceGUID,&rgb,16)){selected=*caps;matches++;}return D3DENUMRET_OK;}
static int modules(void){HANDLE h;MODULEENTRY32 m;DWORD n=0,error;char key[64];BOOL more;h=CreateToolhelp32Snapshot(TH32CS_SNAPMODULE,GetCurrentProcessId());if(h==INVALID_HANDLE_VALUE)return 0;zero(&m,sizeof(m));m.dwSize=sizeof(m);more=Module32First(h,&m);while(more){if(n>=64||!m.szExePath[0]||lstrlenA(m.szExePath)>=MAX_PATH){CloseHandle(h);return 0;}wsprintfA(key,"module%lu.path",n);hex(key,(BYTE*)m.szExePath,lstrlenA(m.szExePath));wsprintfA(key,"module%lu.bytes",n);number(key,m.modBaseSize);n++;more=Module32Next(h,&m);}error=GetLastError();CloseHandle(h);number("modules",n);number("modules.end_error",error);return n>0&&error==ERROR_NO_MORE_FILES&&!io_error;}
static DWORD visible_source[64*64];
static int format(const DDSURFACEDESC2 *s){return s->dwWidth==64&&s->dwHeight==64&&s->ddpfPixelFormat.dwFlags==DDPF_RGB&&s->ddpfPixelFormat.dwRGBBitCount==32&&s->ddpfPixelFormat.dwRBitMask==0xff0000&&s->ddpfPixelFormat.dwGBitMask==0xff00&&s->ddpfPixelFormat.dwBBitMask==0xff&&s->ddpfPixelFormat.dwRGBAlphaBitMask==0&&(s->ddsCaps.dwCaps&(DDSCAPS_SYSTEMMEMORY|DDSCAPS_3DDEVICE|DDSCAPS_OFFSCREENPLAIN))==(DDSCAPS_SYSTEMMEMORY|DDSCAPS_3DDEVICE|DDSCAPS_OFFSCREENPLAIN)&&!(s->ddsCaps.dwCaps&(DDSCAPS_PRIMARYSURFACE|DDSCAPS_VIDEOMEMORY));}
static int snapshot(IDirectDrawSurface7 *surface,HANDLE file,const char *stem){DDSURFACEDESC2 s;HRESULT hr;DWORD y;int good=0;char key[80];zero(&s,sizeof(s));s.dwSize=sizeof(s);hr=IDirectDrawSurface7_Lock(surface,0,&s,DDLOCK_WAIT|DDLOCK_READONLY,0);wsprintfA(key,"%s.lock",stem);number(key,(DWORD)hr);if(hr!=DD_OK)return 0;
 wsprintfA(key,"%s.pitch",stem);number(key,(DWORD)s.lPitch);wsprintfA(key,"%s.caps",stem);number(key,s.ddsCaps.dwCaps);
 if(format(&s)&&s.lpSurface&&s.lPitch>=256&&s.lPitch<=4096){good=1;for(y=0;y<64;y++){DWORD x;DWORD *row=(DWORD*)((BYTE*)s.lpSurface+y*s.lPitch);
 if(file==draw_file)for(x=0;x<64;x++)visible_source[y*64+x]=row[x]&0xffffffUL;
 if(!put(file,row,256)){good=0;break;}}}
 hr=IDirectDrawSurface7_Unlock(surface,0);wsprintfA(key,"%s.unlock",stem);number(key,(DWORD)hr);wsprintfA(key,"%s.valid",stem);number(key,good);return good&&hr==DD_OK;
}

#define PW 80
#define PH 80
static HWND panel,child,cover;
static HBRUSH brushes[3];
static int cancelled;
static HANDLE screens[2]={INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE};
static HANDLE post_file=INVALID_HANDLE_VALUE;
static DWORD screen[PW*PH];
static DDPIXELFORMAT native_format;
static HANDLE native_files[2]={INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE};
static DWORD native_mask;
static DWORD pack_rgb(DWORD v){
 if(native_format.dwRGBBitCount==32)return v&0xffffffUL;
 if(native_format.dwRBitMask==0xf800)return ((v>>8)&0xf800)|((v>>5)&0x7e0)|((v>>3)&31);
 return ((v>>9)&0x7c00)|((v>>6)&0x3e0)|((v>>3)&31);
}

static void snum(const char *key,DWORD value){char label[96];wsprintfA(label,"p.s%u.%s",stage,key);number(label,value);}
static int scall(const char *key,HRESULT hr){snum(key,(DWORD)hr);return hr==DD_OK;}
static int inrect(int x,int y,const RECT *r){return x>=r->left&&x<r->right&&y>=r->top&&y<r->bottom;}
static int covered(int x,int y){return (stage==1||stage==2)&&x>=24&&x<48&&y>=24&&y<48;}
static DWORD expected(unsigned x,unsigned y,int after){
 if(covered((int)x,(int)y))return pack_rgb(0xff00ffUL);
 if(x>=8&&x<56&&y>=8&&y<56)return after?pack_rgb(visible_source[y*64+x]):0;
 return pack_rgb(255);
}
static LRESULT CALLBACK wnd(HWND h,UINT m,WPARAM w,LPARAM l){
 if(m==WM_CLOSE){cancelled=1;return 0;}
 if(m==WM_ERASEBKGND)return 1;
 if(m==WM_PAINT){PAINTSTRUCT ps;RECT r;HDC dc=BeginPaint(h,&ps);GetClientRect(h,&r);FillRect(dc,&r,brushes[h==child?1:h==cover?2:0]);EndPaint(h,&ps);return 0;}
 return DefWindowProcA(h,m,w,l);
}
static void pump(DWORD ms){MSG m;DWORD start=GetTickCount();do{while(PeekMessageA(&m,0,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageA(&m);}Sleep(5);}while(!cancelled&&(DWORD)(GetTickCount()-start)<ms);}
static int windows(void){WNDCLASSA c;HINSTANCE inst=GetModuleHandleA(0);zero(&c,sizeof(c));c.lpfnWndProc=wnd;c.hInstance=inst;c.lpszClassName="XWNScenePresent09c";
 brushes[0]=CreateSolidBrush(RGB(0,0,255));brushes[1]=CreateSolidBrush(RGB(0,0,0));brushes[2]=CreateSolidBrush(RGB(255,0,255));
 if(!brushes[0]||!brushes[1]||!brushes[2]||!RegisterClassA(&c))return 0;
 panel=CreateWindowExA(WS_EX_TOPMOST|WS_EX_TOOLWINDOW,c.lpszClassName,"XWN combined 3D scene",WS_POPUP|WS_CLIPCHILDREN,64,64,PW,PH,0,0,inst,0);
 if(!panel)return 0;
 child=CreateWindowA(c.lpszClassName,"owned target",WS_CHILD|WS_VISIBLE|WS_CLIPSIBLINGS,8,8,48,48,panel,0,inst,0);
 cover=CreateWindowA(c.lpszClassName,"owned GDI occluder",WS_CHILD|WS_CLIPSIBLINGS,24,24,24,24,panel,0,inst,0);
 return child&&cover;
}
static int capture(int after,POINT origin){HDC dc=0,mem=0;HBITMAP bm=0;HGDIOBJ old=0;BYTE *bits=0;struct {BITMAPINFOHEADER bmiHeader;DWORD masks[3];} bi;unsigned i;DWORD bad=0;int ok=0,clean=1;char label[40];
 zero(&bi,sizeof(bi));bi.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);bi.bmiHeader.biWidth=PW;bi.bmiHeader.biHeight=-PH;bi.bmiHeader.biPlanes=1;bi.bmiHeader.biBitCount=(WORD)native_format.dwRGBBitCount;
 bi.bmiHeader.biCompression=BI_BITFIELDS;bi.masks[0]=native_format.dwRBitMask;bi.masks[1]=native_format.dwGBitMask;bi.masks[2]=native_format.dwBBitMask;
 dc=GetDC(0);if(!dc)goto done;mem=CreateCompatibleDC(dc);if(!mem)goto done;
 bm=CreateDIBSection(dc,(BITMAPINFO*)&bi,DIB_RGB_COLORS,(void**)&bits,0,0);if(!bm||!bits)goto done;
 old=SelectObject(mem,bm);if(!old||old==HGDI_ERROR)goto done;
 if(!BitBlt(mem,0,0,PW,PH,dc,origin.x,origin.y,SRCCOPY)||!GdiFlush())goto done;
 for(i=0;i<PW*PH;i++){screen[i]=(native_format.dwRGBBitCount==32?((DWORD*)bits)[i]:((WORD*)bits)[i])&native_mask;if(screen[i]!=expected(i%PW,i/PW,after))bad++;}
 if(!put(screens[after?1:0],screen,sizeof(screen)))goto done;
 ok=1;
done:
 if(old&&old!=HGDI_ERROR)clean&=SelectObject(mem,old)!=0;
 if(bm)clean&=DeleteObject(bm)!=0;
 if(mem)clean&=DeleteDC(mem)!=0;
 if(dc)clean&=ReleaseDC(0,dc)!=0;
 wsprintfA(label,"%s.capture",after?"after":"before");snum(label,ok&&clean);
 wsprintfA(label,"%s.mismatches",after?"after":"before");snum(label,bad);
 return ok&&clean&&!bad;
}
static int clip(IDirectDrawClipper *c,POINT origin){struct {RGNDATAHEADER h;RECT r[64];} data;DWORD bytes=0,i;int x,y,bad=0;char label[64];
 if(!scall("clip.size",IDirectDrawClipper_GetClipList(c,0,0,&bytes)))return 0;
 snum("clip.bytes",bytes);if(bytes<sizeof(RGNDATAHEADER)||bytes>sizeof(data))return 0;
 zero(&data,sizeof(data));if(!scall("clip.list",IDirectDrawClipper_GetClipList(c,0,(RGNDATA*)&data,&bytes)))return 0;
 if(data.h.dwSize!=sizeof(RGNDATAHEADER)||data.h.iType!=RDH_RECTANGLES||!data.h.nCount||data.h.nCount>64||data.h.nRgnSize!=data.h.nCount*sizeof(RECT)||bytes!=sizeof(RGNDATAHEADER)+data.h.nRgnSize)return 0;
 snum("clip.count",data.h.nCount);
 for(i=0;i<data.h.nCount;i++){
  RECT *r=&data.r[i];
  if(r->left<origin.x+8||r->right>origin.x+56||r->top<origin.y+8||r->bottom>origin.y+56||r->left>=r->right||r->top>=r->bottom)bad=1;
#define EDGE(n) wsprintfA(label,"clip.r%lu." #n,i);snum(label,(DWORD)r->n)
  EDGE(left);EDGE(top);EDGE(right);EDGE(bottom);
#undef EDGE
 }
 for(y=0;y<PH;y++)for(x=0;x<PW;x++){unsigned found=0;int want=x>=8&&x<56&&y>=8&&y<56&&!covered(x,y);for(i=0;i<data.h.nCount;i++)found+=inrect(x+origin.x,y+origin.y,&data.r[i]);if(found!=(unsigned)want)bad=1;}
 snum("clip.exact",!bad);return !bad;
}
static int native_bytes(IDirectDrawSurface7 *surface,int post){
 DDSURFACEDESC2 d;HRESULT hr;DWORD x,y,bad=0,row[64],bpp=native_format.dwRGBBitCount/8;int good=0;char label[80];
 zero(&d,sizeof(d));d.dwSize=sizeof(d);hr=IDirectDrawSurface7_Lock(surface,0,&d,DDLOCK_WAIT|(post?DDLOCK_READONLY:0),0);
 wsprintfA(label,"native%u.lock",post);if(!scall(label,hr))return 0;
 if(d.dwWidth==64&&d.dwHeight==64&&d.lpSurface&&d.lPitch>=(LONG)(64*bpp)&&d.lPitch<=4096&&d.lPitch%(LONG)bpp==0&&same(&d.ddpfPixelFormat,&native_format,sizeof(native_format))&&(d.ddsCaps.dwCaps&(DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN))==(DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN)&&!(d.ddsCaps.dwCaps&(DDSCAPS_PRIMARYSURFACE|DDSCAPS_VIDEOMEMORY))){
  good=1;
  for(y=0;y<64;y++){
   BYTE *dest=(BYTE*)d.lpSurface+y*d.lPitch;
   for(x=0;x<64;x++){
    DWORD want=pack_rgb(visible_source[y*64+x]);
    if(!post){if(bpp==4)((DWORD*)dest)[x]=want;else ((WORD*)dest)[x]=(WORD)want;}
    row[x]=(bpp==4?((DWORD*)dest)[x]:((WORD*)dest)[x])&native_mask;if(row[x]!=want)bad++;
   }
   if(!put(native_files[post],row,sizeof(row))){good=0;break;}
  }
 }
 hr=IDirectDrawSurface7_Unlock(surface,0);wsprintfA(label,"native%u.unlock",post);scall(label,hr);
 wsprintfA(label,"native%u.pitch",post);snum(label,(DWORD)d.lPitch);
 wsprintfA(label,"native%u.caps",post);snum(label,d.ddsCaps.dwCaps);
 wsprintfA(label,"native%u.valid",post);snum(label,good);wsprintfA(label,"native%u.mismatches",post);snum(label,bad);
 return good&&!bad&&hr==DD_OK;
}
static int texture_acceptable(const DDPIXELFORMAT *p){return p->dwSize==sizeof(*p)&&(p->dwFlags==DDPF_RGB||p->dwFlags==(DDPF_RGB|DDPF_ALPHAPIXELS))&&p->dwFourCC==0&&p->dwRGBBitCount==32&&p->dwRBitMask==0xff0000&&p->dwGBitMask==0xff00&&p->dwBBitMask==0xff&&p->dwRGBAlphaBitMask==((p->dwFlags&DDPF_ALPHAPIXELS)?0xff000000:0);}
static HRESULT CALLBACK texture_enum(DDPIXELFORMAT *p,void *ctx){if(ctx!=&context||!p||p->dwSize!=sizeof(*p)||texture_count>=64){texture_error=1;return D3DENUMRET_CANCEL;}texture_formats[texture_count]=*p;if(texture_index==0xffffffff&&texture_acceptable(p)){texture_index=texture_count;texture_format=*p;}texture_count++;return D3DENUMRET_OK;}
static DWORD texel(DWORD x,DWORD y){
 static const DWORD colors[2][4]={{0x206040,0x40c080,0x608020,0x80a060},{0x802060,0xc04080,0xa06020,0xe08040}};
 return colors[current_texture][(y/4)*2+x/4]|((texture_format.dwFlags&DDPF_ALPHAPIXELS)?0xff000000:0);
}
static int texture_bytes(IDirectDrawSurface7 *surface,HANDLE file,const char *stem,int upload){DDSURFACEDESC2 s;HRESULT hr;DWORD x,y;int good=0;char key[80];zero(&s,sizeof(s));s.dwSize=sizeof(s);hr=IDirectDrawSurface7_Lock(surface,0,&s,DDLOCK_WAIT|(upload?0:DDLOCK_READONLY),0);wsprintfA(key,"%s.lock",stem);number(key,(DWORD)hr);if(hr!=DD_OK)return 0;
 wsprintfA(key,"%s.pitch",stem);number(key,(DWORD)s.lPitch);wsprintfA(key,"%s.caps",stem);number(key,s.ddsCaps.dwCaps);wsprintfA(key,"%s.format",stem);hex(key,(BYTE*)&s.ddpfPixelFormat,sizeof(s.ddpfPixelFormat));
 if(s.dwWidth==8&&s.dwHeight==8&&s.lpSurface&&s.lPitch>=32&&s.lPitch<=4096&&same(&s.ddpfPixelFormat,&texture_format,sizeof(texture_format))&&(s.ddsCaps.dwCaps&(DDSCAPS_TEXTURE|DDSCAPS_SYSTEMMEMORY))==(DDSCAPS_TEXTURE|DDSCAPS_SYSTEMMEMORY)&&!(s.ddsCaps.dwCaps&(DDSCAPS_PRIMARYSURFACE|DDSCAPS_VIDEOMEMORY|DDSCAPS_MIPMAP))){good=1;for(y=0;y<8;y++){DWORD *row=(DWORD*)((BYTE*)s.lpSurface+y*s.lPitch);if(upload)for(x=0;x<8;x++)row[x]=texel(x,y);if(!put(file,row,32)){good=0;break;}}}
 hr=IDirectDrawSurface7_Unlock(surface,0);wsprintfA(key,"%s.unlock",stem);number(key,(DWORD)hr);wsprintfA(key,"%s.valid",stem);number(key,good);return good&&hr==DD_OK;
}
static int depth_acceptable(const DDPIXELFORMAT *p){return p->dwSize==sizeof(*p)&&p->dwFlags==DDPF_ZBUFFER&&p->dwFourCC==0&&(p->dwZBufferBitDepth==16||p->dwZBufferBitDepth==24||p->dwZBufferBitDepth==32)&&p->dwStencilBitDepth==0&&p->dwStencilBitMask==0;}
static HRESULT CALLBACK depth_enum(DDPIXELFORMAT *p,void *ctx){if(ctx!=&context||!p||p->dwSize!=sizeof(*p)||depth_count>=64){depth_error=1;return D3DENUMRET_CANCEL;}depth_formats[depth_count]=*p;if(depth_index==0xffffffff&&depth_acceptable(p)){depth_index=depth_count;depth_format=*p;}depth_count++;return D3DENUMRET_OK;}
#define HR(key,expr) do{hr=(expr);number(key,(DWORD)hr);if(hr!=DD_OK)goto done;}while(0)
#define RS(key,state,value) do{DWORD actual=0xffffffffUL;HR(key,IDirect3DDevice7_SetRenderState(dev,state,value));HR("get." key,IDirect3DDevice7_GetRenderState(dev,state,&actual));number("value." key,actual);if(actual!=(DWORD)(value))goto done;}while(0)
static void identity(D3DMATRIX *m){zero(m,sizeof(*m));m->_11=m->_22=m->_33=m->_44=1;}
static int transformed(IDirect3DDevice7 *dev,IDirectDrawSurface7 *target,IDirectDrawSurface7 **textures){
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
 wsprintfA(stem,"s%u.clear_capture",stage);if(!measuring&&!snapshot(target,clear_file,stem))goto done;
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
 wsprintfA(stem,"s%u.draw_capture",stage);if(!measuring&&!snapshot(target,draw_file,stem))goto done;
 wsprintfA(key,"s%u.complete",stage);number(key,1);ok=1;
 done:if(scene){number("cleanup.end_scene",(DWORD)IDirect3DDevice7_EndScene(dev));ok=0;}return ok;
#undef MATRIX
#undef SH
}

/* The 64-bit counters are serialized as two DWORDs; no CRT division helpers. */
typedef struct {DWORD cb,faults,peak_ws,ws,peak_paged,paged,peak_nonpaged,nonpaged,commit,peak_commit;} COUNTERS;
typedef char counters_size[(sizeof(COUNTERS)==40)?1:-1];
typedef BOOL (WINAPI *MEMORY_FN)(HANDLE,COUNTERS*,DWORD);
static HMODULE memory_lib;
static MEMORY_FN memory_fn;
static LARGE_INTEGER clock_frequency;
static void wide(const char *key,LARGE_INTEGER value){char b[96];wsprintfA(b,"%s.low",key);number(b,value.LowPart);wsprintfA(b,"%s.high",key);number(b,(DWORD)value.HighPart);}
static int memory_sample(const char *stem){COUNTERS m;char key[96];zero(&m,sizeof(m));m.cb=sizeof(m);
 if(!memory_fn(GetCurrentProcess(),&m,sizeof(m))||m.cb!=sizeof(m))return 0;
#define MC(n,v) wsprintfA(key,"loop.mem.%s." n,stem);number(key,v)
 MC("ws",m.ws);MC("peak_ws",m.peak_ws);MC("commit",m.commit);MC("peak_commit",m.peak_commit);MC("faults",m.faults);
#undef MC
 return m.ws>0&&m.ws<=m.peak_ws&&m.commit<=m.peak_commit&&!io_error;
}
static int loop_init(void){char path[MAX_PATH];UINT n;union{FARPROC raw;MEMORY_FN fn;} u;
 n=GetSystemDirectoryA(path,sizeof(path));if(!n||n+11>=sizeof(path))return 0;lstrcatA(path,"\\psapi.dll");
 memory_lib=LoadLibraryA(path);number("loop.psapi.load",memory_lib!=0);if(!memory_lib)return 0;
 u.raw=GetProcAddress(memory_lib,"GetProcessMemoryInfo");memory_fn=u.fn;number("loop.psapi.entry",u.raw!=0);if(!u.raw)return 0;
 if(!QueryPerformanceFrequency(&clock_frequency)||clock_frequency.QuadPart<=0)return 0;
 wide("loop.frequency",clock_frequency);number("loop.frames_per_stage",32);number("loop.batch_deadline_ms",30000);
 return memory_sample("before");
}
static int stamp(LARGE_INTEGER *v){return QueryPerformanceCounter(v)&&v->QuadPart>=0;}
static int target_ready(IDirectDrawSurface7 *target){DDSURFACEDESC2 d;HRESULT hr;int good;
 zero(&d,sizeof(d));d.dwSize=sizeof(d);hr=IDirectDrawSurface7_Lock(target,0,&d,DDLOCK_WAIT|DDLOCK_READONLY,0);if(hr!=DD_OK)return 0;
 good=format(&d)&&d.lpSurface&&d.lPitch>=256&&d.lPitch<=4096;
 return IDirectDrawSurface7_Unlock(target,0)==DD_OK&&good;
}
static int upload_frame(IDirectDrawSurface7 *target,IDirectDrawSurface7 *bridge){DDSURFACEDESC2 a,b;HRESULT hr;DWORD x,y,bpp=native_format.dwRGBBitCount/8;int good=0;
 zero(&a,sizeof(a));a.dwSize=sizeof(a);hr=IDirectDrawSurface7_Lock(target,0,&a,DDLOCK_WAIT|DDLOCK_READONLY,0);if(hr!=DD_OK)return 0;
 if(format(&a)&&a.lpSurface&&a.lPitch>=256&&a.lPitch<=4096){
  for(y=0;y<64;y++)for(x=0;x<64;x++)visible_source[y*64+x]=((DWORD*)((BYTE*)a.lpSurface+y*a.lPitch))[x]&0xffffffUL;
  good=1;
 }
 hr=IDirectDrawSurface7_Unlock(target,0);if(!good||hr!=DD_OK)return 0;
 zero(&b,sizeof(b));b.dwSize=sizeof(b);hr=IDirectDrawSurface7_Lock(bridge,0,&b,DDLOCK_WAIT,0);if(hr!=DD_OK)return 0;good=0;
 if(b.dwWidth==64&&b.dwHeight==64&&b.lpSurface&&b.lPitch>=(LONG)(64*bpp)&&b.lPitch<=4096&&b.lPitch%(LONG)bpp==0&&same(&b.ddpfPixelFormat,&native_format,sizeof(native_format))){
  for(y=0;y<64;y++)for(x=0;x<64;x++){DWORD v=pack_rgb(visible_source[y*64+x]);BYTE *row=(BYTE*)b.lpSurface+y*b.lPitch;if(bpp==4)((DWORD*)row)[x]=v;else ((WORD*)row)[x]=(WORD)v;}
  good=1;
 }
 return IDirectDrawSurface7_Unlock(bridge,0)==DD_OK&&good;
}
static int repeated(IDirect3DDevice7 *dev,IDirectDrawSurface7 *target,IDirectDrawSurface7 **textures,IDirectDrawSurface7 *bridge,IDirectDrawSurface7 *primary,RECT *to,RECT *from){
 LARGE_INTEGER start,end,a,b,c,d,render,upload,present;DWORD i,tick=0,elapsed;char key[96],stem[32];int good=0;
 render.QuadPart=upload.QuadPart=present.QuadPart=0;
 wsprintfA(stem,"s%u.before",stage);if(!memory_sample(stem))return 0;
 tick=GetTickCount();if(!stamp(&start))return 0;
 measuring=1;
 for(i=0;i<32;i++){
  if((DWORD)(GetTickCount()-tick)>=30000||!stamp(&a))goto done;
  if(!transformed(dev,target,textures)||!target_ready(target)||!stamp(&b)||b.QuadPart<a.QuadPart)goto done;
  if(!upload_frame(target,bridge)||!stamp(&c)||c.QuadPart<b.QuadPart)goto done;
  if(IDirectDrawSurface7_Blt(primary,to,bridge,from,DDBLT_DONOTWAIT,0)!=DD_OK||!GdiFlush()||!stamp(&d)||d.QuadPart<c.QuadPart)goto done;
  render.QuadPart+=b.QuadPart-a.QuadPart;upload.QuadPart+=c.QuadPart-b.QuadPart;present.QuadPart+=d.QuadPart-c.QuadPart;
 }
 if(!stamp(&end)||end.QuadPart<start.QuadPart)goto done;
 elapsed=GetTickCount()-tick;if(elapsed>=30000)goto done;
 good=1;
done:
 measuring=0;
 wsprintfA(key,"loop.s%u.frames",stage);number(key,i);if(!good)return 0;
#define LW(n,v) wsprintfA(key,"loop.s%u." n,stage);wide(key,v)
 LW("start",start);LW("end",end);LW("render",render);LW("upload",upload);LW("present",present);
#undef LW
 wsprintfA(key,"loop.s%u.elapsed_ms",stage);number(key,elapsed);
 wsprintfA(stem,"s%u.after",stage);return memory_sample(stem)&&!io_error;
}

static int run(HWND w,const char *backend){typedef HRESULT(WINAPI *CREATE)(GUID*,void**,REFIID,IUnknown*);union{FARPROC raw;CREATE create;}fn;HMODULE m=0;IDirectDraw7 *dd=0;IDirect3D7 *d3d=0;IDirectDrawSurface7 *target=0,*textures[2]={0,0},*depth=0,*attached_check=0;IDirect3DDevice7 *dev=0;HRESULT hr;DDSURFACEDESC2 s;int ok=0,clean=1,attached=0;ULONG refs;DWORD i;char key[80];DDSCAPS2 caps;IDirectDrawSurface7 *primary=0,*bridge=0;IDirectDrawClipper *cl=0;HWND owner=0;DDPIXELFORMAT pf;
 m=LoadLibraryA("ddraw.dll");number("ddraw.load",m!=0);if(!m)goto done;fn.raw=GetProcAddress(m,"DirectDrawCreateEx");number("ddraw.entry",fn.raw!=0);if(!fn.raw)goto done;
 HR("ddraw.create",fn.create(eq(backend,"hel")?(GUID*)DDCREATE_EMULATIONONLY:0,(void**)&dd,&dd7,0));
 HR("ddraw.cooperative",IDirectDraw7_SetCooperativeLevel(dd,w,DDSCL_NORMAL));
 HR("d3d.query",IDirectDraw7_QueryInterface(dd,&d3d7,(void**)&d3d));
 HR("enum.hr",IDirect3D7_EnumDevices(d3d,enumerate,&context));number("enum.count",enumerated);number("enum.matches",matches);number("enum.error",enum_error);
 if(enum_error||matches!=1||(selected.dwDevCaps&(D3DDEVCAPS_HWRASTERIZATION|D3DDEVCAPS_HWTRANSFORMANDLIGHT))||!(selected.dwDeviceRenderBitDepth&DDBD_32))goto done;
 hex("device.caps",(BYTE*)&selected,sizeof(selected));number("vertex.stride",sizeof(VERTEX));number("vertex.fvf",D3DFVF_XYZ|D3DFVF_TEX1);
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;s.dwWidth=s.dwHeight=64;s.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN|DDSCAPS_3DDEVICE;s.ddpfPixelFormat.dwSize=sizeof(DDPIXELFORMAT);s.ddpfPixelFormat.dwFlags=DDPF_RGB;s.ddpfPixelFormat.dwRGBBitCount=32;s.ddpfPixelFormat.dwRBitMask=0xff0000;s.ddpfPixelFormat.dwGBitMask=0xff00;s.ddpfPixelFormat.dwBBitMask=0xff;
 HR("target.create",IDirectDraw7_CreateSurface(dd,&s,&target,0));
 HR("zformats.hr",IDirect3D7_EnumZBufferFormats(d3d,&selected.deviceGUID,depth_enum,&context));number("zformats.count",depth_count);number("zformats.error",depth_error);number("zformats.selected",depth_index);
 for(i=0;i<depth_count;i++){wsprintfA(key,"zformat%lu",i);hex(key,(BYTE*)&depth_formats[i],sizeof(depth_formats[i]));}
 if(depth_error||depth_index==0xffffffff)goto done;
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
 HR("device.create",IDirect3D7_CreateDevice(d3d,&selected.deviceGUID,target,&dev));
 HR("tformats.hr",IDirect3DDevice7_EnumTextureFormats(dev,texture_enum,&context));number("tformats.count",texture_count);number("tformats.error",texture_error);number("tformats.selected",texture_index);
 for(i=0;i<texture_count;i++){wsprintfA(key,"tformat%lu",i);hex(key,(BYTE*)&texture_formats[i],sizeof(texture_formats[i]));}
 if(texture_error||texture_index==0xffffffff)goto done;
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;s.dwWidth=s.dwHeight=8;s.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_TEXTURE;s.ddpfPixelFormat=texture_format;
 for(current_texture=0;current_texture<2;current_texture++){
  wsprintfA(key,"texture%lu.create",current_texture);HR(key,IDirectDraw7_CreateSurface(dd,&s,&textures[current_texture],0));
  wsprintfA(key,"source%lu.before",current_texture);if(!texture_bytes(textures[current_texture],source_before,key,1))goto done;
 }


 RS("state.clipping",D3DRENDERSTATE_CLIPPING,TRUE);RS("state.colorvertex",D3DRENDERSTATE_COLORVERTEX,TRUE);
 RS("state.zfunc",D3DRENDERSTATE_ZFUNC,D3DCMP_LESS);RS("state.z",D3DRENDERSTATE_ZENABLE,D3DZB_TRUE);RS("state.zwrite",D3DRENDERSTATE_ZWRITEENABLE,TRUE);RS("state.lighting",D3DRENDERSTATE_LIGHTING,FALSE);RS("state.cull",D3DRENDERSTATE_CULLMODE,D3DCULL_NONE);RS("state.fill",D3DRENDERSTATE_FILLMODE,D3DFILL_SOLID);RS("state.shade",D3DRENDERSTATE_SHADEMODE,D3DSHADE_FLAT);RS("state.fog",D3DRENDERSTATE_FOGENABLE,FALSE);RS("state.alpha",D3DRENDERSTATE_ALPHABLENDENABLE,FALSE);RS("state.alphatest",D3DRENDERSTATE_ALPHATESTENABLE,FALSE);RS("state.dither",D3DRENDERSTATE_DITHERENABLE,FALSE);RS("state.specular",D3DRENDERSTATE_SPECULARENABLE,FALSE);RS("state.antialias",D3DRENDERSTATE_ANTIALIAS,D3DANTIALIAS_NONE);
#define TSS(label,unit,state,value) do{DWORD actual=0xffffffff;HR(label,IDirect3DDevice7_SetTextureStageState(dev,unit,state,value));HR("get." label,IDirect3DDevice7_GetTextureStageState(dev,unit,state,&actual));number("value." label,actual);if(actual!=(DWORD)(value))goto done;}while(0)
 TSS("stage0.op",0,D3DTSS_COLOROP,D3DTOP_SELECTARG1);TSS("stage0.arg",0,D3DTSS_COLORARG1,D3DTA_TEXTURE);TSS("stage0.alpha",0,D3DTSS_ALPHAOP,D3DTOP_DISABLE);TSS("stage1.op",1,D3DTSS_COLOROP,D3DTOP_DISABLE);

 TSS("stage0.min",0,D3DTSS_MINFILTER,D3DTFN_POINT);TSS("stage0.mag",0,D3DTSS_MAGFILTER,D3DTFG_POINT);TSS("stage0.mip",0,D3DTSS_MIPFILTER,D3DTFP_NONE);TSS("stage0.u",0,D3DTSS_ADDRESSU,D3DTADDRESS_CLAMP);TSS("stage0.v",0,D3DTSS_ADDRESSV,D3DTADDRESS_CLAMP);TSS("stage0.coord",0,D3DTSS_TEXCOORDINDEX,0);TSS("stage0.transform",0,D3DTSS_TEXTURETRANSFORMFLAGS,D3DTTFF_DISABLE);
 zero(&s,sizeof(s));s.dwSize=sizeof(s);HR("p.mode",IDirectDraw7_GetDisplayMode(dd,&s));
 number("p.mode.width",s.dwWidth);number("p.mode.height",s.dwHeight);number("p.mode.bits",s.ddpfPixelFormat.dwRGBBitCount);
 if(s.dwWidth<640||s.dwHeight<480)goto done;
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS;s.ddsCaps.dwCaps=DDSCAPS_PRIMARYSURFACE;
 HR("p.primary.create",IDirectDraw7_CreateSurface(dd,&s,&primary,0));
 zero(&pf,sizeof(pf));pf.dwSize=sizeof(pf);HR("p.primary.format",IDirectDrawSurface7_GetPixelFormat(primary,&pf));hex("p.format",(BYTE*)&pf,sizeof(pf));
 if(pf.dwFlags!=DDPF_RGB||pf.dwRGBAlphaBitMask||!((pf.dwRGBBitCount==32&&pf.dwRBitMask==0xff0000&&pf.dwGBitMask==0xff00&&pf.dwBBitMask==255)||(pf.dwRGBBitCount==16&&pf.dwBBitMask==31&&((pf.dwRBitMask==0xf800&&pf.dwGBitMask==0x7e0)||(pf.dwRBitMask==0x7c00&&pf.dwGBitMask==0x3e0)))))goto done;
 native_format=pf;native_mask=pf.dwRBitMask|pf.dwGBitMask|pf.dwBBitMask;
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;s.dwWidth=s.dwHeight=64;s.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN;s.ddpfPixelFormat=pf;
 HR("p.bridge.create",IDirectDraw7_CreateSurface(dd,&s,&bridge,0));
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
  if(!capture(0,p)||!clip(cl,p)||!transformed(dev,target,textures)||!native_bytes(bridge,0))goto done;
  to.left=p.x;to.top=p.y;to.right=p.x+64;to.bottom=p.y+64;
  if(!scall("primary.blit",IDirectDrawSurface7_Blt(primary,&to,bridge,&from,DDBLT_DONOTWAIT,0))||!GdiFlush())goto done;
  if(!repeated(dev,target,textures,bridge,primary,&to,&from))goto done;
  Sleep(100);if(!capture(1,p)||!native_bytes(bridge,1))goto done;
  wsprintfA(label,"p.s%u.post",stage);if(!snapshot(target,post_file,label))goto done;
  snum("complete",1);pump(750);if(cancelled)goto done;
 }
 number("stages",stage);
 for(current_texture=0;current_texture<2;current_texture++){
  wsprintfA(key,"source%lu.after",current_texture);if(!texture_bytes(textures[current_texture],source_after,key,0))goto done;
 }
 HR("texture.unbind",IDirect3DDevice7_SetTexture(dev,0,0));
 ok=modules();number("modules.ok",ok);ok=ok&&!io_error;
done:
 if(primary&&cl){hr=IDirectDrawSurface7_SetClipper(primary,0);number("p.primary.detach",(DWORD)hr);clean&=hr==DD_OK;}
 if(bridge){refs=IDirectDrawSurface7_Release(bridge);number("p.release.bridge",refs);clean&=refs==0;}
 if(primary){refs=IDirectDrawSurface7_Release(primary);number("p.release.primary",refs);clean&=refs==0;}
 if(cl){refs=IDirectDrawClipper_Release(cl);number("p.release.clipper",refs);clean&=refs==0;}
 if(dev){refs=IDirect3DDevice7_Release(dev);number("release.device",refs);clean&=refs==0;}
 for(i=0;i<2;i++)if(textures[i]){refs=IDirectDrawSurface7_Release(textures[i]);wsprintfA(key,"release.texture%lu",i);number(key,refs);clean&=refs==0;}
 if(attached_check)IDirectDrawSurface7_Release(attached_check);
 if(attached){hr=IDirectDrawSurface7_DeleteAttachedSurface(target,0,depth);number("depth.detach",(DWORD)hr);clean&=hr==DD_OK;}
 if(depth){refs=IDirectDrawSurface7_Release(depth);number("release.depth",refs);clean&=refs==0;}
 if(target){refs=IDirectDrawSurface7_Release(target);number("release.target",refs);clean&=refs==0;}
 if(d3d)number("release.d3d",IDirect3D7_Release(d3d));
 if(dd){refs=IDirectDraw7_Release(dd);number("release.ddraw",refs);clean&=refs==0;}
 if(m){int unloaded=FreeLibrary(m)!=0;number("ddraw.unload",unloaded);clean&=unloaded;}
 if(!memory_sample("released"))clean=0;
 return ok&&clean;
}
void WINAPI mainCRTStartup(void){const char *s=GetCommandLineA();char exe[512],backend[16],prefix[224],extra[2];unsigned i;HWND w=0;OSVERSIONINFOA os;int code=1;
 SetErrorMode(SEM_FAILCRITICALERRORS|SEM_NOGPFAULTERRORBOX);
 if(token(&s,exe,sizeof(exe))!=1||token(&s,backend,sizeof(backend))!=1||token(&s,prefix,sizeof(prefix))!=1||token(&s,extra,sizeof(extra))!=0||(!eq(backend,"default")&&!eq(backend,"hel")))ExitProcess(2);
 log_file=fresh(prefix,".txt");if(log_file==INVALID_HANDLE_VALUE)ExitProcess(2);clear_file=fresh(prefix,"-clear.bin");draw_file=fresh(prefix,"-draw.bin");if(clear_file==INVALID_HANDLE_VALUE||draw_file==INVALID_HANDLE_VALUE)goto done;
 source_before=fresh(prefix,"-source-before.bin");source_after=fresh(prefix,"-source-after.bin");if(source_before==INVALID_HANDLE_VALUE||source_after==INVALID_HANDLE_VALUE)goto done;
 text("schema","xwn-scene-loop-1");text("backend",backend);text("scope","repeated-windowed-xyz-software-phase-costs");number("width",64);number("height",64);
 zero(&os,sizeof(os));os.dwOSVersionInfoSize=sizeof(os);if(!GetVersionExA(&os))goto done;number("os.major",os.dwMajorVersion);number("os.minor",os.dwMinorVersion);number("os.build",os.dwBuildNumber);
 screens[0]=fresh(prefix,"-screen-before.bin");screens[1]=fresh(prefix,"-screen-after.bin");post_file=fresh(prefix,"-post.bin");
 if(screens[0]==INVALID_HANDLE_VALUE||screens[1]==INVALID_HANDLE_VALUE||post_file==INVALID_HANDLE_VALUE)goto done;
 native_files[0]=fresh(prefix,"-native-before.bin");native_files[1]=fresh(prefix,"-native-after.bin");
 if(native_files[0]==INVALID_HANDLE_VALUE||native_files[1]==INVALID_HANDLE_VALUE)goto done;
 if(!loop_init())goto done;
 if(windows()){w=panel;}number("window.created",w!=0);if(w&&run(w,backend))code=0;

done:
 if(memory_lib){int ok=FreeLibrary(memory_lib)!=0;number("loop.psapi.unload",ok);if(!ok)code=1;}
 if(panel&&!DestroyWindow(panel))code=1;
 for(i=0;i<3;i++)if(brushes[i]&&!DeleteObject(brushes[i]))code=1;
 for(i=0;i<2;i++)if(screens[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(screens[i]))io_error=1;
 for(i=0;i<2;i++)if(native_files[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(native_files[i]))io_error=1;
 if(post_file!=INVALID_HANDLE_VALUE&&!CloseHandle(post_file))io_error=1;
 if(clear_file!=INVALID_HANDLE_VALUE&&!CloseHandle(clear_file))io_error=1;
 if(draw_file!=INVALID_HANDLE_VALUE&&!CloseHandle(draw_file))io_error=1;
 if(source_before!=INVALID_HANDLE_VALUE&&!CloseHandle(source_before))io_error=1;
 if(source_after!=INVALID_HANDLE_VALUE&&!CloseHandle(source_after))io_error=1;
 if(io_error)code=4;
 number("exit",code);text("result",code==0?"CAPTURED":"FAILED");text("end","complete");if(!CloseHandle(log_file))io_error=1;ExitProcess(io_error?4:(UINT)code);
}
