#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python3 "$kit/prepare-volume-probe.py"
src="$root/sources/reactos"
test "$(git -C "$src" rev-parse HEAD)" = afc0127e8f937ab68503d715d948844973756aa1
build="$root/build/volume"
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Debug -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=ON -DXBOX_NATIVE_VOLUME_PREFLIGHT=ON && cmake --build %s --target freeldr rosload -- -j4\n' "$src" "$build" "$src" "$build" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$src" 0 i386
cp "$build/boot/freeldr/freeldr/freeldr.sys" "$kit/artifacts/freeldr.sys"
cp "$build/boot/freeldr/freeldr/rosload.exe" "$kit/artifacts/rosload.exe"
