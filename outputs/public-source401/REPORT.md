# Source review candidate401

Prepared a separate, source-only private review archive from current component
records. No hardware, SDK, original source checkout, tag, public visibility or
private recovery archive changed. No binary compilation or guest launch occurred.

Current archive: C:/xwn401/package001/xwn-source-review401.zip,522791 bytes,
33 entries, SHA256
`3dbd05359123696ac9ab2d0951b09e2e3f654cb19492a3cb77960709d02e64d0`.
Every entry read back exactly; a second assembly from identical inputs has the
same hash. This is deterministic packaging, not a compiler reproducibility claim.
The exact33 files are also retained in this kit's export/ directory. That directory
alone is the review candidate; this kit's private preparation/history records are
not part of a public export.

## Source and tool checks

Six independent cumulative patches replay to the exact recorded FATX390,
HD300, bootE334, display303, launcherE720p374 and audio004 trees. Each applies to
its own base; these patches must not be stacked. All six were independently
replayed through the exported portable CLI into fresh object stores, without
alternates. The launcher exercised full checkout-index materialization; the
ReactOS cases exercised full-object/index reconstruction. Audio's INF was also
actually checked out and its bytes verified.

The audio tree matches32 compiled-source blobs directly. ac97.inf matches the
remaining compiled-source hash under the original tree's explicit text/eol=crlf
rule; both hashes are recorded. No tree normalization or generic exemption was
used. All33 current audio-source hashes agree in their recorded representation.

Fourteen actual utility guard tests passed: changed/missing identities, patch
escape, output/cache/package overlap, low disk reserve, manifest corruption,
unlisted files, duplicate entries and manifest path escape. Tests used synthetic
local inputs; no FTP or compiler was invoked. The included E selector and drag
utility retain their existing source bytes and prior validation; no new physical
selector test is claimed.

All32 payload files passed configured text/type/private-path/IP/credential/token
scans with zero hits; five internal Markdown links resolved. MANIFEST.json is
the33rd archive entry. Original copying texts and changed-file notice inventories
are included. Pattern checks do not establish complete privacy or legal clearance.

## History and publication boundary

Read-only scan of all local reachable refs enumerated27239 objects/23526 unique
blobs:3257 machine-path,601 private-IP,172 credential-literal-review and5 email
category hits. These are triage counts, not172 confirmed exposed secrets. Only
locations/IDs/counts were saved, not matched secret values. No token/private-key
or binary-pattern hit was reported by this scan. Ignored/unreachable/remote-only
objects and commit-author metadata were outside its scope. Do not make the
forensic repository public; use the reviewed allowlist instead.

The candidate remains PRIVATE and public_release_ready=false. Per-file and linked
license review, upstream availability, remaining installed HAL/network/input
provenance, portable compiler provisioning and current-stack builds are unfinished.
The source CLI deliberately verifies source, not a build-version identity: it
leaves an unborn HEAD with an applied index, so the future compiler wrapper must
explicitly establish/document version identity before using Git-derived versions.
The corrected create-only installer still needs disposable-fixture validation.

The physical demo remains FATX390/video303/audio004/E720p374 with original rollback.
720p clean text/dragging and audible tones are user observations. Ftdisk49 remains
a strict failure;1080i text/motion and exact stereo routing remain unresolved.

## Preserved preparation failures

- **001** assumed `.git/objects` under a linked worktree. It failed resolving the
 bootE334 base. Partial source files remain; no completed package was claimed.
- **002** resolved actual Git object directories and replayed five components, then
 rejected audio ac97.inf's checkout-vs-blob hash mismatch.
- **003** explicitly verifies the one upstream CRLF rule and succeeds. Original
 scripts, partial directories, logs and failure reports remain unchanged.

History44181, prepare29917/41317/34950 and portable validation58099 are closed.
All source/packaging operations are confined to this new kit and C:/xwn401.
