/* SPDX-License-Identifier: MIT */
ENTRY(_start)
SECTIONS {
  . = 0x100000;
  .multiboot : { *(.multiboot) }
  .text : { *(.text) }
  /DISCARD/ : { *(.note*) *(.comment*) }
}
