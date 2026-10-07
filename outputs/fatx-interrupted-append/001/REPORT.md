# First interruption: raw split observed, file length still older

Emulator-only debugger experiment,7October2026. Actual installer launch accepted
06:09:51UTC; checkpoint reached06:11:16.569UTC; owned xemu exited0 and runner
cleanup completed06:11:16.905UTC. All sessions are closed.

At the checkpoint, the exact109-byte SetupAPI warning suffix at270336 had a
successful VfatWrite return and Information109. No write overlapping the target
prefix had been observed. All breakpoints were removed, monitor status was
`paused (debug)`, and HMP quit was sent while GDB remained connected. No step,
resume, detach or Windows shutdown followed the accepted checkpoint.

Cold raw disk reads show the first111 bytes still zero and the following109
exactly correct. The immutable input at that range was all zero. However the
persisted directory entry still reports269718 bytes, so the220-byte target at
270225 is beyond the recorded file size. **The physical file-visible anomaly
has not been reproduced.** This distinguishes data writeback from metadata
publication and justifies testing a later observed write checkpoint.

The interrupted allocation audit fails: one invalid chain terminal for
`/winnt/system32/wbem/repository/$WinMgmt.CFG.BAK` and one orphan cluster.
Five hives parse with matching header sequences. Neither that nor unchanged
selected binaries waives the allocation failure or absent normal shutdown.
This is not an ordinary stability qualification or a driver fix.

HMP quit reset the monitor socket with Windows error10054. The trace retains
that exception under its existing `resume_error` field although no resume was
attempted. The audit explicitly classifies it using the paused checkpoint,
quit request and separately recorded owned process exit0/cleanup. The generic
runner itself exits1 because it treats emulator exit as an exception; its exact
message was `Task emulator exited: 0`. Both outcomes remain recorded.

Evidence: `trace.json`, `launch.json`, `exit-observation.json`,
`interruption-audit.json`, `allocation.json`, source/site pins and private raw
buffers/disk. Original physical reboot method remains unknown. This result
supports a possible interrupted-writeback mechanism only.
