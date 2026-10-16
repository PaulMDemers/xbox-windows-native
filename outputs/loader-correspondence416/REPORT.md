# Loader correspondence and inactive candidate 416

Fresh HAL, FreeLoader and ROS loader builds now match the live415 installed
binaries in every byte outside explicit PE timestamps and checksums. No source
behavior, compiler implementation or Windows configuration was changed to obtain
this match. These results explain how to reconstruct the baseline; they do not
retroactively prove all arbitrary-path403 bytes equivalent or explain the failed
physical menu/FTP launches.

## Actual builds

Build001 materialized fresh HAL and loader profile trees from the pinned base
and overlays. Both complete trees match their manifest references; no shared
source/SDK was edited. It used the independently bootstrapped RosBE compiler
SHA8ab0685d..., with its complete6587-entry toolchain receipt, not the historical
compiler executable. Source roots had the original byte lengths and compiler
macro-prefix maps restored the original diagnostic path spelling.

HAL001 matches the installed2422745-byte HAL except8 timestamp/checksum bytes.
ROS loader001 matches its263826-byte original except8 such bytes. FreeLoader001
did NOT pass:11395 bytes differed and its text virtual size was32 bytes shorter.
The first comparison remains false and unchanged.

The exact original/fresh generated headers and printable strings identified
FreeLoader's banner difference: the recorded original has the build date and
unknown-revision label, whereas the normal fresh checkout has a new date and its
base Git revision. A shorter banner shifts later data and its references.

Separate loader002 used the same pinned source and fresh compiler, with
SOURCE_DATE_EPOCH set to the original build date and CMake Git discovery disabled
solely for this reconstruction. Its generated buildno.h matches the original
byte-for-byte, SHA02eaeacf3ebf0b85c4d979472f41ae81fcf5c128d02a37e7b2e65fc297cce84e.
No generated or binary bytes were patched after compilation.

| Selected candidate | Complete bytes | Differences from installed original |
| --- | ---: | --- |
| HAL001 |2422745 |8, timestamps/checksum only |
| FreeLoader002 |171008 |5, export timestamp/checksum only;2048-byte prepended stub exact |
| ROS loader002 |263826 |8, timestamps/checksum only |

All other bytes, including code, data, relocation information and imports/exports,
are exact under the complete comparison.77 negative controls reject changes to
nonmetadata section bytes, headers, appended/truncated files and the FreeLoader
stub. All three builds retain17 inherited compiler warning instances each, with
no new warning messages relative to the corresponding403 build. This is not a
zero-warning claim. Actual build commands, source trees and log hashes are saved.

## Staging and the next physical comparison

Private candidate and original rollback bytes are under E:/xwn416 on the host.
stage001 records one inactive upload/readback under Xbox E:/xwn416-stage, with
separate candidate/baseline subdirectories and an ownership marker. Only a
completed stage record confirms deployment. The original active files, launcher,
configuration, startup and current SYSTEM/SOFTWARE are checked before and after.
No Xbox C access, firmware/menu edit, driver activation or launch is part of staging.

The actual source hard-codes XWNEBoot in both Xromwell and FreeLoader. Therefore
launching a renamed copy would not test an isolated chain. The staged directory
contains no launchable default.xbe and is not a new dashboard entry. For a valid
comparison, temporarily activate the three reviewed files at their original paths
while preserving and verifying rollback, then use the SAME File Explorer entry.
Keep the original XBE, INI, Windows files and startup unchanged. Capture actual
screen transitions and collect/restore on dashboard return. Do not substitute
FTP SITE EXEC and call it the same route.

No new build has booted on the console or emulator in416. The demo remains the
active baseline until a separately recorded activation. Reconstructed historical
version metadata must not be advertised as the identity of a new public release.
The source/tree/tool receipts, not the banner, identify this candidate.

The clean-install FATX long-name exclusions, strict event failures, fresh registry
parity and physical recovery qualification remain separate. No public tag or
whole-install replacement occurred. All prior failed and partial records remain.
