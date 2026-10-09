
list(APPEND SOURCE
    enable.c
    palette.c
    pointer.c
    screen.c
    surface.c
    shadow.c
    ownership.c
    row_store.h
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

option(XWN_UC_STORES "Bounded aligned scalar32bit scanout stores" OFF)
if(XWN_UC_STORES)
 target_compile_definitions(xwnown PRIVATE XWN_UC_STORES=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_UC_STORES=0)
endif()
