def integrate(src,kit):
 root=src/'win32ss/drivers/displays/framebuf'
 assert (root/'capture.h').read_bytes()==(kit/'capture.h').read_bytes()
 def replace(n,a,b):
  p=root/n;s=p.read_text();assert s.count(a)==1,(n,a);p.write_text(s.replace(a,b))
 (root/'memory_warm.c').write_bytes((kit/'memory_warm.c').read_bytes())
 replace('CMakeLists.txt','    memory_state.c','    memory_state.c\n    memory_warm.c')
 replace('framebuf.h','ULONG XwnMemoryState354(SURFOBJ *,ULONG,PVOID);','ULONG XwnMemoryState354(SURFOBJ *,ULONG,PVOID);\nULONG XwnMemoryState357(SURFOBJ *,ULONG,PVOID);')
 replace('enable.c','   if (Escape == 0x5857443a)','   if (Escape == 0x5857443b) return XwnMemoryState357(Surface,OutBytes,Out);\n   if (Escape == 0x5857443a)')
