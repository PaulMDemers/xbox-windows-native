FATX second-stage diagnostic

Select Applications -> XWN Loader Diagnostic on the Xbox.
Expected final line: XWN80: Handoff diagnostic complete. Windows NOT entered.
Photograph the final screen and then reboot to UnleashX. The halt is intentional.
There is no result file or timed dashboard return in this build.

The test reads the app-local 131075-byte probe.bin, checks every byte and EOF,
then seeks across a sector boundary. It loads rosload.exe, which repeats the
file test through imported FreeLoader services and checks the INI token.

The physical XWN40 test already passed. This second stage passed in a private
64 MiB xemu instance; a wrong INI token correctly halted with XWNFAIL instead.
Neither test enters Windows. The existing Xromwell launcher is reused.

The previous physical freeldr.sys is retained on the console as
freeldr-xwn40.sys. The previous instructions are README-xwn40.txt.
The app folder and dashboard menu entry are unchanged.

Source: ReactOS afc0127e8f937ab68503d715d948844973756aa1 plus the ordered patches
in patch-check-0018.json. Invoke-Build.ps1 builds the opt-in diagnostic; the
normal loader rebuild is recorded separately. The source remains under its
original licenses. No Microsoft Windows binaries are included.
