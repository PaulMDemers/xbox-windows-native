#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
src="$root/sources/reactos-extended"
kit=/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f
build="$root/build/physical-f-loader"
printf 'cmake -S %s -B %s -G Ninja -DCMAKE_TOOLCHAIN_FILE=%s/toolchain-gcc.cmake -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Release -DDBG=OFF -DKDBG=OFF -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NT5_VIDEO_ADAPTER_DIAGNOSTIC=OFF -DXBOX_NT5_VIDEO_ENTRY_DIAGNOSTIC=OFF -DXBOX_NT5_VIDEO_TRACE=OFF -DXBOX_NT5_VIDEO_PNP_DIAGNOSTIC=OFF -DXBOX_NT5_VIDEO_DIAGNOSTIC=OFF -DXBOX_NT5_HAL=ON -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=ON -DXBOX_NATIVE_EXTENDED_READ_PREFLIGHT=OFF -DXBOX_NATIVE_EXTENDED_NT5_BOOT=ON -DXBOX_NATIVE_FATX_F_BOOT=ON -DXBOX_NATIVE_VOLUME_PREFLIGHT=OFF -DXBOX_NATIVE_NT5_HANDOFF=ON -DXBOX_NATIVE_NT5_ENTER=ON -DXBOX_NATIVE_NT5_AUTORUN=ON && cmake --build %s --target xboxvnt5 -- -j4\n' "$src" "$build" "$src" "$build" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$src" 0 i386
cp "$build/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.sys" "$kit/artifacts/xboxvnt5-normal.sys"
