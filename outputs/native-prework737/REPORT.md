# 737 CLOSED: first native read85 after CPU-only work

User observed orange and a held report. All416 photo bits agreed across isolated
cell detection, five sample positions, three thresholds and adjacent-row checks.
Raw rows:7370000d,4,5,7378,793a7efe,30085,20085,850085,30085,
4001003b,0,610,102200f. Private photo hash is in photo001.json.

After4,093 register-only iterations, the first direct and reselected CR1b reads
were both85, before saved6303 restoration. Work checksum793a7efe is independently
recomputed. Actual native CR0/3/4:4001003b/0/610. Final6303/CR1b85; summary reports
full cleanup, selectors,32 unchanged late samples and completed work. Orange
is the unchanged full-byte forward predicate rejecting05 versus85, code7378.

This shows that a preceding post-write read or630 restoration is unnecessary to
obtain85 in this minimal native sequence. Compared with727's immediate05 reads,
added CPU work changes the observed result. No exact delay threshold, bit7
semantics, full-mode safety or root cause of708/709 is established. It is not a
matched full-prefix comparison to735/736, and no mask or repair was introduced.

After photo capture, user confirmed a manual power cycle. Nine preparation
reports collected once with identical double-read; audit001 PASS. PCI/CRTC/
sequencer/geometry/allocation plan match727. Last disk phase handoff_armed is
preparation only; native values come from the photo. Manual power cycle is not
normal Windows shutdown. No hook or owned process/VM; console dashboard.
All737/prior runtimes CLOSED. Preserve packaging review failures below.

---

# 737 staged: native CPU work before the first CR1b read

This compares against native test727: the same minimal630/CR1b sequence, with
4,093 register-only rotate/xor/decrement iterations inserted before the first
post-write CR1b read. Kernel test736 read85 after this work, but used a larger
prefix.737 is not a matched reproduction of736's entire register sequence.

There is one CR1b05 write, the same unlock and6302/saved6303 writes, and the
same output blanking/restoration and full cleanup comparisons. No retry,
repair, bit mask, or CR22/CR33 data write was added. The frontend, native
handoff, page ownership and CPU admission source remain unchanged except IDs.
Work completion requires count4093, final counter0 and checksum793a7efe.

Validation passed:12 fresh diskless CPU fixtures (all closed),51 compiled
integration cases,76 full-framebuffer optical cases,20 nxdk page cases,
372 nxdk ownership cases and131379 host ownership cases. Linked object bytes,
embedded payload/bridge, source delta and frozen source hashes were verified.
Modeled behaviors include unchanged05,85 appearing after the work or other
steps, ignored writes and cleanup failures. These are harness validations,
not physical register semantics or calibrated timing evidence.

The13 optical words report signature7370000d, bridge phase, admission stage,
return code, work checksum, baseline pair, pre-write pair, first direct and
reselected CR1b bytes, final pair, actual native CR0/3/4, and cleanup/work
summary. White is1, black is0, MSB on the left. Decode independently of expected
values. See optical-schema001.json for offsets and packing. Kernel pre-arm CPU
readings are distinct from the actual native readings exported on screen.

Green requires first/reselected05 and successful cleanup. Orange may mean85
was observed after the work with cleanup successful, or a different rejection;
the raw rows distinguish these. No full modeset or Windows qualification.

Staged and read back at E/Applications/XWNMode737. XBE SHA256:
e3d6ef67f8cacbf32aca87268f132f6bf0c848de677d035e5ae824b8a52bab02

No physical launch yet. The native test intentionally holds; it has no supported
post-handoff kernel file writer or automatic return. A watched photo and manual
power cycle are needed. Preparation files alone cannot establish native results.
No hook or owned host process/VM. Console is reachable at the dashboard. All736
and earlier runtimes remain closed. Ordinary720p and launchers are protected.
No737 build/test/stage failure. Final Git index review initially found the
authored linker script ignored; index-review001 preserves that failure. It was
force-added unchanged, and index-review002 verifies all32 frozen source files.
A documentation-only count assertion33 versus actual32 is preserved separately
in documentation-failure001; this report uses the verified manifest count.
Earlier failures remain preserved.
