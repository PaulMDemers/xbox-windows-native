# Watched Xbox Deluxe startup test565

This is an exploratory retail-game test through the unchanged ordinary launcher
at 720p. It uses the unmodified Deluxe executable and private installed assets
from fresh PC control566. It is not a driver change or an Xbox compatibility
claim. No game assets are distributed in this repository.

The full installer omits 20 original disc Data files. Control564 failed without
them even though the game exited zero. Control566 combines those original files,
the game's Window setting, and temporary Path/SetupPath registry values. Its
optical drive was empty when the title and Forest Frontiers rendered.

Stage only after verifying the frozen payload, existing resource ownership,
ordinary launcher/startup, protected720p and runtime module hashes. Record current
console E free space and retain at least128MiB beyond the complete payload.
Host C must retain20GiB including collection headroom. Console dashboard C is
off limits. The only new console paths are E:\xwn565-kit, E:\xwn565 and the owned
xwn565.cmd startup hook. Read back every staged file; install the hook last.

Use one SITE request with a20second reply bound. Never retry an accepted or
uncertain launch. The helper backs up Path, Language and SetupPath before setting
them, creates one owned game process, records its visible windows, waits180seconds,
requests a graceful close and waits10seconds. A forced termination is recorded
as a limitation, not a successful game exit. It restores the registry values
before requesting normal Windows Restart. It does not dismiss game dialogs.

On dashboard return remove the exact owned hook first, then collect two matching
reads of logs, game changes, relevant hives/events and protected files. Preserve
new saves. Unchanged retail bytes may refer to the verified private package,
avoiding a second large host copy. Check the game registry subtree independently.
Distinguish dashboard return, Windows desktop, actual game rendering, clean game
exit and normal shutdown evidence. None alone establishes GPU acceleration.

Host controller fault cases are transport models. They cannot establish real
FATX persistence or console behavior. Watch for startup errors, menu rendering
and park rendering; audio and save/load require separate observations.
