#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
src=/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/work/reactos001
target="$kit/artifacts/corresponding-source001"
test ! -e "$target"
mkdir "$target"
test "$(git -C "$src" write-tree)" = 5c302cf16ce08e7f2748be580e3d2e60d7d2441b
git -C "$src" archive --format=tar.gz --prefix=reactos0016/ --output="$target/reactos0016.tar.gz" 5c302cf16ce08e7f2748be580e3d2e60d7d2441b
cp "$kit/0210-waveonly-cumulative.patch" "$target/"
sha256sum "$target/reactos0016.tar.gz" "$target/0210-waveonly-cumulative.patch"
