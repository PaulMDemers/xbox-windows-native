#644: explicit boot selector prepared; physical cycle pending

The existing E selector now accepts the exact native480p633 launcher, whose
Windows drawing and interaction passed638/642. Legacy two-profile policies remain
accepted. Normal720p is unchanged. The new policy includes480p,720p and the retained
experimental1080i identity; no automatic mode or hardware detection was added.
The480p binary retains its Conexant/HDTV/enabled480p flag gates and fail-closed
behavior. No driver, video programming or compiled launcher was changed.

Host tests exercise the actual selector through a modeled FTP transport: exact
720p-to480p-to720p restoration; first/append transfer failures; corrupt readback;
failed rollback with preserved exact backup; mismatched local/current/prerequisite
bytes; reused/tampered receipts; intervening changes; legacy policy compatibility;
ambiguous pins; no-op selection and forbidden paths.16 tests pass. This does not
prove physical FTP or hardware recovery. A final readback gap was fixed: previously
the last downloaded hash was recorded without requiring equality to the intended
launcher. The new fault test changes bytes between the two reads and requires
failure plus verified rollback.

Private archive: `C:/xwn644/xwn-display-selector644-002.zip`,355907 bytes,
SHA256 `249a270ab9c7254b36cd24f15203acf42140dc1b26bf323f579df730411ba420`.
Eight entries were read back exactly; the independent verifier checks its manifest,
launcher policy and authored source equality. It includes only two matched XBEs,
selector/policy and instructions. No Windows/game/firmware/hives/credentials.
Archive001 and host001 are preserved. Package002 only normalizes policy CRLF to
LF so authored package files exactly match staged Git bytes; JSON meaning and
tested selector code are unchanged. Read package002.json for that check.
No existing release archive was changed. C had23,619,031,040 free bytes before this
small allocation, E21,503,672,320; no WSL process/disk, deletion or backing-chain move.

The PC selector runs at the dashboard. It only changes the next boot's E launcher
and captures a rollback receipt; it never sends SITE or installs a hook. A partial
launcher after a second transport failure remains deliberately unrecognized.
Manual recovery instructions require the exact verified receipt backup and a
reachable dashboard; that recovery has not been physically fault-injected.

No console connection, launch, hook or remote write this turn. Original console
last observed at dashboard; its current state was not freshly queried. All host
verification processes exited.642/643 and all prior closed runtimes remain closed.
Ftdisk49, intermittent boot failures, unsupported primary Lock and1080i findings
remain unchanged. No live switching, fullscreen, revision or acceleration claim.

Read host001.json for actual test output/pins and NEXT.md for the next physical
qualification. These artifacts prepare a selector test, not a new supported release.
