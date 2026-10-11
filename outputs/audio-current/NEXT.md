# Current Xbox audio qualification and next work

Updated October 10, 2026, after the closed analog listening trial published at
`2ddf0362d1857b7085718f6926e582bd42f3b5f8`.

Build004 produces user-observed analog sound: the user heard the Windows login
sound through speakers connected to the composite cable audio connectors.
Genuine installation and the subsequent twelve-cycle playback/reset workload
passed their scoped physical gates. The incoming baseline is restored, both
audio physical tickets are closed, and no audio-owned guest or console session
remains active.

Use this continuation together with the [listening report](../audio-listen001/REPORT.md).
Older audio207, audio220 and capability-review001 documents remain historical
records with their original hashes. Their statements that all physical audio is
untested or audibility is wholly unknown are superseded only to the extent of
the later evidence below.

## Evidence and open gates

| Gate | Current result | Evidence needed to advance |
| --- | --- | --- |
| Audible analog output | User heard Windows login sound during the installation boot. | No further evidence is needed for this narrowly worded observation. |
| Installed-driver runtime | Genuine xwnaci207 binding and subsequent loaded-module ownership; twelve cycles completed and normal restart verified. | Requalification for any changed driver, helper, provider or combined fixture. |
| Dedicated tones and stereo routing | No user observation received for the dedicated pattern; left/right routing remains unverified. | A listening observation tied to that case, or a newly coordinated case with distinguishable channel intervals. |
| Signal quality | No instrumented capture. | External capture with known connection, channel mapping, levels and analysis of the actual signal. |
| Whole-boot qualification | FAIL: Ftdisk49 on both Windows boots. | Independently verified resolution; never suppress or waive the event. |
| Prompt-free startup | Not established; known unrelated wizard cancellation was used. | Genuine resolution of pending device setup and a subsequent boot without dialog actions. |
| Digital and APU output | Unsupported/unqualified by this package. | Separate implementation, resource ownership design and physical output evidence. |
| General repeated-boot storage safety | Not established by these bounded audio trials. | Resolution and regression coverage for the separate retained storage failures. |
| New video/HAL integration | Not tested. | Exact combined source/provider/resource manifest and fresh integrated qualification. |

The login sound was heard while build004 was staged under the incoming legacy
filename, before or during genuine SetupAPI installation. The subsequent boot
verified xwnaci207 module ownership and playback completion, but did not receive
a dedicated listening observation. Preserve this distinction when describing
which installed state was heard.

The coordinator's root234 result concerns emulator observation of guest GPU
acknowledgements. It does not change any audio gate or authorize physical access.

## Next independent work

First resolve the outstanding dedicated-pattern observation if the user supplies
it. Record the user's words, the case and its limits without replaying either
closed physical trial. A report of hearing sound alone does not establish correct
left/right routing or measured quality.

For a future qualification helper, use explicit left-only, silence, right-only
and stereo intervals with a logged schedule. The existing probe generates
simultaneous 400 Hz left and 600 Hz right triangular signals; its eight full
two-second plays and four short resets test lifecycle behavior, but simultaneous
tones make channel identification less clear to a listener. A revised helper
would need its own source/build hashes, waveform checks and ordinary emulator
validation before a new physical case. This is a proposed follow-up, not a
built or qualified helper.

Keep the unchanged driver as the control. Any new physical case needs a new
serialized ticket, capture of the then-current incoming baseline, provider and
full hive checks, unique paths, bounded launch/observation, normal restart, cold
checks and verified rollback. The closed audio-listen001 ticket cannot be reused.
Do not silently install the experimental driver permanently.

## Fixed candidate and integration constraints

- Candidate: xwnaci207 version 0.0.4.207, source/package commit
  `7cdb191bd2ef72e24001370726f97a7383a7250b`.
- Driver SHA256:
  `c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75`.
- Use cumulative0210 alone on its documented source base. No driver/helper
  implementation changed during the listening trial.
- Bind only exact ACI01B1, subsystem00000000, revisionB1; APU01B0 is separate.
- Preserve translated ACI MMIO, PortCls interrupt synchronization and ordinary
  DMA allocation ownership. Fixed-codec initialization resets both PCM and
  S/PDIF engines; future digital support needs coordinated engine ownership.
- Preserve physical FATX0101/video0093, original0088 rollback, immutable0.1.0
  and every failed case. No GPU candidate promotion or device merge is implied.

## Authoritative records

- [User listening observation](../audio-listen001/user-observation001.json)
- [Installation audit](../audio-listen001/install001/audit.json)
- [Subsequent playback audit](../audio-listen001/playback001/audit.json)
- [Restoration and readbacks](../audio-listen001/restored001/restoration.json)
- [Final dashboard and baseline confirmation](../audio-listen001/restored001/confirmation.json)
- [Closed successor ticket](../audio-listen001/queue-close.json)
- [Review and evidence hashes](../audio-listen001/review001.json)
- [Source and resource capability review](../audio-capability-review001/README.md)
