
list(APPEND SOURCE
    adapter.cpp
    common.cpp
    mintopo.cpp
    prophnd.cpp
    miniport.cpp
    stream.cpp
    stream2.cpp
    rtminiport.cpp
    rtstream.cpp
    wavepciminiport.cpp
    wavepcistream.cpp
    wavecyclicminiport.cpp
    wavecyclicstream.cpp)

add_library(ac97 MODULE
    ${SOURCE}
    ac97.rc)

target_link_libraries(ac97 stdunk libcntpr uuid)
set_module_type(ac97 wdmdriver)
add_importlibs(ac97 portcls hal ntoskrnl)

if(CMAKE_C_COMPILER_ID STREQUAL "GNU" OR CMAKE_C_COMPILER_ID STREQUAL "Clang")
    target_compile_options(ac97 PRIVATE -Wno-write-strings -Wno-switch)
endif()

add_cd_file(TARGET ac97 DESTINATION reactos/system32/drivers FOR all)
add_driver_inf(ac97 ac97.inf)

# Experimental Xbox ACI MMIO path. Codec probing is still the PC model;
# this target is for isolated emulator bring-up, not physical-console audio.
if(XBOX_NT5_HAL)
    add_library(ac97xnt5 MODULE ${SOURCE} ac97.rc)
    target_compile_definitions(ac97xnt5 PRIVATE XBOX_NT5_AC97_MMIO=1)
    target_link_libraries(ac97xnt5 stdunk libcntpr uuid)
    set_module_type(ac97xnt5 wdmdriver)
    add_importlibs(ac97xnt5 portcls hal ntoskrnl)
    if(CMAKE_C_COMPILER_ID STREQUAL "GNU" OR CMAKE_C_COMPILER_ID STREQUAL "Clang")
        target_compile_options(ac97xnt5 PRIVATE -Wno-write-strings -Wno-switch)
    endif()
endif()
