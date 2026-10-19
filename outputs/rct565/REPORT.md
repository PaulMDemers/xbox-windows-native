# Deluxe on native Xbox: watched startup and park rendering

On October 19, 2026, the user confirmed that the prepared RollerCoaster Tycoon
Deluxe installation reached its title menu and rendered Forest Frontiers on
the physical Xbox. The requested sequence was New Game → Forest Frontiers,
followed by the test's automatic restart. The user's exact answer was:

> Yeah it all worked, it just rebooted

This is a watched native-console result. It is separate from the earlier PC
controls for all three supplied editions. A post-close clarification reports
that building worked, but window-edge scrolling left the view completely still.
The exact construction action was not specified. Arrow-key scrolling and
right-button dragging remain untested. Sound testing is deferred at the user's
request. Save/reload, frame rate, extended play and repeated-launch reliability
were not qualified. This additional user observation does not reopen the runtime
or alter its frozen final001 record; see user-observation002.json.
No graphics API trace or native GPU acceleration claim follows from this result.

## Candidate and launch

The private package came from the closed [local-data PC control566](../rct566/REPORT.md).
It contains the full Deluxe installation, twenty additional unmodified Data
files from the supplied disc, the game's built-in Window configuration and
runner004. The executable was not patched. The complete package was read back
after staging and again before launch. The supplied disc SHA-256 is
`7910b1440239f7026821507180e6dfdbc5a119147baaf77c4e542182c1ad9052`.
The game executable SHA-256 is
`bdfebd64383b231de0252fe0726523d1c45aa2c4da919c2d7ed8bfb7aaa05c76`.

Dashboard `E:\xwn565-kit\game` is Windows `C:\xwn565-kit\game`. The original
`E:\Applications\XWNEBoot\default.xbe` launcher and protected 720p configuration
were retained. One SITE request was accepted at 05:57:49 UTC. No second launch
was sent. The helper temporarily set Path, Language and SetupPath, launched
the game once, allowed about three minutes for the watched check, and was
designed to close the game, restore those values and request Windows Restart.

The dashboard authenticated again at 06:02:07 UTC with the runner receipt
listed. Collection first disabled the exact owned startup hook by moving it
out of Startup to `E:\xwn565-kit\startup-used.cmd`. The ordinary startup and
launcher remained byte-identical. Console dashboard C was not accessed.

## Shutdown and readback

The runner recorded the game window, requested its close after 183,405 ms and
received exit code zero without forced termination. It restored the temporary
registry values and successfully requested Windows Restart. Independent review
of the collected SOFTWARE hives confirms that the complete typed game registry
subtree matches its pre-run state, including removal of the newly created keys.

All five registry hives have consistent headers/sequences and independently
agreeing raw values. The event comparison finds one new EventLog 6006 shutdown
record, alongside the observed dashboard return. Ftdisk 49 remains present;
there are no new application events. The scan may include stale records outside
the active ring, so it is a sequence-boundary comparison, not proof of complete
active-ring decoding. Historical shutdown-popup limitations remain unresolved.

Readback covers 527 selected files. The game executable, runner, ten pinned
Windows runtime modules, ordinary launcher and ordinary startup are unchanged.
Only CSS0.DAT and Game.cfg changed within the game package; both versions are
retained privately with hashes. Their semantic contents were not independently
decoded. No new game file or save appeared. This is not a save/reload test.

The original collector hit its 1,200-second bound after 499 verified files.
Its incomplete journal and closed failed supervisor are preserved. One earlier
read timeout recovered through its existing bounded retry. A separate 300-second
read-only continuation verified retained local evidence and fetched only the
28 missing paths, without launching Windows, reinstalling the hook or writing
to the console. It completed in about 81 seconds. The final collection pins the
partial record; it does not overwrite the timeout. The initial offline audit
also failed before reading hives because libhivex's library path was missing.
That failure is retained; the same audit succeeded with the existing offline
toolchain's library directory supplied through LD_LIBRARY_PATH.

The runtime is CLOSED. Both collector processes have exited, the Xbox is at the
dashboard and no temporary startup hook remains armed. Do not rerun, recollect
or parent this closed runtime. A future gameplay check needs a new attempt ID.

## Preserved failures and scope

The earlier missing-disc-data PC failure remains recorded in
[control564](../rct564/REPORT.md), including its zero process exit status despite
an initialization error. That is why this test required a watched park result.
The [FTP transport investigation](TRANSPORT.md) preserves the slow first stage,
partial-file cleanup correction, stage002 refusal and stage003 upload timeout.
Stage004 completed the same package using bounded chunked uploads; none of
those staging attempts launched Windows or changed the game executable.

Retail assets, ISO files, screenshots and registry hives remain private.
Published evidence consists of source, hashes, metadata and observations.
The collected file/hive checks do not constitute a complete FATX allocation
ownership audit, and one successful game run does not resolve the tabled boot
intermittency or shutdown-popup investigations.

Evidence: `stage004.json`, `launch001.json`, `observation001.json`,
`user-observation001.json`, `user-observation002.json`, `collection001.json`, `collection002.json`,
`audit1.json`, `registry-review001.json`, `closeout-review001.json`,
`final001.json` and their supervisor records.
