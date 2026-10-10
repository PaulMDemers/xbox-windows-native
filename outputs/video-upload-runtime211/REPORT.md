# Upload accounting119: matched emulator and physical results

The diagnostic identifies actual completed framebuffer uploads without changing
Eng rendering, clipping, cache policy or ownership. Five samples of forty
controlled steps on each platform produced identical phase totals:

| Phase, 200 steps | Bytes | Producers |
| --- | ---: | --- |
| Movement/exposure/chrome | 66,738,880 | CopyBits57,344,000 (85.92%); BitBlt9,394,880 |
| Explicit client repaint | 27,865,600 | CopyBits26,214,400; bounded TextOut1,651,200 |
| Oracle readback | 0 | No framebuffer upload |

Every measured upload had explicit input bounds; no NULL-input upload or clip
fallback appeared in these phases. Movement median333,824 bytes/step, repaint
139,328 bytes/step. This scene provides no evidence for another bounds fix.
Explicit bounds do not establish that every copied byte is optimal. These are
device-global counters including exposure/chrome/background, not timings, FPS,
a generalized desktop workload, or proof of a transfer bottleneck. No speed
improvement is claimed or promoted. See producer-analysis.json and raw samples.

## Build and host evidence

Fresh119 builds210 differ only in XWN_UPLOAD_ACCOUNTING OFF/ON; validated text
bounds ON, scalar stores/body clocks OFF both. Actual treec8654947539246de3ce1e386e7007e124fcaa98f.
OFF DLLdb79d42929ea155b9ac1dcc240dace7fd1e6f136723a83484f5221185119a715,
ON7c3901dd3e457f6cdeb4e4c0e2fb82d2fd6ae1ec9a489cc7be2fe4bd35afba31.
Source/import/compiled-instruction reviews pass; bounded632-byte read-only
escape contains fifteen explicit producers. No new imports or cache changes.
Host ASan/UBSan315,711 arithmetic checks pass. Packet parser rejects20 malformed
cases, actual closed text/lifecycle evidence rejects21 mutations, and additional
sequence review rejects a reset in an inter-step gap. Host tests are distinct
from ordinary GDI results; original frozen within-step parser remains preserved.

## Ordinary emulator pair

control58987 and candidate81630 CLOSED. Exact new packets plus retained265 copy,
200 window checks,25 timed loops/50 coherence stages and all13 text oracles pass.
Each full cold allocation has324 directories,6,727 files,325 directory clusters,
zero errors/orphans, five structural hives and protected payload/policy checks.
Normal restart/dashboard and all five159-transition sequence reviews pass.
Candidate lease refusals occurred before any run/marker creation; exactly one
guest launch accepted00:09:59.885473Z and closed00:13:56.268852Z October10.
No debugger was used. emulator-pair-review.json establishes actual119 coverage
and matched modes/caps/text geometry; it does not qualify hardware timing.

## Physical pair

control96890 and candidate92423 CLOSED. Accepted00:15:41.269241Z and
00:22:14.442337Z October10 respectively; closed00:21:01Z and00:27:17Z.
Both autonomously returned to dashboard, normal shutdown count1, exact pixels/
upload coverage/helper join/install-idle/measurement boundaries pass. Five
complete159-transition sequences pass each. Startup restored FIRST during
collection, then original0101/video0093 display payloads and captured SYSTEM;
independent FTP readback and ten before/after structural hives/protected/typed
policies pass. Device branches were not integrated. Keyboard remained unplugged
as persistently reported. No root-owned process remains.

Both platforms retain sole actual warning/error Ftdisk49 HarddiskVolume6 error3,
outside measurement; no application/popup/measurement errors. Whole-boot strict
qualification remains FALSE; no event waiver or release/storage/dump/new-mode
qualification. Physical full allocation/content scan was not performed in this
narrow display trial. physical-pair-review.json and387-pin evidence-review.json
record exact scope and baseline restoration. Original0088 and immutable0.1.0
remain unchanged. No baseline promotion.

## Retained host failures and next direction

Factory failed001 and prelaunch parser-version correction are preserved.
Physical description-only correction archived original ordinary frozen bytes and
proved literal-only changes before separate physical freeze. Capture creation
fields were completed from compiled helper hashes before FTP capture, without
changing binaries. Unsupported HMP screendump made no image or guest mutation.
A premature index comparison included a normally mutable live observer record;
precommit-live-record-check.json retains this host-only failure. Final index
comparisons must follow closure. A first WSL source search lacked rg and its
pattern was split by the shell; no source or guest changed. The subsequent
bounded Python inventory and private source readback passed.

Closed historical hardware003/004 standalone disks were hash/readback verified
on E with original-path junctions; no active backing-chain relocation or new cold
qualification. Their manifests retain actual timestamps.20GiB C reserve remains.

Next work is the separately reviewed transfer prototype in TRANSFER-NEXT.md.
Pinned local NV2A model source leads are archived privately; they are not hardware
documentation or working acceleration. Existing late-cache review already rejects
a same-buffer UC-to-WC transition preserving the crash pointer; do not repeat it.
No new registers, DMA transfers, driver integration or video modes were attempted.
Independent PCI branch801bdbd delivers SMBus telemetry/persisted binding with
shutdown/audio/physical modem blockers; USB5d86c99 delivers a descriptor collector,
not controller support. Audio remains in its independent investigation.
