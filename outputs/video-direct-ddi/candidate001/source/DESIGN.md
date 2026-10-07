# Direct display DDI compatibility baseline

This candidate replaces only the desktop display DDI selected in a disposable
emulator SYSTEM hive. It has no shadow surface, GPU acceleration, cache change
or new mode. SharedUC0106 bootvid/miniport and the qualified emulator storage and
network stack remain fixed. The physical console is not accessed.

Build002 reconstructs tree3c664be8842518eac9dd18d92f6a3e2f78d36f73, using the
pinned RosBE toolchain and explicit prior0093/0106 flags. The ReactOS framebuf
source is GPL-2.0-or-later; retain its file notices. New module xwndir.dll keeps
Microsoft framebuf.dll intact. Both fixtures carry the same xwndir/probe bytes;
control selects framebuf, candidate selects xwndir. Only existing bound display
selection values change, with complete logical SYSTEM-hive comparison verifying
that all other nodes and values remain unchanged. The inherited emulator-only
QEMU null-device and01B0/01B4 unsupported-device policy stays explicit.

Changes to the source lead:

- Zero stack GDIINFO/DEVINFO before filling supported fields.
- Bound the number/size/returned bytes of mode records and respect DrvGetModes'
  caller buffer capacity.
- Restrict the initial prototype to positive-stride32-bit framebuffer geometry
  fitting the reserved4MiB mapping. Check the map response and unwind successful
  maps after later bitmap/association failure; do not map an already enabled PDEV.
- Delete/unmap only initialized handles, clearing the local lifecycle state.
  The existing provider retains its permanent physical mapping. These checks
  are not generic PnP, failed-unmap or concurrent disable qualification.
- Add a read-only identity escape. The probe requires its exact revision and
  geometry on the candidate, and unsupported response on the Microsoft control.
  No kernel pointers, arbitrary memory reads or write operations are exposed.

The initial build001 failed at git apply because the Windows-generated patch had
CRLF line endings. Its exact patch/source/build report remains in build001/source
and the WSL build directory. Build002 uses LF patch/source bytes. No compilation
or guest launch occurred in build001.

Host harness issues are also retained: an initial shell quoting command failed
before creating the test directory; host001 then discovered clang unavailable.
The preserved script records that assumption. Host002 uses the installed GCC
with ASan/UBSan/leak checks and passes17 actual-surface.c allocation/failure/
geometry/lifecycle cases. This models API responses, not NT5 synchronization.
A malformed Windows UNC path prevented an early source-read check; verify-source.py
instead checks the exact Linux build inputs directly and pins all ten files.

Control preparation first stopped before creating its disk: this hivex binding
throws on a missing optional value rather than returning zero. The failed source
and unchanged SYSTEM bytes are preserved in preparation-failure001. Explicit
value enumeration fixes the host API use; the unlaunched preparation can resume.
No failure is relabeled as a guest driver failure.

Ordinary validation requires54 drawing cases/162 pixel stages, exact identity,
normal restart and dashboard return, full allocation, five structural hives,
unchanged protected executables/configuration/pagefile and strict event deltas.
No debugger or automatic dialog dismissal is allowed. Preserve failures and
never reuse a recorded launch. Timing does not establish Xbox hardware speed.
Shadow coherence, broad GDI/DDI coverage, mode transitions, repeated boots,
independent scanout comparison and crash rendering remain subsequent gates.
