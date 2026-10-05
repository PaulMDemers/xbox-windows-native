#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
src="$root/sources/reactos-extended"
build="$root/build/vfat-nt5-deferred-buffer"
kit=/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-fatx-forensics
case ${1:-rename} in
  rename) manifest=0080; artifact=xwnfatx-rename-integration.sys ;;
  cleanup) manifest=0081; artifact=xwnfatx-delete-cache.sys ;;
  trace) manifest=0082; artifact=xwnfatx-write-trace.sys ;;
  deleted-write) manifest=0083; artifact=xwnfatx-deleted-write.sys ;;
  rename-trace) manifest=0084; artifact=xwnfatx-rename-trace.sys ;;
  rename-filter) manifest=0085; artifact=xwnfatx-rename-filter.sys ;;
  unlinked) manifest=0086; artifact=xwnfatx-unlinked.sys ;;
  lifetime-trace) manifest=0087; artifact=xwnfatx-lifetime-trace.sys ;;
  retired-write) manifest=0088; artifact=xwnfatx-retired-write.sys ;;
  *) exit 2 ;;
esac
tree=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["result_tree"])' "$kit/patch-check-$manifest.json")
git -C "$src" diff --exit-code "$tree" -- >/dev/null
printf 'cmake --build %s --target vfatfs -- -j4\n' "$build" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$src" 0 i386
cp "$build/drivers/filesystems/vfatfs/vfatfs.sys" "$kit/artifacts/$artifact"
