# Live nine-MiB mapping diagnostic

Scoped mapping and resumed-workload checks PASS. Strict whole-boot qualification remains FALSE for the inherited Ftdisk49 on HarddiskVolume6. This was a stopped-snapshot emulator diagnostic, not an ordinary run or physical HD qualification.

One fresh child of the unused301 candidate preparation launched at19:36:22 UTC on October12. At19:37:38 the owned monitor stopped it, captured registers and64MiB RAM, then resumed at19:37:41. No guest memory/register writes or breakpoints were used. The drawing/audio workload finished, Windows restarted normally, and xemu stopped/quit with exit0. Never relaunch, recollect, or parent from this closed runtime.

Actual IDT vectors0/14 establish the kernel base using pinned trap RVAs. Five resident code pins cover both traps, MmGetPhysicalMemoryRanges, and complete bootvid/miniport text sections with relocations accounted for. The actual ready provider publishes ABI2, physical55MiB,9MiB reserved,720x480/stride2880, and the316160-byte hidden tail.

Both actual physical-memory runs end below the reservation. The highest managed PFN is14078, below framebuffer PFN14080; all2304 reserved pages are excluded. Zero PFN records lie in the managed range: this is not a claim that2304 individual PFN structures were read. All19 linked active process roots have the same2304-page framebuffer view, PCD/PWT set and PAT clear, with exact visible/tail/end translations. No additional present target alias with a different cache policy was found in those roots.

The walker tests passed4616 independent checks. Frozen172 workspace inputs and six host dependencies rehash exactly. Private64MiB RAM and full alias records are separately hashed in mapping.json. Cold allocation is327 directories,6763 files,328 directory clusters, zero errors/orphans; five hives and58 protected hashes pass. Six audio segments and five drawing samples passed, with no warning/error inside the combined workload interval. Ftdisk49 remains a strict failure.

Limitations: point-in-time active roots/present translations only; no TLB/MSR/future-alias guarantee, physical deployment, Windows1080i, GPU ownership or speedup claim. This closes the reservation discriminator before software surface bounds and HD timing work.
