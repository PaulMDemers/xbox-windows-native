# Actual reset/crash guard diagnostic221

Fresh isolated children of the immutable211 prelaunch seed receive only the
already reviewed matched219 bootvid control/candidate and a new one-shot guest
trigger. No physical console, GPU channel/context, driver policy or dump setting
changes. A guest IOCTL validates an exact cookie and calls KeBugCheckEx E058D221.
This is intentional sacrificial debugger evidence, never ordinary qualification.

Discover kernel from two actual IDT gates after boot, pin loaded kernel/provider
headers and relocated reset/fill/string bodies. At the intended bugcheck stop,
verify provider state/mapping, then seed the entire excluded84KiB tail with a
deterministic pattern through bounded GDB writes. Pair private/public reset
returns by real entry thread/stack; capture tail and final saved-row bytes after
reset and after crash text before callback processing. The old control must
destroy the guard; candidate must preserve every byte. Compare actual indexed
end to the tail boundary. These are host-seeded guards, not GPU memory contents.

Trace is bounded, removes every owned breakpoint and resumes the guest even on
failure. Preserve a crash screenshot and cold disk. Allow inherited later crash
callback/dump failures without confusing them with rendering evidence: record
them, never claim recovered dump or normal shutdown. Full allocation, five hive
structures, incoming protected bytes and exact trigger intent are cold-audited;
these do not prove all file contents safe. No recovery boot of crash disks.
