# 852 retained 480p failure code

Separate, held 633-based diagnostic; no console launch has occurred. XBE SHA-256 `8bb3f91da378c823588b63d5a59e97b4a018dc2a376cc04741dee44bc5dceb77`; source delta `error852.patch`. It preserves the 633 guard and transaction. On guard or transaction failure it disables interrupts and repeats an LED code instead of requesting reset. It requires manual power-off after observation. The inherited comment referring to a reset is stale; the actual modified branch emits the code and holds. Successful paths continue to normal loader dispatch, which may write to disk: only diagnostic signaling itself avoids persistent writes.

The device first pauses about four seconds with the LED off, then repeats five separated groups. Each pulse lasts about half a second, followed by half a second off; groups have about two seconds off. Count every pulse in each group; for every group subtract **one** to obtain the digit or stage (one pulse means zero):

1. Amber pulses: stage before the failure handler changed it to 255.
2. Red pulses: error tens digit.
3. Green pulses: error units digit.
4. Red pulses: detail tens digit.
5. Green pulses: detail units digit.

For example, amber 3 / red 2 / green 4 / red 1 / green 6 means stage 2, error 13, detail 5. The full five groups repeat after the long pause. Record raw counts and colors, preferably two cycles. An LED transfer error halts reporting; an old light or incomplete sequence cannot establish a code. The timer and SMBus operations are software bounded in loop counts, not guaranteed by wall clock. Timing and LED transactions perturb the system. Color accuracy and full-cycle observation are required; no emulated or physical signal behavior is claimed.

Error 30 is admission refusal (stage 0). Errors 11, 12, 13 are encoder SMBus busy, timeout, or error status respectively; detail is attempted write number, not a register value. Attempts 1 and 2 use register `ba`, 3 and 4 `6c`, 5–17 correspond in order to `d6 2e 32 3c 3e 40 c4 c6 ce a0 9e 9c 6c`, 18 uses `6c` and 19 `ba`. Error 21 is display sync timeout; 22 is vertical-blank edge timeout. Error 23 is geometry readback; detail 21. Error 24 is CRTC readback: detail 22, 23, 24 means index 13, 19, 28 respectively. Stage is the value immediately before failure is set to 255; it is not a complete execution trace.

The actual modified adapter passed 235,552 modeled assertions with diagnostic globals substituted; the actual pulse-group emitter passed 30 modeled cases. Neither test executes the entire reporting loop with real hardware or proves visible colors. Full source patch, build and host receipts are retained for independent review.
