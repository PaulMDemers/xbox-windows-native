#646 pending user observation and normal restart

Read actual launch001/observation001/collection001 and the latest user answer.
One SITE accepted; never send another. Observer exec session44493 owns bounded
600second collection. No hook installed;720p already restored. If it is still
running, let it collect rather than racing a second collector. If deadline occurs,
record unknown screen/FTP unavailable and ask user state; do not infer a crash.

After complete collection, run the retained-file audit ONCE with the private
library path (the645 missing-library failure remains recorded):

    wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/display-selector646/audit.py

Record user desktop/file observation, whether restart was normal versus forced,
new6006,selected integrity,events,Ftdisk49 and observer exit separately. Close646
only after collection/audit or explicit bounded failure. Update continuation/docs
and commit/push. No further launch planned in this watched sequence.645 remains
failed boot despite successful selector transfers; full480p selector boot-cycle
qualification remains pending. Never reopen prior closed runtimes.
