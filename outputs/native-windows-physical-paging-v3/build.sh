#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
src="$root/sources/reactos"
build="$root/build/handoff"
kit=/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-paging-v3
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Debug -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=ON -DXBOX_NATIVE_FATX_IO_PREFLIGHT=OFF -DXBOX_NATIVE_FATX_NT5_PREFLIGHT=ON -DXBOX_NATIVE_FATX_PAGING_PREFLIGHT=ON -DXBOX_NATIVE_VOLUME_PREFLIGHT=OFF -DXBOX_NATIVE_NT5_HANDOFF=ON -DXBOX_NATIVE_NT5_ENTER=OFF -DXBOX_NATIVE_NT5_AUTORUN=OFF && cmake --build %s --target freeldr rosload -- -j4\n' "$src" "$build" "$src" "$build" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$src" 0 i386 > "$kit/build-logs/io.log" 2>&1
cp "$build/boot/freeldr/freeldr/freeldr.sys" "$kit/package/"
cp "$build/boot/freeldr/freeldr/rosload.exe" "$kit/package/"
