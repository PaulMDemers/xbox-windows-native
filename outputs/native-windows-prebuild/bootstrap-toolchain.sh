#!/usr/bin/env bash
set -euo pipefail
kit=$(cd -- "$(dirname -- "$0")" && pwd)
source "$kit/host-env.sh"
if [[ ${XWN_BUILD_LEASE:-} != held ]]; then
    echo 'Invoke through Invoke-Build.ps1 to hold the shared build resource lease.' >&2
    exit 2
fi
destination="$XWN_ROOT/toolchains/RosBE-2.2.1"
test ! -e "$destination" || { echo 'Toolchain destination already exists; inspect it before retrying.' >&2; exit 2; }
for tool in as bzip2 find gcc g++ grep m4 makeinfo python tar make pkg-config; do command -v "$tool" >/dev/null; done
pkg-config --exists zlib
python3 "$kit/patch-ninja-python.py"
mkdir -p "$XWN_ROOT/toolchains"
# Limit CPU affinity because this upstream builder selects its own parallelism.
cpus=$(python3 -c 'import os; print(",".join(map(str, sorted(os.sched_getaffinity(0))[:4])))')
# Upstream asks non-root users to confirm even with a private writable prefix.
printf 'yes\n' | taskset -c "$cpus" bash "$XWN_ROOT/toolchain-source/RosBE-Unix-2.2.1/RosBE-Builder.sh" "$destination"
