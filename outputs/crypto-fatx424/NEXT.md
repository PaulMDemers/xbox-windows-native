# Next: identify real failing file requests before a namespace change

423 NTFS phase1/2 and 424 emu001/002 are CLOSED and cold-audited. Never relaunch,
recollect, repair or use them as an unrelated test parent. Keep their private
security state and all failed host/reader records intact. No physical test is
queued. The original 720p demo loaders remain restored as recorded in 422.

1. Review exact owned SP4 CSP/DPAPI code and FATX create/name handling. Design a
   new bounded diagnostic that records actual failing native file paths, lengths,
   dispositions and final statuses, paired to the user/machine API call. Avoid
   logging private key or protected-data contents. Account for asynchronous
   completion and prove any debugger or instrumentation teardown.
2. Use a fresh unused child and unique attempt ID only after source/binary pins,
   output guards, fixture lease and space guard pass. C briefly fell below
   20 GiB during cold analysis, then returned to 22,484,520,960 bytes at closeout;
   E had 21,791,899,648 bytes. Recheck the projected reserve before any new
   build/launch. Never move backing chains casually.
3. Compare observed requests with the actual NTFS-created 69-byte key names and
   44-byte user SID component. Machine RSA's generic first error is not sufficient
   to identify the producer. COM+ needs its own meaningful workload.
4. Choose a Windows-compatible storage/namespace design only from that evidence.
   Do not truncate or omit keys, rename SIDs, force successful API results, change
   event/service policies or waive the 42-byte transfer gate. Any implementation
   needs create/enumerate/open/rename/delete/reboot coverage and cold audits.

The user/machine API distinction is now established; another identical probe-only
boot would add little. The next experiment must resolve actual path/status
causality. This does not block using the existing demonstrated 720p installation,
but it blocks calling the clean transfer lossless or generally qualified.
