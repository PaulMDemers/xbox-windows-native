


list(APPEND SOURCE
    backoff.c
    debug.h
    init.c
    interrupt.c
    nic.c
    nic.h
    nvnet.c
    nvnet.h
    phy.c
    phyreg.h
    requests.c
    send.c)

add_library(nvnet MODULE ${SOURCE} nvnet.rc)
target_compile_definitions(nvnet PRIVATE NDIS51_MINIPORT NDIS_MINIPORT_DRIVER)
target_link_libraries(nvnet memcmp)
add_pch(nvnet nvnet.h SOURCE)
set_module_type(nvnet kernelmodedriver)
add_importlibs(nvnet ndis ntoskrnl hal)
add_cd_file(TARGET nvnet DESTINATION reactos/system32/drivers FOR all)
add_driver_inf(nvnet netnv.inf)

if(XBOX_NT5_HAL)
    add_library(nvnetnt5 MODULE ${SOURCE} nt5.c nvnet.rc)
    target_compile_definitions(nvnetnt5 PRIVATE NDIS50_MINIPORT NDIS_MINIPORT_DRIVER XBOX_NVNET_NT5=1)
    target_link_libraries(nvnetnt5 memcmp)
    set_module_type(nvnetnt5 kernelmodedriver)
    add_importlibs(nvnetnt5 ndis ntoskrnl hal)
endif()
