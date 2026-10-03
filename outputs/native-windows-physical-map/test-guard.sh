#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
src="$root/sources/reactos"
build="$root/build/map-probe-forbidden-parent"
kit=/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-map
if printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Debug -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=ON -DXBOX_NATIVE_FATX_IO_PREFLIGHT=OFF -DXBOX_NATIVE_FATX_NT5_PREFLIGHT=ON -DXBOX_NATIVE_FATX_PAGING_PREFLIGHT=ON -DXBOX_NATIVE_FATX_ENTRY_PREFLIGHT=ON -DXBOX_NATIVE_FATX_PHASE0_PREFLIGHT=ON -DXBOX_NATIVE_FATX_HALBASE_PREFLIGHT=ON -DXBOX_NATIVE_FATX_TIMER_PREFLIGHT=ON -DXBOX_NATIVE_FATX_CLOCK_PREFLIGHT=ON -DXBOX_NATIVE_FATX_HOOKS_PREFLIGHT=ON -DXBOX_NATIVE_FATX_BIOS_PREFLIGHT=ON -DXBOX_NATIVE_FATX_MM_PREFLIGHT=ON -DXBOX_NATIVE_FATX_MI_PREFLIGHT=OFF -DXBOX_NATIVE_FATX_MAP_PREFLIGHT=ON -DXBOX_NATIVE_VOLUME_PREFLIGHT=OFF -DXBOX_NATIVE_NT5_HANDOFF=ON -DXBOX_NATIVE_NT5_ENTER=OFF -DXBOX_NATIVE_NT5_AUTORUN=OFF\n' "$src" "$build" "$src" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$src" 0 i386 > "$kit/build-logs/forbidden-entry.log" 2>&1; then
  echo "Configuration unexpectedly succeeded"; exit 1
fi
grep -q "MAP probe requires MI preflight" "$kit/build-logs/forbidden-entry.log"
