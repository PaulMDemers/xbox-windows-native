def integrate(src,kit):
 root=src/'win32ss/drivers/displays/framebuf'
 for n in ['bandwidth.h','bandwidth.c']:(root/n).write_bytes((kit/n).read_bytes())
 p=root/'enable.c';s=p.read_text();assert s.count('0x5857443c')==1;p.write_text(s.replace('0x5857443c','0x5857443d'))
 p=root/'ownership.c';s=p.read_text();assert s.count('out[1]=361;')==1;p.write_text(s.replace('out[1]=361;','out[1]=364;'))
