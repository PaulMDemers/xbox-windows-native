def integrate(src,kit):
 root=src/'win32ss/drivers/displays/framebuf'
 def replace(n,a,b):
  p=root/n;s=p.read_text();assert s.count(a)==1,(n,a);p.write_text(s.replace(a,b))
 for n in ['capture.h','memory_state.c']:(root/n).write_bytes((kit/n).read_bytes())
 replace('CMakeLists.txt','    ownership.c','    ownership.c\n    memory_state.c')
 replace('CMakeLists.txt','target_link_libraries(xwnown libcntpr)','target_link_libraries(xwnown libcntpr pseh)')
 replace('CMakeLists.txt','add_importlibs(xwnown win32k)','add_importlibs(xwnown win32k ntoskrnl)')
 replace('framebuf.h','VOID XwnEligibleSnapshot(PPDEV,ULONG *);','VOID XwnEligibleSnapshot(PPDEV,ULONG *);\nULONG XwnMemoryState354(SURFOBJ *,ULONG,PVOID);')
 replace('enable.c','   if (Escape == 0x58574439 && OutBytes == sizeof(Data))','   if (Escape == 0x5857443a) return XwnMemoryState354(Surface,OutBytes,Out);\n   if (Escape == 0x58574439 && OutBytes == sizeof(Data))')
