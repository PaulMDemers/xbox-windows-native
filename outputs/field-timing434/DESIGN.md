# Read-only raster timing comparison

One fresh standalone launch uses the stock mode API for 720p, 1080i and recovery
720p. It preserves the Windows launcher, startup and payloads. It never writes
encoder data, timing values, interrupt enables or GPU commands. The sole direct
register writes select the same 23 CRTC indices observed by 307; the selector and
interrupt-enable flag are restored. No interrupt masking during temporal samples.

Each mode paints an owned static pattern, checks every framebuffer pixel before
and after, captures static registers twice and records up to 32,768 raw PCRTC
0x600808 reads bracketed by kernel performance-counter timestamps. Samples span
200 ms, with 10 us stalls and an independent 1,000 ms wall deadline. Capacity,
clock regression, short coverage or bad transport is failure, never success.
No guessed parity bit is masked in or interpreted. The raster observation uses
the same read-only address identified by the upstream Xbox emulator implementers
as the input to GetRasterStatus. xemu's increment-on-read stub is explicitly not
timing validation. No new emulator runtime is justified for this hardware-only
register behavior; compilation, source/binary review and host transport tests
must complete before physical deployment.

Raw values and timestamps can establish counter range, wraps and cadence. They
cannot independently prove which framebuffer rows reach the analog/HDMI output,
nor prove both field parities. Static 540-line CRTC and 1080-line output timings
are consistent with interlace and are not themselves a defect. Changes require
actual evidence, not a guessed timing patch. All files use exclusive creation in
a fresh launch directory; a launch timeout is not permission to retry.

Each raster file contains two 512-byte little-endian headers and N 24-byte
samples (before-counter u64, raw raster u32, after-counter u64, sequence u32).
Headers are explicit u32 arrays, avoiding packing/ABI assumptions. Initial and
terminal result records are eight u32 each. All captures remain private; publish
only hashes, decoded register/timing facts and limitations. A failed partial file
is preserved and never overwritten. No capture is a Windows shutdown, disk-wide
integrity or 1080i visual qualification.
