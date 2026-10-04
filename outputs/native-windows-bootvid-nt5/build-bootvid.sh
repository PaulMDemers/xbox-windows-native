#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
src="$root/sources/reactos"
build="$root/build/bootvid-nt5"
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Release -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NT5_HAL=ON && cmake --build %s --target xboxbvidnt5 -- -j4\n' "$src" "$build" "$src" "$build" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$src" 0 i386
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cp "$build/drivers/base/bootvid/xboxbvidnt5.dll" "$kit/artifacts/xboxbvid.dll"
