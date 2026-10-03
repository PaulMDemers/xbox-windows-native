#!/usr/bin/env bash
set -euo pipefail
kit=$(cd -- "$(dirname -- "$0")" && pwd)
workspace=$(cd "$kit/../.." && pwd)
task_root=/home/paul/xbox-windows-native
mkdir -p "$task_root/sources"
stage_source() {
    local name=$1 origin=$2 revision=$3 reference=$4
    local destination="$task_root/sources/$name"
    if [[ ! -d "$destination" ]]; then
        git clone --no-hardlinks --no-checkout "$reference" "$destination"
        git -C "$destination" remote set-url origin "$origin"
        git -C "$destination" checkout -b codex/native-windows-preflight "$revision"
    fi
    test "$(git -C "$destination" rev-parse HEAD)" = "$revision"
    test ! -e "$destination/.git/objects/info/alternates"
}
stage_source reactos https://github.com/DistroHopper39B/reactos.git afc0127e8f937ab68503d715d948844973756aa1 "$workspace/work/reference-sources/reactos-ntatv"
stage_source cromwell https://github.com/PaulMDemers/cromwell.git 9fc54d0c7cbed7bc3c70373642d833684853011f /home/paul/ogxbox-linux/sources/cromwell-xboxdev
apply_once() {
    local repo=$1 patch=$2
    if git -C "$repo" apply --reverse --check "$patch" 2>/dev/null; then
        printf 'Already applied: %s\n' "$patch"
    else
        git -C "$repo" apply --check "$patch"
        git -C "$repo" apply "$patch"
    fi
}
# Cumulative patch replaces 0001; do not apply both to a fresh source tree.
apply_once "$task_root/sources/reactos" "$kit/patches/0005-native-io-cumulative.patch"
apply_once "$task_root/sources/cromwell" "$kit/patches/0002-Reserve-full-legacy-heap.patch"
git -C "$task_root/sources/reactos" diff --check
git -C "$task_root/sources/cromwell" diff --check
printf 'Private source branches prepared; no build was run.\n'
