
list(APPEND SOURCE
    enable.c
    palette.c
    pointer.c
    screen.c
    surface.c
    shadow.c
    ownership.c
    profile_math.h
    text_bounds.h
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

option(XWN_BODY_PROFILE "Diagnostic elapsed engine/upload bodies" OFF)
if(XWN_BODY_PROFILE)
 target_compile_definitions(xwnown PRIVATE XWN_BODY_PROFILE=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_BODY_PROFILE=0)
endif()

option(XWN_TEXT_BOUNDS "Conservative string/opaque text upload bounds" OFF)
if(XWN_TEXT_BOUNDS)
 target_compile_definitions(xwnown PRIVATE XWN_TEXT_BOUNDS=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_TEXT_BOUNDS=0)
endif()

option(XWN_UPLOAD_ACCOUNTING "Diagnostic completed upload bytes by DDI" OFF)
if(XWN_UPLOAD_ACCOUNTING)
 target_compile_definitions(xwnown PRIVATE XWN_UPLOAD_ACCOUNTING=1)
else()
 target_compile_definitions(xwnown PRIVATE XWN_UPLOAD_ACCOUNTING=0)
endif()
