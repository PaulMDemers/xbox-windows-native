#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
owned=/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/work
src="$owned/reactos001"
build="$owned/build001"
export TMPDIR="$owned/tmp"
test ! -e "$kit/artifacts/build002"
mkdir "$kit/artifacts/build002"
test "$(git -C "$src" write-tree)" = 5c302cf16ce08e7f2748be580e3d2e60d7d2441b
printf 'cmake --build %s --target ac97xnt5 ac97 -- -j4\n' "$build" | /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/RosBE.sh "$src" 0 i386
for driver in ac97xnt5 ac97; do
    cp "$build/drivers/wdm/audio/drivers/ac97/$driver.sys" "$kit/artifacts/build002/"
    sha256sum "$kit/artifacts/build002/$driver.sys"
done
python3 "$kit/test-lifecycle003.py" "$src"
python3 "$kit/test-fixed-codec002.py" "$src"
