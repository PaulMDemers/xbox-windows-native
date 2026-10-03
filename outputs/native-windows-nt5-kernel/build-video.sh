#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || { echo 'Build lease required'; exit 2; }
root=/home/paul/xbox-windows-native
source_tree="$root/sources/reactos"
build="$root/build/hal-nt5"
test "$(git -C "$source_tree" rev-parse HEAD)" = afc0127e8f937ab68503d715d948844973756aa1
mkdir -p "$build"
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Release -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NT5_HAL=ON -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=OFF && cmake --build %s --target xboxvnt5 -- -j4\n' \
  "$source_tree" "$build" "$source_tree" "$build" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$source_tree" 0 i386
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$kit/artifacts"
cp "$build/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.sys" "$kit/artifacts/xboxvnt5.sys"
