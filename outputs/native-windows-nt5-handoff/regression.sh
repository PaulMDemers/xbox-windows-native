#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
root=/home/paul/xbox-windows-native
test "$(git -C "$root/sources/reactos" rev-parse HEAD)" = afc0127e8f937ab68503d715d948844973756aa1
printf 'cmake --build %s/build/hal-nt5 --target halxbox xboxbvid -- -j4\n' "$root" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$root/sources/reactos" 0 i386
printf 'cmake --build %s/build/loader --target freeldr rosload -- -j4\n' "$root" | "$root/toolchains/RosBE-2.2.1/RosBE.sh" "$root/sources/reactos" 0 i386
grep '^XBOX_NATIVE_.*:BOOL=' "$root/build/loader/CMakeCache.txt"
if grep -q '^XBOX_NATIVE_.*:BOOL=ON' "$root/build/loader/CMakeCache.txt"; then
    echo 'Normal loader unexpectedly contains a diagnostic option' >&2
    exit 1
fi
