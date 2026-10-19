# Deluxe local-data PC control566

The unmodified Deluxe game reached the title menu and rendered Forest Frontiers
in a window with the optical drive empty. This is a PC control, not an Xbox
result. The fresh fixture used original404,64MiB RAM, PentiumIII and Cirrus VGA;
there was no emulated audio device or network.

The full install went to C:\xwn565-kit\game. Twenty Data files missing from the
full installation were copied unchanged from the user's original Deluxe ISO.
The game's Window configuration was retained from the closed564 control. Exact
565runner-build004 temporarily set Path, Language and SetupPath, then launched
the original executable once. Both original and helper discs were ejected before
launch. The combined candidate succeeded; the experiment does not isolate the
individual effects of the additional data and SetupPath.

After180seconds the helper requested a graceful game close. It recorded exit0
without forced termination, restored all three registry values and requested
normal Windows Restart. The independent cold audit found one new6006 shutdown
event, consistent clean hives and unchanged protected OS executables. This is
not a complete independent NTFS allocation-ownership audit.

The first export check failed because CSS0.DAT differed between fresh installs.
That failure and the original script are preserved. Only CSS0.DAT and Game.cfg
differ among shared game files. The [CSS0 parser author's documentation](https://github.com/zackfertig/rct_progress)
identifies CSS0 as scenario/progress state. The corrected exporter preserves
its exact566 bytes separately from immutable assets; it does not rewrite them.
Its semantic contents were not independently decoded. Every other common asset
matches564's already-collected manifest, and every added disc file matches its
original ISO hash. No closed564 disk was reopened.

The verified private export has502 files and533084524bytes. Retail files, the
registry backup and screenshots remain outside the repository. The temporary
helper ISO alone was removed after VM closure and exact ownership/hash checks
to retain host free-space reserve. Original media and reconstruction inputs
remain retained. No console file, hook or launch was changed by this control.

Evidence: observations003.json, no-disc001.json, ntfs-phase1.json,
ntfs-cold1-002.json, transfer001.json, mutable-state001.json and final001.json.
The inherited cold script's runner_present field checks xwn566; actual565 runner
presence and its complete log are independently verified in transfer001.json.
Keep this naming limitation visible; do not interpret that field as a missing
runner or replace the actual rendering observations with exit-code inference.
