#!/usr/bin/env bash
set -euo pipefail
[[ ${XWN_BUILD_LEASE:-} == held ]] || exit 2
kit=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd "$kit/../.." && pwd)
owned=/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/work
mkdir -p "$owned"
test ! -e "$owned/reactos001"
git clone --no-hardlinks --no-checkout /home/paul/xbox-windows-native/sources/reactos "$owned/reactos001"
git -C "$owned/reactos001" checkout --detach afc0127e8f937ab68503d715d948844973756aa1
python3 "$repo/tools/apply-series.py" --source "$owned/reactos001" --manifest "$repo/outputs/native-windows-nt5-kernel/patch-check-0016.json"
