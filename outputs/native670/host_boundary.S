/* HOST TEST BOUNDARIES ONLY. UD2 prevents accidental standalone execution.
 * The isolated CPU harness models these PCI helper ABIs explicitly. */
.text
.global PciReadDword,PciReadWord,PciWriteWord
PciReadDword: ud2
PciReadWord: ud2
PciWriteWord: ud2
.bss
.balign 4
.global xbox_ram
xbox_ram: .space 4
.section .note.GNU-stack,"",@progbits
