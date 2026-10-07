#!/bin/sh
set -eu
cd "$(dirname "$0")"
test ! -e artifacts/dispatch.bin
mkdir -p artifacts
as --32 -o artifacts/dispatch.o dispatch.S
ld -m elf_i386 -Ttext=0x15800 --defsym extended_dispatch=0x258c --defsym legacy_dispatch=0x27fe -e dispatch -o artifacts/dispatch.elf artifacts/dispatch.o
objcopy -O binary -j .text artifacts/dispatch.elf artifacts/dispatch.bin
sha256sum /usr/bin/as /usr/bin/ld /usr/bin/objcopy > artifacts/toolchain.sha256
as --version > artifacts/assembler-version.txt
ld --version > artifacts/linker-version.txt
