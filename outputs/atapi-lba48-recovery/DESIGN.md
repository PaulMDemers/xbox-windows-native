# Separate dump recovery boot

Create recovery003 only after crash006 has passed complete64KiB payload,
correct48-bit wire address, bounded write containment and unchanged alias gates.
The original crash disk and all backing files remain immutable. A new child
changes only startup and adds the owned one-shot recovery observer. It does not
invoke the crash trigger, change dump settings, dismiss dialogs or disable services.

The observer waits at most120seconds for a64KiB recovered Windows dump with the
exact intended bugcheck/cookie, flushes its result and requests normal restart.
Cold audit requires a new saved file byte-identical to the complete crash payload,
preserved old dumps, normal shutdown/dashboard, clean allocation, five structural
hives and all protected hashes. Use Microsoft's signed dump reader independently
to inspect the final saved file's header, crash identity, context and module list.

This is recovery from a deliberate prior crash, not an ordinary strict run.
EventLog6008 and Save Dump1001 carrying the exact intended cookie are explicitly
expected crash evidence and retained verbatim. All other warning/error events
and application deltas fail recovery qualification. No event is suppressed.
Ordinary matched control/candidate qualification remains a separate result.
No physical deployment, recovery snapshot promotion or release-tag changes.

Recovery001 is preserved as a host backing-path failure before guest boot. Its
run disk matched the unbooted seed. Recovery002 uses a fresh unique child with
portable relative backing paths checked before launch; recovery001 is never retried.

Recovery002 also failed before guest boot: the nested relative backing path was
not accepted by Windows xemu. Recovery003 copies only the preserved crash overlay
into the existing artifact directory, rebases that copy to the identical parent
by basename, and requires qemu-img compare across the complete logical disk.
Original crash006 and both failed host attempts remain immutable.
