"""Deterministic BMP inputs for Paint save tests; no external image assets."""
import hashlib,json,pathlib,struct
k=pathlib.Path(__file__).resolve().parent

def bitmap(width,height,pattern):
    pixels=bytearray(b'\xff'*(width*height*3))
    def dot(x,y,color):
        for dy in range(-2,3):
            for dx in range(-2,3):
                if 0<=x+dx<width and 0<=y+dy<height:
                    p=((y+dy)*width+x+dx)*3;pixels[p:p+3]=bytes(color)
    if pattern=='scribble':
        points=[(28,145),(115,48),(83,230),(221,82),(182,240),(345,49),(299,223),(460,99)]
        for i,((x0,y0),(x1,y1)) in enumerate(zip(points,points[1:])):
            n=max(abs(x1-x0),abs(y1-y0))
            for t in range(n+1):dot(x0+(x1-x0)*t//n,y0+(y1-y0)*t//n,(20,20,20) if i<4 else (180,40,10))
    elif pattern=='coordinates':
        for y in range(height):
            for x in range(width):
                p=(y*width+x)*3;pixels[p:p+3]=bytes((x&255,y&255,(x^y)&255))
    stride=(width*3+3)&~3
    body=b''.join(pixels[y*width*3:(y+1)*width*3]+bytes(stride-width*3) for y in reversed(range(height)))
    return struct.pack('<2sIHHI',b'BM',54+len(body),0,0,54)+struct.pack('<IiiHHIIiiII',40,width,height,1,24,0,len(body),3780,3780,0,0)+body

if __name__=='__main__':
    folder=k/'artifacts/images';folder.mkdir(parents=True,exist_ok=True);rows=[]
    for name,w,h,pattern in [('scribble.bmp',512,288,'scribble'),('blank.bmp',512,288,'blank'),('coords.bmp',512,288,'coordinates'),('oddwidth.bmp',513,288,'coordinates')]:
        data=bitmap(w,h,pattern);(folder/name).write_bytes(data)
        assert len(data)==54+((w*3+3)&~3)*h and struct.unpack_from('<I',data,2)[0]==len(data)
        rows.append(dict(name=name,width=w,height=h,bits_per_pixel=24,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    (k/'images.json').write_text(json.dumps(dict(scope=__doc__,files=rows),indent=2)+'\n')
