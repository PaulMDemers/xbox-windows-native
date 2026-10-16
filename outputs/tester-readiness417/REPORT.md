# Public repository and tester kit 417

The repository was verified PUBLIC at main904f6c67. No console access, activation,
launch, release tag or binary publication occurred. Physical testing remains
deferred until this evening;416 stays staged INACTIVE and the existing demo is
unchanged. This work delivers a utilities preview and local packaging tools,
not a newly qualified Windows distribution.

## Public repository review

history001 scanned24,532 unique reachable local Git blobs. No binary/payload or
supported token/private-key pattern matched. Counts:3,485 machine-path blobs,
619 private-IP blobs,174 credential-pattern blobs,69 email-pattern blobs.
credential-triage001 inspected every credential match:95 environment lookups,
76 standard Xbox FTP defaults,3 unattended boolean settings and2 manual-review
matches. The latter are a test assertion containing the text ftp.login and an
environment assignment of the standard emulator default. No distinct nondefault
secret was identified by these checks. This is not a comprehensive secret audit;
author metadata, unreachable and remote-only objects are outside scope. No history
rewrite or visibility change. Historical local paths/failed evidence remain.

README/current licensing/release docs now acknowledge the public repository.
Installation docs no longer assert intermittent boot failure: route-dependent
observations do not prove same-route randomness. Added short tester instructions,
report template, rollout plan, utility-build and bundle instructions, GitHub issue
template and pinned read-only CI workflow. Existing component/source build
instructions retain their actual limitations, including exact launcher compiler
identity and absence of pristine-host validation. No component compiler gate relaxed.

## Utility build and actual emulator test

New original MIT source:src/utilities/hardware-report. Reports kernel version,
kernel RAM pages, hardware revisions/flags, PCI IDs/classes, AV settings/modes,
E space and two read-only encoder-response probes. Failed Conexant/Focus probes
do not identify Xcalibur. No EEPROM dump, keys, serial/MAC, firmware, network
transfer, registry or partition-table API. The only application file write is
a fresh numbered JSON on dashboard E, followed by flush/close/readback.

build001 compiled but emu001 cold audit found NO report. The SDK automounts D
only; a DVD-launched WinAPI E path was not established. Original sources, build
and failed audit preserved. build002 adds a checked standard Partition1 E alias;
an existing different mapping refuses. It never unmounts/replaces an alias.
Both builds use exact nxdk58427c with prebuilt libraries, unchanged SDK headers,
libraries and tools. One inherited linker edata merge warning; no native C
warnings. PE export directory0/0 checked at packaging. Not a full SDK rebuild.

emu002 is a fresh private official blank8GiB child, owned EEPROM/config/ports
and emulator lease. Actual1470-byte report cold-read exactly,12 PCI devices,
kernel-reported64MiB, Conexant response and successful E-space query. Complete
E allocation:3 directories,1 file,4 owned clusters,0 errors/orphans; prior files
unchanged. Both QCOW checks passed; EEPROM unchanged. Whole-disk map comparison
finds the known reserved byte1540 change outside E. Report/allocation scope PASS;
whole-disk unchanged gate FALSE, retained. Not physical revision qualification.

Owned xemu exited0 without fallback kill using no-reboot. No Windows ran and no
dashboard-return observation is claimed for the blank fixture. A requested screen
capture was absent; no UI screenshot claim. Native terminal request vs observed
exit is not independent proof of every on-screen status or reboot path. Cold
report bytes and full allocation are the actual persistence evidence.

The first launch was refused before xemu by capacity guard after WSL preparation;
that record remains. Only the unused prepared child was subsequently launched.
No closed runtime was rerun or used as a new parent.

## Packages and host validation

The7,206,072-byte xwn-utilities-preview-417b.zip contains2,246 files/324 directories:
tested default.xbe, host validators/planner, guides, utility source,2,229 SDK text
source/notice files and build identity. Every ZIP entry readback-verified.
SHA256:070b8c5b54669c6b88a3459e785705aae7cae70873eb61a76d3621f87525792a.
XBE SHA256:dd7fb7777d1806e478571f2680db771ea0ec3d13acba0e679e9077fb420074c7.
Local artifact E:/xwn417/xwn-utilities-preview-417b.zip; no upload performed.
package001 failed before archive creation on Windows path-separator lookup;
separate package002 normalized manifest keys and completed. Package003/417b adds
stricter manifest checks and manual FTP-readback verification commands. Earlier
417 archive remains superseded, never silently replaced. Failed staging kept.

tools/tester_bundle.py provides explicit plan/build/verify. It requires fresh
outputs, exact unchanged staging files, FATX/CP437 paths, case/parent checks,
preserved empty directories, no links, exact ZIP membership and content hashes.
Windows mode requires explicit private-input acknowledgement and essential paths;
this is NOT Windows provisioning, privacy sanitization or licensing clearance.
All manifests retain experimental-not-hardware-qualified. It never uses FTP.
tools/hardware_report.py rejects private extra fields, malformed/duplicate keys,
invalid capacities/ranges and invented encoder inferences.

Final Linux suite passes46 tests including link/restore/bundle/readback negatives.
Final Windows suite46 passes with10 platform skips. Prior suite results retained. All8 maintained component source profiles verify.
CI is configured but its remote run is separate from these local results.

## Capacity and next steps

The20GiB guard remained enforced. Closed executable/evidence files were compressed
in place with NTFS; every logical-file SHA verified unchanged, no files deleted
and no disk/backing chain moved. capacity002 failed on a wrong basename BEFORE
mutation; corrected003 separate. New emulator portable uses a same-volume hard
link to a pinned immutable executable with separate config/scratch; no executable
byte mutation. Prior evidence, SDK and physical rollbacks preserved.

Windows bundle blockers remain: six FATX long-name exclusions, portable clean
provisioning/registry setup, retained strict event failures and physical install/
restore qualification. The private current-console recovery bundle is not a
tester image. Follow docs/tester-rollout.md. Next physical work: inventory utility
check, then the staged416 loader comparison through the known File Explorer route.
