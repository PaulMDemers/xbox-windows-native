#367 host-only memory-policy context correction

365 first cold packet stopped on a nonpresent shadow PTE after two rows. Complete warm packet passed all4050 translations and all within-packet register equality checks. Across these distinct captures only CR0 changed0x80010031->0x8001003b (xor0xA). Intel253668-021 section2.5 identifies bit1MP and bit3TS as floating-point task-control flags; cache controls CD(bit30)/NW(bit29), pagingPG(bit31) and every other captured bit stayed equal. The actual writer/scheduling event was not traced and is not attributed.

New paired interpreter compares all CR3/CR4/CPUID/PAT/MTRR fields exactly and every CR0 bit EXCEPT MP/TS across distinct cold/warm captures. It reports raw values and their xor. No masks change within a complete capture: native status, before/after CPU equality, translations, geometry/ownership, page rights, full buffer read/byte check and all error gates remain. A partial cold capture stays partial; nonpresent PTEs receive no PFN/cache interpretation. decode.py remains byte-identical360. No guest data/register or raw evidence is changed. This corrects a memory-policy comparison; it does not prove uninterrupted CPU/FPU context.

Original365 audit/final-review stay failed, as do362 and359. New supplemental scoped qualification requires all original nonmemory workload/audio/identity/integrity/shutdown/event-interval gates and these independently checked ten memory pairs. Whole-boot Ftdisk49 still prevents strict/release qualification. No rerun or physical access for this analysis.

Primary source: https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366821.pdf (253668-021, section2.5, printed2-19 through2-22).
