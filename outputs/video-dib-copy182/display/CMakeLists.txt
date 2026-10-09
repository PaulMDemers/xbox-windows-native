
list(APPEND SOURCE
    enable.c
    palette.c
    pointer.c
    screen.c
    surface.c
    shadow.c
    ownership.c
    dib_plan.h
    framebuf.h)

add_library(xwnown MODULE
    ${SOURCE}
    framebuf.rc)

set_module_type(xwnown kerneldll ENTRYPOINT DrvEnableDriver 12)
add_pch(xwnown framebuf.h SOURCE)
target_link_libraries(xwnown libcntpr)
add_importlibs(xwnown win32k)
add_dependencies(xwnown psdk)
add_cd_file(TARGET xwnown DESTINATION reactos/system32 FOR all)

option(XWN_DIB_FASTPATH "Bounded standard32bpp DIB to RAM-primary copy" OFF)
if(XWN_DIB_FASTPATH)
 target_compile_definitions(xwnown PRIVATE XWN_DIB_FASTPATH=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_DIB_FASTPATH=0)
endif()
