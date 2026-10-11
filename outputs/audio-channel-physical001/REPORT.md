# Xbox dedicated channel listening trial

The unchanged build004 ACI driver passed genuine installation and a subsequent
physical playback boot using the new channel-identification helper. All six
three-second phases completed, followed by normal restart and cold integrity
checks. The captured incoming baseline is restored and verified.

## Listening observations

No user listening observation was received before closure.

Physical left/right mapping: **unverified; awaiting a user observation**.
The earlier audio-listen001 login-sound observation remains valid independently.
Runtime completion alone is not a new listening observation. No instrumented
physical audio capture was made; measured quality remains unqualified.

## Results

| Gate | Result |
| --- | --- |
| Genuine installation | Exact ACI target, SetupAPI success, xwnaci207 binding, problem 0. |
| Subsequent runtime | xwnaci207 module present, legacy module absent; six complete 144,000-frame phases with masks left/right/both repeated twice. |
| Pattern | Each phase has two seconds of low-level tone and one second of encoded silence, followed by a 350 ms inter-cycle pause. Left 400 Hz; right 600 Hz. |
| Shutdown | Joined helpers, unforced restart, one new EventLog6006 and dashboard return on both Windows boots. |
| Cold integrity | Five full hives, protected bytes, preserved event/setup history and policy checks passed. |
| Allocation | Baseline, post-install, post-playback and post-restore scans all passed with zero errors/orphans. |
| Rollback | 1202 readback checks; 11 changed files restored; 3 exact new files removed after preservation. |
| Strict qualification | FAIL: Ftdisk49 remains on both Windows boots. |

Known unrelated wizard cancellation prevents prompt-free boot qualification.
APU, digital output, capture, hardware mixer, protected content, suspend/resume,
future video integration and general repeated-boot storage safety remain outside
these results. Separate emulator storage failures are not resolved by this trial.

## Candidate and preparation

Driver version 0.0.4.207, SHA256
`c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75`.
New helper SHA256
`5ddf733be56e5bbffbcf1ad69f69a6fe31584d4635683a37dd18a0b5c912db77`.
No driver, HAL, kernel, video or APU implementation was changed.

The helper passed source waveform sanitizer checks and six capture-oracle cases,
actual NT5 import checks, and an ordinary emulator boot whose captured PCM showed
the exact left/right/both sequence twice with silence between phases. Emulator
results are recorded separately from user listening observations.

The new physical ticket used a fresh actual baseline capture and exact rollback.
Original startup, hives/companions, INF and audio files are restored; event/setup
history is retained. Inactive evidence paths /F/xwnaC01i, /F/xwnaC01p and the four
/E/Applications/XWNAC01scanB, XWNAC01scanI, XWNAC01scanP, XWNAC01scanR directories
remain preserved. Normal startup invokes none of them. Prior closed tickets and
physical FATX0101/video0093, original0088 and immutable0.1.0 were preserved.

## Records

- [Emulator qualification](../audio-channel001/emu001/audit.json)
- [Captured emulator sequence](../audio-channel001/emu001/capture.json)
- [Installation audit](install001/audit.json)
- [Physical playback audit](playback001/audit.json)
- [Restoration](restored001/restoration.json) and [final confirmation](restored001/confirmation.json)
- [Observations and evidence hashes](review001.json)
- [Closed successor ticket](queue-close.json)

The audio-channel001 physical ticket is closed with no active console operation.
This was a bounded test followed by rollback, not a permanent installation.
