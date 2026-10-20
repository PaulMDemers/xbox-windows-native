# PC603: retained saved scene restored exactly

A fresh Windows 2000 PC fixture loaded the retained PC593 Forest Frontiers save
after a deliberate camera movement. The 165600-pixel scenery region matched the
original post-save reference exactly and remained identical ten seconds later.
This qualifies a stationary scene for subsequent cost measurements; it measures
no game FPS, CPU cost, observer overhead or Xbox acceleration.

## Actual run

The immutable404 child used an unchanged retail RCT executable, no debugger or
game patches, a 1024x768 HighColor16 desktop and a 640x480 Window-mode game client.
Both virtual CDs were ejected after the independent 503-file copy verification.
One helper launch reached the title menu and paused Forest Frontiers, moved the
camera with a two-second Right-key hold, then submitted one native Load Game
dialog after checking process ownership, control hierarchy and exact path
readback. Input submission alone was not used as evidence of restoration.

| Comparison in fixed region (160,80)-(620,440) | Changed pixels |
| --- | ---: |
| Initial view to deliberately moved view | 130200 / 165600 |
| Moved view to loaded save | 130200 / 165600 |
| Loaded save to retained PC593 reference | 0 / 165600 |
| Loaded save to capture ten seconds later | 0 / 165600 |

All nine private captures and the retained reference were directly inspected.
The entrance, path and trees visibly return after loading; the options capture
shows Window mode. The comparison excludes UI and pointer pixels. It establishes
the checked camera/scenery state, not every serialized game value.

## Identity and cleanup

The PC593 save is 290244 bytes with SHA256
`ca9a26c940a6dfc8dc5ba53cf8717eb4eb7b247140aa636a0afd29b9bbf5947e`.
It is distinct from the similarly named physical594 save (290247 bytes, SHA256
`fe67dd7567ecd6282b30715a2c0e668a3b9c3baab57b7f7bdce5f1dc69feb77d`).
No physical save or Xbox reload claim is made from this PC comparison.

The game exited with code0 without forced termination. The helper restored the
temporary registry values and requested restart. The VM exited normally at
2026-10-20 03:50:09 UTC. One subsequent cold audit enumerated 7002 files and315
directories; protected OS binaries, seed and audited disk identities were
unchanged. Five hives were clean with independently agreeing raw values, the
temporary game registry subtree was absent, and EventLog6006 increased by one.
New system events were6009,6005,6006. The retained save was byte-identical.
This is not a complete NTFS allocation ownership audit.

## Validation and preserved failure

Build001 failed with `-Werror=misleading-indentation` in the new dialog helper.
Its sources and log remain preserved. Distinct002 source versions split the
ambiguous line; build002 passed with the same warnings policy. The qualified
run603.exe SHA256 is
`590ee996742df4e8f612243b3721052cad29c7a255253d1f1b9daf230defbee3`.

Independent media and 503-entry asset checks, source/binary reviews, four asset
mutation rejections, seven scene rejection cases, actual image comparison and
cold cleanup review passed. See review001.json, scene-review001.json and
final001.json for exact evidence and pins. Private game/media/hives/images remain
outside Git. The runtime is CLOSED; never reopen, recollect or use it as a parent.

All owned VM/build/cold processes exited. No Xbox access occurred. Its last known
state remains dashboard with no owned hook;596 SOFTWARE cleanup remains cold-only.
Launcher, protected720p and transfer ZIPs are unchanged; ZIPs still exclude RCT.
Ftdisk49 and earlier physical shutdown limitations remain separate and unresolved.

## Publication review

The first exact-index review failed on repository documentation line endings:
Git normalized CRLF to LF while the working file still had CRLF. This did not
involve staged tool sources or any runtime result. The failed staged-review001
receipt is preserved. Documentation was explicitly written as LF and restaged;
staged_review002 uses the same checks with a new receipt path. The frozen603
source bytes and the failed/corrected build records remain unchanged.
