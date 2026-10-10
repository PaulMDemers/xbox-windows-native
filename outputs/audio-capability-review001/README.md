# Xbox ACI capabilities and integration prerequisites

Review date: 2026-10-10. This source and evidence review covers build004 of
`xwnaci207`, version 0.0.4.207, and the closed hardware220 trial. Its PCM software
path passed installation and runtime checks on the tested Xbox. Audible output
remains unobserved; digital output and APU support are not qualified.

## Capability boundaries

| Capability | Implemented behavior | Evidence and remaining gap |
| --- | --- | --- |
| Device binding | Exact ACI `PCI\VEN_10DE&DEV_01B1&SUBSYS_00000000&REV_B1`; demand-start service `xwnaci207`. | Genuine SetupAPI install and subsequent started-device check passed. The INF does not bind APU01B0. |
| PCM rendering | WaveCyclic render filter with two pins and one DAC; 48,000 Hz, 16-bit, two channels, four-byte frames. | Twelve physical playback/reset cycles passed, including eight full 96,000-sample buffers. Audible stereo and channel routing remain unverified. |
| Codec handling | Recognizes fixed-codec IDs `574D/4C09`; preserves the emulator codec path `8384/7600`; rejects other codec IDs. | Source behavior. An emulator result cannot establish the physical codec's signal output. |
| S/PDIF | Stops and resets the separate output engine on fixed-codec initialization; exposes no digital stream. | Quiescing inherited DMA is not digital playback support. No receiver-lock or captured digital-output result exists in this trial. |
| HDMI adapter output | No qualified adapter configuration. | Adapter model, connection and actual source of audio are unknown. Do not assume the adapter consumes the candidate's PCM output. |
| APU01B0 | No binding or APU implementation in this package. | It remains a separate unsupported function; expanding the ACI INF would not implement it. |
| Capture and hardware mixer | No capture interface or separate hardware topology filter. Fixed-codec register writes return unsupported. | INF registration for `wave,mixer` does not establish hardware mixer controls. Software volume behavior is not qualified here. |
| Protected content and power transitions | No qualification claim. | Playback/reset and normal-restart results do not establish protected-content behavior or suspend/resume reliability. |

The source boundaries are visible in [the exact INF](../audio207/xwnaci207.inf)
and [cumulative patch0210](../audio207/0210-waveonly-cumulative.patch):
`ValidateResources`, `CAC97AdapterCommon::Init`, `ProgramSampleRate`,
`CMiniport::TestDataFormat`, `CMiniport::Init`, and `NewStream`.
The [physical report](../audio220/REPORT.md) and
[playback audit](../audio220/playback001/audit.json) establish the tested runtime
scope. The [audibility record](../audio220/audibility.json) explicitly records
an unknown connection and no user observation; it is not a report of silence.

## Resource and ownership prerequisites

The preserved [physical resource design](../audio207/PHYSICAL-DESIGN.md) records
ACI at PCI00:06.0, BAR values D001/D201/FEC00000 and IRQ6; APU is separately at
PCI00:05.0, FE800000 and IRQ5. These are observations from that machine, not
addresses to hard-code into a new integration.

The driver accepts zero or two translated I/O ranges, one translated memory
resource of at least 0x180 bytes, one interrupt and no legacy DMA resource.
It validates the resource shape and maps 0x180 bytes of the supplied MMIO address
as noncached memory. A zero legacy-DMA-resource count does not mean it avoids
bus-master DMA: the stream uses DMA/common-buffer allocations.

Future PCI, HAL or video integration should preserve these contracts:

1. Supply valid translated ACI resources and the interrupt contract used by
   PortCls. Compare the actual new resource assignment with the retained record;
   do not treat the old IRQ/BAR values as a new observation.
2. Preserve DMA allocation ownership, addressability and interrupt synchronization.
   The source checks 32-bit address bounds and alignment, detaches the ISR-visible
   stream at interrupt synchronization level, and releases descriptors only after
   confirmed halt. Unconfirmed halt faults the miniport and retains allocations.
