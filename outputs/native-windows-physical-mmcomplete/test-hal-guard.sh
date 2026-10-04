#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
src="$root/sources/reactos"
kit=/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-mmcomplete
build="$root/build/mmcomplete-hal-forbidden-parent"
if printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Release -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NT5_HAL=ON -DXBOX_NT5_PROCESSINIT_PREFLIGHT=OFF -DXBOX_NT5_MMCOMPLETE_PREFLIGHT=ON\n' "$src" "$build" "$src" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$src" 0 i386 > "$kit/build-logs/forbidden-hal.log" 2>&1; then
    echo 'HAL configuration unexpectedly succeeded'; exit 1
fi
grep -q 'MMCOMPLETE probe requires PROCESSINIT preflight' "$kit/build-logs/forbidden-hal.log"
