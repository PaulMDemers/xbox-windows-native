# xemu change inventory and upstream plan

Inventory reviewed 2026-10-05. No issue, comment or PR submitted. Scope: changes
recorded by this Windows project and the known shared Linux integration project;
this is not an exhaustive audit of every unrelated development checkout.

## Candidate changes

| Change | Classification | Existing evidence | Next gate |
| --- | --- | --- | --- |
| [NVNET access-size alignment](patches/01-nvnet-cromwell.patch) | Likely device-model correction, needs width/side-effect review | Separate Cromwell-compatible build used by earlier fixtures | Verify byte/halfword accesses, neighboring bytes and special-register semantics; provide a small reproducer |
| [NVNET TX batch draining](patches/02-nvnet-drain-tx-batch.patch) | Best-supported upstream candidate | Linux project's matched failing control, two patched passing trials, isolated TX function regression | Port focused test to current upstream, rerun fragment/wrap/invalid/full-ring cases and normal title networking |
| [NV2A BAR resource experiment](patches/03-nv2a-resource-experiment.patch) | Synthetic diagnostic fixture; not submission-ready | Isolated resource-allocation investigation, build/provenance recorded here | Obtain actual BAR read/write sizing and alias behavior from hardware before proposing a faithful model |

The TX patch preserves ring-size bounds and invalid-descriptor termination while
removing the early complete-packet break. The alignment patch relaxes the MMIO
assertion according to access size; an assertion change alone does not establish
correct partial-register side effects. The NV2A experiment conditionally exposes
a 128 MiB alias and optional extra BAR through an environment variable. It must
not be bundled as a general hardware fix.

The original common base was `e72e76bd1f12ce45c6c63b4196c6918ea2cc705d`.
The Linux TX report identifies patched commit
`462416a575af879f1f162bbc6f81b0bbbbc60afc` and matching control
`205f6321d46bde964a67c0d13a358f01462193fd`. Its evidence remains owned by the
Linux project; reading that report here does not constitute rerunning its tests.
`inventory.json` records original source paths, patch hashes and evidence links.

## Upstream context

Read-only GitHub inspection returned upstream master
`478b4f496102379c7eaa7f3ec10e714a703c4300`. The inspected
[NVNET source](https://github.com/xemu-project/xemu/blob/478b4f496102379c7eaa7f3ec10e714a703c4300/hw/xbox/mcpx/nvnet/nvnet.c)
retains the word-alignment assertion and complete-packet break. Search found
existing reports for [Cromwell MMIO access (#2305)](https://github.com/xemu-project/xemu/issues/2305)
and [forcedeth TX timeout (#2910)](https://github.com/xemu-project/xemu/issues/2910).
These are related reports, not proof that every reported symptom has our cause.
The open-PR search for `nvnet` returned none; broader searches and a refreshed
review are still needed immediately before submission.

Current [contribution guidance](https://github.com/xemu-project/xemu/blob/master/CONTRIBUTING.md)
favors faithful hardware models, focused patches, current-master branches and
reproducible validation; hardware-comparison XBEs are encouraged. It also expects
human ownership of review and disclosure of AI assistance/models. Plan separate
networking proposals with small tests and accurate evidence, not one collection
of project workarounds. Recheck that guidance when preparing actual submissions.

## Preparation order

1. Recover and review the TX regression harness and matched control evidence;
   sanitize paths and guest data for a public reproducer.
2. Create a private branch from current upstream and port one change at a time.
   Check existing related PRs/issues and recent NVNET commits again.
3. Build patched/control executables with the same pinned toolchain. Verify
   ordinary workloads plus queue exhaustion, wrap, fragments and IRQ completion.
4. For partial MMIO, build a source-available test XBE and compare real hardware
   with stock/patched xemu. Keep register-specific restrictions explicit.
5. Write concise proposal bodies with cause, change, test commands, limitations,
   provenance and AI disclosure. Review them with the user before submitting.

No modifications were made to the shared Linux project or installed emulator.
