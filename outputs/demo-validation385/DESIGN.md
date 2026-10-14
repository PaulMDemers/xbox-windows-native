# Instrumented 720p validation385

Fresh namespace and same binary drivers/payloads as384. Record every file-stage
entry, immediate ERRORLEVEL, stdout and stderr. Preserve original COPY/MOVE
operations. A failed stage skips remaining file actions, emits FILE_FAILED and
runs the independent bounded audio/GDI supervisor, which owns normal restart.
This allows independent evidence; combined/persistence gates STILL require all
six zero statuses, FILE_SUCCESS, exact persisted files and absent intermediates.
No failed stage can produce a successful file marker. Stale files refuse.
Old382/384 attempts remain closed and never retried. No driver/config changes.
All original before/after scans, protected hashes, hives and event gates remain.
Windows C is dashboard E; dashboard C excluded; temporary E startup restored first.
One new launch only. User asked to let supervisor restart without manual reset.
