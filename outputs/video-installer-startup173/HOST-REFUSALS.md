The first inputs-freeze invocation used Windows Python, but inherited common.py
depends on the WSL-only FATX tooling import path. It failed ModuleNotFoundError
before creating frozen-inputs.json. The following preflight invocation refused
that missing freeze before reading or writing any guest fixture. No sources,
binaries or fixture changed and no guest launched. These host invocations are
retained separately from runtime results; subsequent freeze/preflight use WSL.

The next WSL preflight checked the frozen inputs and protected files, then could
not load owned libhivex.so.0 without the offline-toolchain LD_LIBRARY_PATH. No
preflight.json completion record or guest launch exists from that invocation.
Its cold before-system bytes are preserved separately with hashes. The following
read-only preflight uses the existing verified library directory; no frozen source
or fixture changes, completed stage rerun or gate waiver.
