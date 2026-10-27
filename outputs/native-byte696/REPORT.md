# Native byte696 CLOSED: reported green cable-read result

One launch was accepted at 2026-10-27T02:09:12.996089Z. Asked about the top bar,
second result bar and hold state, the user replied: **“Green, it’s holding.”**
The reviewed code renders result1 green only after a successful native byte read
from SMC address10/register04 returns cable byte1 and final busy/terminal flags
are clear. This observation supports that limited transaction result; native raw
values were not independently photographed or captured in this run.

The user confirmed the requested manual power-cycle back to UnleashX. Eight
pre-transfer records were each read twice with matching bytes; independent local
hashes also match. Staged files and unrelated E/apps directory entries are
unchanged. The last persisted phase is `handoff_armed`. This is not a normal
Windows shutdown. No Windows payload or startup hook was installed.

## Checked behavior

The kernel admission/allocation policy is unchanged from695 after namespace
renaming. It retains physical target, rounded virtual reservation and high
pointer separately, checks framebuffer custody and compares both4096-byte page
copies. Actual source01f00000, physical stub/requested target01eff000, reservation
01ef0000+10000 and low alias backing000bb000..000bbfff passed. Persisted CPU
context is pre-file-write: EFLAGS296, CR08001003b, CR3f000, CR4610, CS8/DS10/SS10.
Final and native context were RAM-only and lost on manual reset.

The transition through the first green header is unchanged except for relocating
the owned descriptor-table pointers. New code ends at1111 bytes, before GDT4c0;
pointer records end4f6, input begins500, final shadow ends5a0, transaction data
ends5c8, IDT occupies600..e00 and stacke00..1000. Complete CPU fixtures exercise
these actual addresses. The added probe/render code uses at most8 stack bytes
in the IO models; all neighboring-memory and full-frame checks pass.

Native PCI identity, I/O enable and BAR gates remain. CF8 is restored before
SMBus access. The probe paints a blue pending bar, reads entry status, and refuses
inherited busy0800 or terminal0036 without clearing them. With clean entry, it
issues exactly these controller writes:

| Port | Width | Value | Purpose |
| --- | --- | --- | --- |
| C004 | 8 | 21 | SMC10 read address |
| C008 | 8 | 04 | Cable register |
| C002 | 8 | 0A | Start byte-read command |

At most100,000 status-byte polls follow. Completion plus any error is failure.
Only pure completion permits the byte-data read atC006. The probe acknowledges
only observed owned terminal bits0036, once, then retains a final16-bit status
sample. A timeout never acknowledges, resets or retries, even if the final sample
shows a late completion. Final busy/terminal status and an unexpected cable byte
are failures. This is a software poll bound, not a hardware I/O-cycle timeout.
Kernel display APIs are still not application-time-bounded.

Protocol provenance is the authored `outputs/xcal-visible689/config.c`, pinned
in review001.json. The new assembly is GPL-2.0-or-later; the existing supporting
MIT sources retain their licenses. No encoder configuration, firmware setup,
ordinary launcher patch or driver change was made. The prior690 kernel cable
read provides the value1 reference; current kernel HDMI720p eligibility is checked.

## Validation and preserved failure

- Build002 and extract002 pin the actual linked4096-byte template. The staged XBE
  SHA-256 is `3632ea4e5d6d02284dcd012b34e2135b7b37b108499a9dd499c24f6178898ce3`.
- Ten fresh diskless CPU fixtures pass: three mappings reach the expected PC-PCI
  identity refusal display, and seven malformed/fault cases stop without display
  writes. All ten VMs are closed. These do not emulate an Xbox SMBus transaction.
- Thirty-three linked-byte Unicorn IO models pass with exact port events, poll
  counts, CF8 restoration, stack bounds, whole-frame pixels and guard checks. Cases
  include last-poll success, timeout, late completion without acknowledgement,
  inherited status, completion+error, final dirty status and unexpected data.
- Nine actual nxdk page-builder and nineteen memory-policy cases pass.

Build001 linked successfully, but io-review001 rejected the timeout pixels after
four passing cases. Its color table still contained only seven entries; result7
read instruction bytes `FAFDEBF4` instead of blue. Preserve stub001.S, build001,
extract001 and io-review001. Build002 extends only that table to eleven entries;
its timeout color is000000FF. It was validated in fresh models before staging.
Build001 never ran on the Xbox.

The second result bar uses green=success, red=PCI identity, cyan=I/O disabled,
yellow=BAR mismatch, orange=inherited busy, magenta=inherited terminal,
blue=timeout, red-orange=transaction error, white=final dirty status and
violet=unexpected cable. Nine MSB-left rows below show PCI ID, command/status,
BAR, entry, last poll, data, final status, result code and poll count. White=1,
black=0. The first green handoff header remains independent.

## Limits and next step

This supports one native cable-read success indication on the incoming1.6. It
does not identify689's failure, resolve historical boot intermittency, establish
native Xcalibur configuration, or qualify Windows1.6. Original Conexant720p and
the ordinary launcher remain unchanged. No owned host process or hook remains;
hardware ticket retained, build/emulator leases released, automation paused.

Next is a fresh bounded native Xcalibur register read with strict returned-length,
error, ownership and final-status checks before any encoder configuration write.
Do not rerun/recollect696 or any earlier closed runtime.
