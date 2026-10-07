# Prepared regression: built and reviewed, not launched

The actual mapping lifecycle is established in ../fatx-mapped-lifecycle/002:
58 complete successful appends; all mapped source ranges match cold output.
probe.c and Build.ps1 compile with the pinned RosBE8.4.0 compiler. review.py and
build-review.json verify compiler hash, PE checksum/subsystem5.0, static imports
against owned NT5 DLL exports and CMP_WaitNoPendingInstallEvents dynamically.
No fixture, guest launch or regression result exists yet.

The helper uses13 prefix sizes spanning512-byte,4096-byte and65536-byte boundaries,
including the observed270225 offset. Four rounds each contain18 appends with the
actual observed post-warning chunk lengths:936 mapping/seek/unmap/truncate/close
cycles,52 full-file reopen checks,13 final files. The first220-byte payload is
the actual warning; other bytes are deterministic by offset/index/round.
Every mapping grows to finalEOF+35; seek occurs while mapped, then unmap, close
mapping, SetEndOfFile and file close, matching the target call sequence.

Mode0 uses that application lifecycle. Mode1 adds explicit FlushViewOfFile and
FlushFileBuffers before unmap, plus file flush after truncation. Both modes
flush the initial file and diagnostic log. They require idle installation queues
before work and before normal restart. A timeout holds/fails the attempt rather
than dismissing dialogs or forcing a restart. Immediate reopen checks are not
cold persistence proof. No debugger is needed for the ordinary paired runs.

Next build reproducible paired fixtures and cold auditors BEFORE launching:

1. Use the closed, fully audited fatx-mapped-lifecycle002 output as a preserved
   post-installation parent. Pin its qcow2 hash and unchanged parents. A child
   backing path may reference that retained run, or copy/rebase the delta with
   virtual-disk equality verification. Never modify the completed parent.
2. Stage only the new helper, one-byte mode and startup in new owned child images.
   Use folder xwnmap01. Preserve0101/video0093, boot files and all five hives; hash
   and read back staged data. Create separate fresh seeds and unique run IDs.
   Ensure xwnmap01/result.log is absent before each attempt (CREATE_NEW guard).
3. Add owned Run/supervisor with resource lease and one launch per mode. Wait for
   normal dashboard return without debugger or automatic dialog actions.
4. Cold audits must require exact936 operations,52 checks,13 final file hashes
   matching round3 and their expected sizes, complete normal-restart protocol,
   one normal shutdown, strict event delta gates, complete allocation ownership,
   five structural hives and protected binary/boot hashes. Count total appended
   bytes from Chunks independently. Do not infer persistence from helper output.
5. Compare the two modes with their exact source/fixture/artifact pins; preserve
   failed held runs. Keep normal results separate from earlier debugger and
   intentional interruption results. No physical access or driver patch.

Parent's original startup invokes xwnidle; replace it in children, never the
parent. Parent carries completed helper logs which are historical and must not
be mistaken for new workload results. Decode event deltas from this exact parent.
Check time before work and enforce13:00UTC7October cutoff. Do not rerun completed
mapped-lifecycle or interrupted-append experiments.
