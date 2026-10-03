#!/usr/bin/env bash
set -euo pipefail
root=/home/paul/xbox-windows-native
mode=${1:-diagnostic}
preflight=OFF
io_preflight=OFF
targets='freeldr rosload'
flavor=Debug
case "$mode" in diagnostic) preflight=ON;; loader) :;; io) io_preflight=ON;; hal-audit) targets='halxbox xboxbvid';; hal-free-audit) targets='halxbox xboxbvid'; flavor=Release;; *) echo 'Use diagnostic, loader, io, hal-audit or hal-free-audit' >&2; exit 2;; esac
if [[ ${XWN_BUILD_LEASE:-} != held ]]; then
    echo 'Invoke through Invoke-Build.ps1 to hold the shared build resource lease.' >&2
    exit 2
fi
rosbe="$root/toolchains/RosBE-2.2.1"
test -x "$rosbe/RosBE.sh" || { echo 'Run the toolchain bootstrap first.' >&2; exit 2; }
source_tree="$root/sources/reactos"
test "$(git -C "$source_tree" rev-parse HEAD)" = afc0127e8f937ab68503d715d948844973756aa1
build="$root/build/$mode"
mkdir -p "$build"
# Run RosBE's own environment wrapper, as used by the pinned source's CI.
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=%s -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NATIVE_PREFLIGHT=%s -DXBOX_NATIVE_IO_PREFLIGHT=%s && cmake --build %s --target %s -- -j4\n' \
    "$source_tree" "$build" "$source_tree" "$flavor" "$preflight" "$io_preflight" "$build" "$targets" | "$rosbe/RosBE.sh" "$source_tree" 0 i386
