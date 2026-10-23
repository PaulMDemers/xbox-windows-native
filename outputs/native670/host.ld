/* Isolated function fixture only, never a bootable image. */
ENTRY(terminal670)
SECTIONS {
 . = 0x02600000;
 .text : { *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 . = 0x02680000;
 _bss = .;
 .bss : { *(.bss*) *(COMMON) }
 BSS_END = .;
 /DISCARD/ : { *(.eh_frame*) *(.comment*) *(.note*) }
}
