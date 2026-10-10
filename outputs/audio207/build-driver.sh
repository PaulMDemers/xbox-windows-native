#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
owned=/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/work
src="$owned/reactos001"
build="$owned/build001"
export TMPDIR="$owned/tmp"
mkdir -p "$TMPDIR" "$kit/artifacts/build001"
test "$(git -C "$src" rev-parse HEAD)" = afc0127e8f937ab68503d715d948844973756aa1
test "$(git -C "$src" write-tree)" = 5c302cf16ce08e7f2748be580e3d2e60d7d2441b
test ! -e "$kit/artifacts/build001/ac97xnt5.sys"
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Release -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NT5_HAL=ON -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=OFF && cmake --build %s --target ac97xnt5 -- -j4\n' "$src" "$build" "$src" "$build" | /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/RosBE.sh "$src" 0 i386
test -e "$build/drivers/wdm/audio/drivers/ac97/ac97xnt5.sys"
cp "$build/drivers/wdm/audio/drivers/ac97/ac97xnt5.sys" "$kit/artifacts/build001/"
sha256sum "$kit/artifacts/build001/ac97xnt5.sys"
