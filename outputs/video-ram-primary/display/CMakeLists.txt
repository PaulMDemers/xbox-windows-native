
list(APPEND SOURCE
    enable.c
    palette.c
    pointer.c
    screen.c
    surface.c
    shadow.c
    framebuf.h)

add_library(xwnram MODULE
    ${SOURCE}
    framebuf.rc)

set_module_type(xwnram kerneldll ENTRYPOINT DrvEnableDriver 12)
add_pch(xwnram framebuf.h SOURCE)
target_link_libraries(xwnram libcntpr)
add_importlibs(xwnram win32k)
add_dependencies(xwnram psdk)
add_cd_file(TARGET xwnram DESTINATION reactos/system32 FOR all)
