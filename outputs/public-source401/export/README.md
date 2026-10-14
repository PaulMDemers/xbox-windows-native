# Native Windows on Xbox: source review candidate

This is a **private review draft**, prepared from the integrated 720p demo.
It is not a tagged release, Windows distribution, installer or ready-to-flash
firmware. The running console has not been changed by this export.

The six independent cumulative patches reconstruct the recorded source trees
for FATX390, HD300 miniport/boot video, E334 loaders, display303, E720p374 launcher
and audio004. Apply each patch to its own specified upstream commit in a separate
checkout. **Do not stack the six patches.** Their overlapping source histories
and compile-time settings are intentional; they are not one merged source tree.

- [Reconstruct and build](BUILD.md): exact trees, definitions and remaining gaps.
- [Use and configure the demo](USAGE.md): resolution, dragging and partition map.
- [Evidence and limitations](STATUS.md): hardware, emulator and user observations.
- [Licenses and provenance](NOTICE.md): component notices and unresolved review.
- [Release checklist](RELEASE-CHECKLIST.md): what must happen before publication.

Run `python3 -B tools/verify-package.py` after extraction. This checks every file
against MANIFEST.json and refuses extra files; it is not a digital signature.
The archive contains source patches, source utilities, metadata, upstream license
texts and these guides. It excludes Windows files, firmware, EEPROMs, dashboards,
registry hives, personal saves, captures, compiled drivers and Git history.

The private repository's 0.1.0 and 0.2.0 identities are unchanged. This package
does not promote the unresolved 1080i mode or native GPU acceleration.
