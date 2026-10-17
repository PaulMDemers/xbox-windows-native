# 423: persistent Windows security state across a normal reboot

The six remaining 406 paths are not disposable setup debris. Three RSA files
have 69-byte names; the user SID directory is 44 bytes; the COM+ log component
is 45 bytes. Native FATX accepts at most 42 encoded bytes. Shortening these
names without implementing the consumers' namespace would change identity.
The two OEM437 shortcuts were already resolved in 406 and are not retested.

This diagnostic asks a narrower question before choosing a storage design:
does a newly created Windows key/protection operation persist on the current
FATX installation, compared with the original NTFS installation? It does not
repair or rename any of the six excluded paths, test COM+, or qualify a
long-name implementation.

## Native witness

Original MIT C source builds two no-CRT x86 console executables using the pinned
403 compiler and NT5 subsystem version 5.0. There are no private-key exports,
existing-container deletions, driver changes or registry edits. CryptoAPI and
DPAPI themselves may create state in their normal Windows directories. Only
disposable private guests may run these programs.

First boot creates an exclusively new C:\XWN423 directory and create.log. The
second boot exclusively creates reopen.log. Both run under the same saved SID;
a missing/different identity refuses before crypto work. An existing output
directory/log refuses rather than rerunning an accepted phase.

The probe checks an in-memory enhanced-provider context separately from user
and machine persistent RSA containers. It creates 1024-bit signature keys for
this historical compatibility test, saves only public keys and a signature of
fixed synthetic bytes, then verifies both the saved signature and a newly
generated signature. The reopen binary never creates a missing keyset. DPAPI
user and machine blobs use fixed synthetic data and explicit entropy, forbid
UI, and require byte-exact recovery immediately and after reboot. This is
compatibility evidence, not a recommendation for modern cryptographic use.

Independent direct filenames of 41, 42, 43 and 69 ASCII bytes distinguish the
namespace boundary. Their error results are observations; a decoder does not
turn expected FATX rejection into a lossless-installer PASS. Each API failure
is counted. The complete marker means the bounded sequence finished, not that
every operation succeeded. Normal restart is requested after flushing the log.
The host watchdog is the outer bound for providers that do not return.

## Runtime and cold evidence

The NTFS control uses a NEW QCOW2 overlay of the closed, hashed 404 clean-media
disk. It is a continuation of that install, not another fresh-from-ISO result.
No old disk is booted writable. A private read-only floppy carries the two
probes. Network is absent. Each phase has a unique directory, one owned process
under the emulator lease, and a 420-second deadline. Ordinary keyboard UI input
launches the probe; no debugger or guest register/memory mutation is used.

Phase 2 requires phase 1's closed process, completed cold log and exactly one
new normal-shutdown event. Cold inspection hashes every enumerated ordinary
file while explicitly excluding NTFS metadata, paging and restore/recycle
state. Five hives and event deltas are checked; all Windows EXE/DLL/SYS contents
must remain exact. This is not an independent NTFS allocation-bitmap audit.

The read-only reader uses the existing qemu-nbd socket transport and a bounded
partition stream, never a mount or kernel block-device attachment. Reader002
splits up to 64 MiB per logical read into at most 1 MiB NBD requests. Cross-checks
against seven existing independently extracted cold hashes cover five hives
and two kernel binaries. The original incompatible API call and 32 MiB extent
refusal are retained, as is the import-environment failure. No failed reader
result qualifies a guest.

Private tooling: dissect.ntfs 3.16 (AGPL-3.0-or-later), dissect.cstruct 4.7 and
dissect.util 3.24 (Apache-2.0), downloaded as wheels to E:\xwn423 and installed
only in an isolated directory. Wheel/package hashes and their upstream license
metadata are retained. They are not bundled into the Windows/native utilities
or relabeled MIT. Native probe source is original MIT code. The library's
[upstream documentation](https://docs.dissect.tools/en/latest/projects/dissect.ntfs/index.html)
describes the parser; the pinned implementation uses fs.mft.get, unlike the
current documentation example's fs.get.

## Decision boundary

Actual persistent-key or DPAPI failure on FATX would establish application
impact; it would not alone identify the exact failing file operation. Correlate
new crypto/Protect paths and, if needed, bounded native file-call tracing before
changing a driver. A working memory context is not persistence evidence.
NTFS success alone does not qualify FATX. Existing 406 exclusions and strict
event failures remain. No physical-console access is part of 423.

Any eventual solution must preserve complete logical names, case/collision
rules, directory enumeration, rename/delete, open-handle/cache lifetime and
crash recovery. Native aliases require explicit metadata interoperability with
dashboard writers; a file-backed Windows filesystem requires an actual block,
boot and recovery design. Neither is currently implemented or selected.
