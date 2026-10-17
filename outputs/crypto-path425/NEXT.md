# Next: select a compatible long-name storage design

425emu001 is CLOSED, paired and cold-audited. Do not relaunch/recollect it, rerun
consumed build/sites/parser IDs or edit frozen inputs. Original423/424 operation
results and their failures remain intact. No physical test is queued.

The new evidence answers the file-request question:44-byte SID directories and
69-byte RSA keys reach native file creation and receive C0000106. Machine RSA
uses FILE_OPEN_IF after missing-file lookups. Services.exe requests the user
Protect SID directory during userDPAPI; RPC/impersonation details are outside
this trace. Do not repeat these same probe boots merely to reproduce the names.

Next compare two real storage approaches against the current boot and recovery
paths: a versioned logical long-name layer over FATX, or a file-backed Windows
filesystem volume. Review existing create/lookup/enumeration/rename/delete and
boot-loader dependencies before choosing. No functional patch is installed yet.

For a FATX logical-name design, require deterministic collision-safe physical
aliases plus durable original-name metadata, full case/enumeration semantics,
directory renames, open-handle lifetime, crash ordering and detection of external
dashboard changes. Never silently truncate/hash-rename a name without a complete
reversible logical mapping. FATX directory fields remain42 bytes; changing that
limit in code is not storage support. Dashboard interoperability and recovery
must be explicit, including older drivers encountering unsupported metadata.

A file-backed filesystem instead needs a reviewed block/boot implementation,
allocation mapping and crash/recovery contract; availability of ntfs.sys alone
does not supply that design. Keep Xbox C untouched and retain E compatibility
with stock disks. Windows C and dashboard E are different namespaces.

Start with a bounded host model of the selected metadata/transaction contract
and adversarial collision/torn-write/restart cases before integrating a driver.
Then use fresh isolated matched fixtures and rerun the actual native APIs plus
full namespace operations, COM+ and cold audits. Keep six lossless-transfer
exclusions and strict event gates until measured evidence resolves each one.

Future tracer reuse must move the initial Enter after CPU resume, or separate
arming and submission with acknowledged running state. Preserve425's original
failure and correction records. Do not replay its accepted requests. All raw
keys, blobs, Windows binaries and private media remain outside the public repo.
