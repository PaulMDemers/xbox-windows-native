"""MIT. Explicit native-format staging; no display mode changes."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1];p=W/'src/samples/graphics-ladder/scenepresent.c'
s=p.read_text(encoding='utf-8');prior=hashlib.sha256(p.read_bytes()).hexdigest()
s=s.replace(' * RGB32 desktop required.', ' * RGB32 offscreen render with explicit native-format CPU staging.')
s=s.replace('static DWORD screen[PW*PH];', '''static DWORD screen[PW*PH];
static DDPIXELFORMAT native_format;
static HANDLE native_files[2]={INVALID_HANDLE_VALUE,INVALID_HANDLE_VALUE};
static DWORD native_mask;
static DWORD pack_rgb(DWORD v){
 if(native_format.dwRGBBitCount==32)return v&0xffffffUL;
 if(native_format.dwRBitMask==0xf800)return ((v>>8)&0xf800)|((v>>5)&0x7e0)|((v>>3)&31);
 return ((v>>9)&0x7c00)|((v>>6)&0x3e0)|((v>>3)&31);
}
''')
s=s.replace('return 0xff00ffUL;','return pack_rgb(0xff00ffUL);').replace('return after?visible_source[y*64+x]:0;', 'return after?pack_rgb(visible_source[y*64+x]):0;').replace(' return 255;',' return pack_rgb(255);')
s=s.replace('DWORD *bits=0;BITMAPINFO bi;', 'BYTE *bits=0;struct {BITMAPINFOHEADER bmiHeader;DWORD masks[3];} bi;')
s=s.replace('bi.bmiHeader.biBitCount=32;', '''bi.bmiHeader.biBitCount=(WORD)native_format.dwRGBBitCount;
 bi.bmiHeader.biCompression=BI_BITFIELDS;bi.masks[0]=native_format.dwRBitMask;bi.masks[1]=native_format.dwGBitMask;bi.masks[2]=native_format.dwBBitMask;''')
s=s.replace('CreateDIBSection(dc,&bi,','CreateDIBSection(dc,(BITMAPINFO*)&bi,')
s=s.replace('screen[i]=bits[i]&0xffffffUL;', 'screen[i]=(native_format.dwRGBBitCount==32?((DWORD*)bits)[i]:((WORD*)bits)[i])&native_mask;')
at=s.index('static int texture_acceptable(')
extra='''static int native_bytes(IDirectDrawSurface7 *surface,int post){
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
'''
s=s[:at]+extra+s[at:]
s=s.replace('IDirectDrawSurface7 *primary=0;', 'IDirectDrawSurface7 *primary=0,*bridge=0;')
s=s.replace('||s.ddpfPixelFormat.dwRGBBitCount!=32','')
s=s.replace('if(pf.dwFlags!=DDPF_RGB||pf.dwRGBBitCount!=32||pf.dwRBitMask!=0xff0000||pf.dwGBitMask!=0xff00||pf.dwBBitMask!=255||pf.dwRGBAlphaBitMask)goto done;', '''if(pf.dwFlags!=DDPF_RGB||pf.dwRGBAlphaBitMask||!((pf.dwRGBBitCount==32&&pf.dwRBitMask==0xff0000&&pf.dwGBitMask==0xff00&&pf.dwBBitMask==255)||(pf.dwRGBBitCount==16&&pf.dwBBitMask==31&&((pf.dwRBitMask==0xf800&&pf.dwGBitMask==0x7e0)||(pf.dwRBitMask==0x7c00&&pf.dwGBitMask==0x3e0)))))goto done;
 native_format=pf;native_mask=pf.dwRBitMask|pf.dwGBitMask|pf.dwBBitMask;
 zero(&s,sizeof(s));s.dwSize=sizeof(s);s.dwFlags=DDSD_CAPS|DDSD_WIDTH|DDSD_HEIGHT|DDSD_PIXELFORMAT;s.dwWidth=s.dwHeight=64;s.ddsCaps.dwCaps=DDSCAPS_SYSTEMMEMORY|DDSCAPS_OFFSCREENPLAIN;s.ddpfPixelFormat=pf;
 HR("p.bridge.create",IDirectDraw7_CreateSurface(dd,&s,&bridge,0));''')
s=s.replace('if(!capture(0,p)||!clip(cl,p)||!transformed(dev,target,textures))goto done;', 'if(!capture(0,p)||!clip(cl,p)||!transformed(dev,target,textures)||!native_bytes(bridge,0))goto done;')
s=s.replace('Blt(primary,&to,target,&from','Blt(primary,&to,bridge,&from')
s=s.replace('if(!capture(1,p))goto done;', 'if(!capture(1,p)||!native_bytes(bridge,1))goto done;')
s=s.replace(' if(primary){refs=', ' if(bridge){refs=IDirectDrawSurface7_Release(bridge);number("p.release.bridge",refs);clean&=refs==0;}\n if(primary){refs=')
s=s.replace('xwn-scene-present-1','xwn-scene-present-2')
s=s.replace(' if(windows()){w=panel;}', ''' native_files[0]=fresh(prefix,"-native-before.bin");native_files[1]=fresh(prefix,"-native-after.bin");
 if(native_files[0]==INVALID_HANDLE_VALUE||native_files[1]==INVALID_HANDLE_VALUE)goto done;
 if(windows()){w=panel;}''')
s=s.replace(' if(post_file!=INVALID_HANDLE_VALUE', ' for(i=0;i<2;i++)if(native_files[i]!=INVALID_HANDLE_VALUE&&!CloseHandle(native_files[i]))io_error=1;\n if(post_file!=INVALID_HANDLE_VALUE')
p.write_text(s,encoding='utf-8',newline='\n')
(K/'source001.json').write_text(json.dumps(dict(previous_sha256=prior,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
