/* MIT. Actual NT5 no-output-pointer creation, including unsupported mask layout. */
static BOOL nullcontrol607(void){
 HMODULE g=GetModuleHandleA("GDI32.DLL");union {FARPROC generic;DIB601 dib;} da;
 BITMAPINFO rgb;struct {BITMAPINFOHEADER h;DWORD masks[3];} masked;
 DIBSECTION ds;HBITMAP bitmap=0;BOOL ok=FALSE;int n;
 da.generic=GetProcAddress(g,"CreateDIBSection");if(!da.dib)return FALSE;
 zero601(&rgb,sizeof(rgb));rgb.bmiHeader.biSize=40;rgb.bmiHeader.biWidth=8;rgb.bmiHeader.biHeight=-8;
 rgb.bmiHeader.biPlanes=1;rgb.bmiHeader.biBitCount=32;
 bitmap=da.dib(0,&rgb,0,0,0,0);if(!bitmap)goto done;
 zero601(&ds,sizeof(ds));n=GetObjectA(bitmap,sizeof(ds),&ds);
 if(n!=sizeof(ds)||ds.dsBm.bmWidth!=8||ds.dsBm.bmHeight!=8||ds.dsBm.bmBitsPixel!=32)goto done;
 if(!DeleteObject(bitmap))goto done;
 bitmap=0;
 zero601(&masked,sizeof(masked));masked.h.biSize=40;masked.h.biWidth=8;masked.h.biHeight=8;masked.h.biPlanes=1;masked.h.biBitCount=16;masked.h.biCompression=BI_BITFIELDS;
 masked.masks[0]=0xf800;masked.masks[1]=0x07e0;masked.masks[2]=0x001f;
 bitmap=da.dib(0,(const BITMAPINFO*)&masked,0,0,0,0);if(!bitmap)goto done;
 zero601(&ds,sizeof(ds));n=GetObjectA(bitmap,sizeof(ds),&ds);
 if(n!=sizeof(ds)||ds.dsBm.bmWidth!=8||ds.dsBm.bmHeight!=8||ds.dsBm.bmBitsPixel!=16)goto done;
 if(!DeleteObject(bitmap))goto done;
 bitmap=0;rgb.bmiHeader.biSize=0;
 bitmap=da.dib(0,&rgb,0,0,0,0);if(bitmap)goto done;
 ok=TRUE;
done:
 if(bitmap)DeleteObject(bitmap);
 record(ok?"NULL607 PASS: RGB and masks objects, invalid header, no output pointers\r\n":"NULL607 FAIL\r\n");return ok;
}
