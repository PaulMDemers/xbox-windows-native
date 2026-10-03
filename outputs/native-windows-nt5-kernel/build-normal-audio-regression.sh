#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
src="$root/sources/reactos"
test "$(git -C "$src" rev-parse HEAD)" = afc0127e8f937ab68503d715d948844973756aa1
build="$root/build/normal-nt5-regression"
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Debug -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=OFF -DXBOX_NATIVE_VOLUME_PREFLIGHT=OFF -DXBOX_NATIVE_NT5_HANDOFF=OFF -DXBOX_NATIVE_NT5_ENTER=OFF -DXBOX_NATIVE_NT5_AUTORUN=OFF -DXBOX_NT5_HAL=OFF && cmake --build %s --target freeldr rosload halxbox xboxbvid nvnet ac97 -- -j4\n' "$src" "$build" "$src" "$build" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$src" 0 i386
