# Reconstructed loader physical comparison 422

The three reviewed 416 artifacts are temporarily active at the original
E:/Applications/XWNEBoot paths. Activation completed with readback verification;
the previous active originals remain at same-directory `.422old` paths, with
additional known rollback copies under E:/xwn416-stage/baseline. No launch command
was sent. The user has been asked to use the same UnleashX File Explorer entry
as the working Windows demo. Boot, playback, normal restart and rollback results
are pending; staging/activation alone is not a boot result.

## Current baseline review

The first read-only preflight refused a changed SYSTEM hash before any write.
That failed record is retained. A separate read-only capture preserved current
SYSTEM/SOFTWARE, event logs and startup twice with identical readback. All selected
active code, inactive candidate/rollback files and owner marker matched 416.

Full decoded key/value comparisons covered 6,022 SYSTEM keys and 26,921 SOFTWARE
keys. There were no added/deleted keys or changed value types: 24 SYSTEM and eight
SOFTWARE values changed. These concern print/logon/shutdown times, DHCP state,
LanmanServer GUID, RNG seed, WBEM heap sizing, profile load times and synchronization
timestamps. All other decoded key/value data, including driver, display, pagefile
and mount settings, matched. Hive timestamps, security descriptors and free-space
layout are outside this semantic comparison. Private values remain on the host.

An explicit reviewed fresh baseline pins both current hives; the original 416
stage and failed 422 preflight were not rewritten. The review rejects 128 negative
mutations. New 422 activation/restore tooling retains the original restore-planner
AST and journal sequence, uses fresh local/remote evidence names, and requires
the reviewed capture hashes. Its finite rollback planner passed 256 states
(14 accepted, 242 refused). FTP failure behavior is not modeled by that test.

## Temporary activation

Only these active paths changed:

- E:/Applications/XWNEBoot/loader/halxboxnt5.dll
- E:/Applications/XWNEBoot/freeldr.sys
- E:/Applications/XWNEBoot/rosload.exe

All candidate bytes match 416 comparison002. Each complete file matches its
original except parsed timestamps/checksum fields; no source behavior was changed
to obtain correspondence. The same original XBE, INI, Windows drivers, startup,
current SYSTEM/SOFTWARE and video mode are retained. Console C was not accessed.
No automatic benchmark or startup restart was installed.

The previously successful inventory FTP launch is a different application. This
loader comparison retains the known working manual File Explorer route so launch
route is not an additional experimental variable. One successful result would
qualify this component replacement only, not the fresh Windows assembly or other
hardware. Strict events, FATX path exclusions and 1080i display defects remain
separate. No public release tag or full installation replacement occurred.