3. Give the audio driver exclusive ownership of the output engines it initializes.
   Its fixed-codec initialization resets both PCM and S/PDIF engines, even though
   only PCM is exposed. A future digital driver cannot independently own that
   same engine without an explicit shared ownership and shutdown design.
4. Pin the actual HAL, kernel, PortCls and other imported providers for the new
   fixture. Hardware220's provider checks apply to its captured bytes; a changed
   provider or resource implementation needs its own compatibility assessment.
5. Qualify the exact combined fixture through genuine binding, subsequent playback,
   joined helpers, normal restart and cold integrity checks. Existing audio results
   do not establish compatibility with future GPU memory layouts or ownership.

No GPU register/context operations were introduced by the audio work. This
review identifies integration contracts; it does not diagnose a current conflict
with the coordinator's video work.

## Work needed before claiming digital or APU support

Digital output needs a defined connector/adapter target, a reviewed account of
its routing and format requirements, an implemented stream and DMA lifecycle for
that target, and physical output evidence. The existing stop/reset sequence is
only a starting point for ownership review. It does not establish digital framing,
receiver compatibility, channel status or compressed-format support.

APU support is a separate driver/design task. Before implementation, define its
device/resource owner, required interfaces and formats, interrupt and memory
lifecycle, firmware-inherited state handling, and the relationship to ACI output.
Any such design needs its own source provenance and test cases. No APU code or
digital stream was added by this review.

## Next output verification checklist

The next useful evidence is the actual listening/capture path. Record the Xbox
AV cable, adapter model if present, selected receiver/display input, and whether
the signal path uses analog audio or a digital connection. A recollection from
the closed trial may be recorded as a dated user observation, with its uncertainty;
it cannot supply a new instrumented measurement.

For a future coordinated physical case:

1. Assign a new ticket and unique case directory. Capture the then-current physical
   baseline and startup state; do not assume the restored hardware220 snapshot is
   still current or reuse its closed ticket.
2. Pin the candidate, INF, test helper and output pattern. Use an audible channel
   identification pattern with known left/right timing; record completion and
   reset intervals so shortened cycles are not mistaken for output failures.
3. Record listening and, if available, an external capture independently from
   WinMM completion. Distinguish audible output, correct channel routing and signal
   quality. Listening can establish an observation; measured quality requires a
   suitable capture and analysis.
4. If output is absent, preserve the exact connection, input selection, mute/volume
   state and known working control-path observation before attributing it to the
   driver. Leave an unobserved result unknown.
5. Repeat the existing runtime, normal-shutdown and cold-integrity gates, then
   restore and read back the captured incoming baseline. Keep Ftdisk49 in the
   strict whole-boot verdict and record any wizard actions separately.

This checklist is preparation for a future case. No test was launched or hardware
access performed for this review.

## Reproducible candidate and closed trial

- Source/package commit: `7cdb191bd2ef72e24001370726f97a7383a7250b`.
- Hardware report commit: `5fbcc97185dc9c5ad7deb9ee1f3909fdb7ec0d84`.
- Driver SHA256: `c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75`.
- Cumulative0210 SHA256: `9a90ec42b89d4dc90b0b413e1e84982cda23a3766a38929549b4c3bc6f9336f2`.
- Rebuild inputs: [source manifest](../audio207/source-build004.json) and
  [rebuild instructions](../audio207/SOURCE-REBUILD.md). Apply cumulative0210 alone
  to its documented base; do not stack earlier cumulative patches.
- Closed-trial review: [final review](../audio220/final-review001.json),
  [restoration](../audio220/restored001/restoration.json),
  [confirmation](../audio220/restored001/confirmation.json) and
  [queue closure](../audio220/queue-close.json).

Hardware220 restored the incoming baseline with 1,202 file readback checks and
zero allocation errors/orphans. Its installation and runtime gates passed;
Ftdisk49 still failed strict whole-boot qualification. Known unrelated wizard
cancellation prevents calling those boots prompt-free. The older audio207
documents describing hardware as untested remain historical records; audio220
supplies the later, narrowly scoped physical results.
