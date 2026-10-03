#!/usr/bin/env bash
set -euo pipefail
root=/home/paul/xbox-windows-native
[[ ${XWN_BUILD_LEASE:-} == held ]] || { echo 'Use Invoke-Build.ps1' >&2; exit 2; }
source_tree="$root/sources/cromwell"
build="$root/build/cromwell"
test ! -e "$build" || { echo 'Use a fresh Cromwell build directory or inspect the existing one first.' >&2; exit 2; }
test "$(git -C "$source_tree" rev-parse HEAD)" = 9fc54d0c7cbed7bc3c70373642d833684853011f
mkdir -p "$build"
git -C "$source_tree" archive HEAD | tar -x -C "$build"
git -C "$source_tree" diff --binary HEAD | (cd "$build" && patch -p1)
mkdir -p "$build/.host-tools"
ln -s /usr/bin/gcc-12 "$build/.host-tools/gcc"
# This upstream 'all' target includes clean; do not run it with parallel make.
# This upstream flag invokes generic CD OS detection; our disc has only FreeLoader.
# It does not boot or include a Linux guest and avoids an interactive icon menu.
PATH="$build/.host-tools:$PATH" make -C "$build" all CC=/usr/bin/gcc-12 GITREV=9fc54d0-xwn EXTRA_CROM_CFLAGS=-DXBOX_LINUX_AUTOBOOT_CD
sha256sum "$build/image/cromwell_1024.bin" "$build/xbe/xromwell.xbe"
