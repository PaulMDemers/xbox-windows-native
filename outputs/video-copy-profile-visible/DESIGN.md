# Fixed-driver copy-path profile

Discriminator: compare screen overlap with system-memory DIB overlap plus upload, and
isolate fill/upload/readback/DIB overlap at64x64,256x128,768x384. This tests the
feasibility of avoiding framebuffer reads without changing drivers or mapping.
No shadow display driver is implemented or promoted by this experiment.

One ordinary run, three rounds, six paths with rotated order per round:54timings.
Every case must verify both overlap directions before timing and all final pixels
after timing (162 pixel stages). Independent RGB formula ignores unused alpha.
Each loop flushes GDI, pumps messages and checks full visibility. Timings include
those API costs; they are neither pure bandwidth nor window-drag FPS. Bound
4096operations/300ms target, with an outer emulator timeout for blocked GDI.
Source/readback DIBs are top-down32bpp with16pixel margins and explicit stride.
No disk logging within timed loops. Partial/occluded/mismatched cases fail.

Fixed1024x576x32, video0093 and Microsoft framebuf.dll. New child of the exact
ordinary ATAPI0105 candidate fixture; unchanged HAL0102/FATX0103/NVNet0104,
restored HidServ and explicit inherited emulator null/unsupported-device policy.
Require pending-install idle before and after, normal restart/dashboard, complete
cold allocation, five hives, protected hashes and no warning/error/application
event delta. No automatic UI dismissal, physical access or device changes.
This emulator result cannot establish physical memory throughput or safe new
cache attributes. A shadow surface would also need cursor/clipping/ROP/format,
consumer teardown and memory-pressure tests before driver implementation.

The original video-copy-profile/baseline001 is preserved: FAIL_INITIALIZE before
any timing. Welcome window occluded the test; later Notepad and manual restart
were diagnostic cleanup. This NEW kit raises only its own topmost window and
waits at most10seconds for an unobstructed clip before each case, outside timing.
It neither closes the welcome window nor alters its startup preference.

Corrected-kit baseline001 was a host failure before guest boot: Windows xemu
could not open a deep backing path with the longer run name. The run disk still
matched the untouched seed. New baseline002 uses short nt5-vcopy106-baseline002
at the same directory depth; no backing-chain files are moved or changed.
