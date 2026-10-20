# RCT592 closed: new save survived restart; helper timing check failed

Read REPORT.md, final001.json and save-phase1-review001.json. User screen report
pending. One explicitly requested watched rerun launched, Windows and RCT ran,
normal restart6006delta1. New XWN586.SV4 collected after reboot (290247bytes,
SHA25687f2ddaf852a1ebfc9f8b2c734bbdedfffe83ce8e2a97fb33d0bb41ce7909fd2).
Helper's immediate CreateFile after Save dialog closure returned error2, so
sequence=0, no post-save capture. Gate remains failed. No phase2/load launch.

No owned host process or startup hook remains. Original launcher/startup/720p
preserved; six hive audits and game registry restoration pass; Ftdisk49 recurred.
Game and save retained /E/xwn586-kit/game; now503 files. Existing resultxwn586
must never be reused/overwritten. Prior591 and592 are closed; no rerun/recollect.

Next engineering step: inspect the exact dialog/file-read sequence and prepare
a bounded wait/observation helper that records first file visibility and stable
readback, without resubmitting Save or silently claiming success. Validate it
on a fresh owned PC fixture before new physical execution. Preserve the current
save for a separately justified future reload check; do not overwrite it. No
gate waiver and no inference that the missing immediate file implies corruption.
Space must be re-admitted (host C near20GiB reserve); do not reopen old PC disks.
User only requested this watched rerun; no further console launch now. Other
consoles/fullscreen/boot diagnosis/1080i/sound remain deferred; automation paused.
