#639 interactive480p preparation

Unchanged633 native480p candidate, matched installed boot/display inputs and a
fresh never-executed466 child. Probe retains638 geometry/GDI checks, then creates
one owned input.txt and starts Windows Notepad. User replaces all text with
XBOX480, saves and closes. Probe reads and checks exact bytes, reopens Notepad,
and waits for a second close; file must remain exact. Normal restart follows.
One shared300second interaction deadline bounds both sessions. On timeout only
the newly owned Notepad process is terminated, failure is recorded, and normal
restart is requested. Do not enter unrelated work in these test windows.
Emulator input is synthetic validation, not a physical keyboard/mouse result.
Physical launch waits for the user to be available for the interactive actions.
The saved test file is retained for later720p cross-restart readback; no640wide
mode, live Windows switch or general application compatibility claim.
