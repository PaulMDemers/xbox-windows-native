
list(APPEND SOURCE
    enable.c
    palette.c
    pointer.c
    screen.c
    surface.c
    framebuf.h)

add_library(xwndir MODULE
    ${SOURCE}
    framebuf.rc)

set_module_type(xwndir kerneldll ENTRYPOINT DrvEnableDriver 12)
add_pch(xwndir framebuf.h SOURCE)
target_link_libraries(xwndir libcntpr)
add_importlibs(xwndir win32k)
add_dependencies(xwndir psdk)
add_cd_file(TARGET xwndir DESTINATION reactos/system32 FOR all)
