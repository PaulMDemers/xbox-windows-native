#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
printf 'cmake --build %s/build/hal-nt5 --target halxbox xboxbvid -- -j4\n' "$root" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$root/sources/reactos" 0 i386
