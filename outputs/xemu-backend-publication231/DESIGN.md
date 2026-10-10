#231 ordered queue telemetry, emulator only

Fresh model child of exact228build002; unchanged refusal predicates and pusher.
Request metadata is published by release state1 and consumed with acquire.
Worker final states3/4/6 are release-published after tuple stores and terminal
claim7. Reports acquire state before reading that tuple. Timeout5 deliberately
exposes no worker tuple because a late worker may still be writing it. Request
words remain immutable after release1. No resets, reuse or ownership grant.

Two real ten-word snapshots under FIFO lock: request and worker gate. Indices
0GET,1PUT,2DMA_STATE,3PUSH0,4PUSH1,5DMA_PUSH,6PULL0,7STATUS,8SUBROUTINE,
9PGRAPH_FIFO. No register writes, consuming drain or fabricated empty bits.
One stopped dashboard request precedes one unchanged224 Windows CPU workload.
Old20KiB RAMIN and84KiB CPU tail get actual physical before/after reads, with
explicit selected/restored GDB mode verification. No physical-console access.
Existing211 emulator wizard policy inherited explicitly; no null-device policy.
Positive readback, ended frontend/backend references and native copy remain
unqualified. Inherited Ftdisk49 remains a strict failure if observed.
