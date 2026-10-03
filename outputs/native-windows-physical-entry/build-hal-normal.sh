#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || { echo 'Build lease required'; exit 2; }
root=/home/paul/xbox-windows-native
source_tree="$root/sources/reactos"
build="$root/build/physical-entry-hal-normal"
test "$(git -C "$source_tree" rev-parse HEAD)" = afc0127e8f937ab68503d715d948844973756aa1
mkdir -p "$build"
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Release -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NT5_HAL=ON -DXBOX_NT5_ENTRY_PREFLIGHT=OFF -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=OFF && cmake --build %s --target halxboxnt5 xboxbvid -- -j4\n' \
  "$source_tree" "$build" "$source_tree" "$build" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$source_tree" 0 i386
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$kit/artifacts-normal"
cp "$build/hal/halx86/xboxnt5/halxboxnt5.dll" "$kit/artifacts-normal/halxboxnt5.dll"
cp "$build/drivers/base/bootvid/xboxbvid.dll" "$kit/artifacts-normal/xboxbvid.dll"
