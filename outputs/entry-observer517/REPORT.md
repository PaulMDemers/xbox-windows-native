# Emulator517 closed: relocated-data diagnostic passes its scoped contract

Exact516 (`a272c18d32f96719ddf5ec07dcc551f74165f797b8247b361c1a4e3b3d84da1d`,
545088bytes) ran once in a new child of the never-executed466 preparation.
SITE was accepted10:45:58.990680UTC; observation ended10:46:27.617230UTC.
The11100 trampoline reached94aff with eight GPRs, EFLAGS and CR0/3/4 unchanged.
The original-preparation guard11105 was never reached. Windows was not started.

Actual929-byte code and320-byte initial data captures match the candidate.
Independent pagewalk evidence places both on the same4KiB physical page, PTE
778275, at virtual94877/94c20. All10 imports match actual kernel export ordinals.
Twelve observed LED/delay/file calls returned status0; file state7, indicator
state2, six status words0, restored saved registers/flags, and one firmware
return-mode1 entry satisfy the original contracts. All breakpoints were removed
and physical-memory mode restored before firmware execution resumed. The owned
host exited0 without fallback. This is29 stops/88 immutable private captures,
not proof of visible LED behavior or physical-console boot reliability.

The control-only return protocol saw a112-byte receipt; cold collection matches
its bytes to the actual memory receipt. Independent reviews reject96 file-call,
58 indicator-call,112 receipt-byte and35 trampoline mutations. The complete
10GB virtual map and327680 local extent bytes were compared:275 bytes changed,
so strict whole-disk equality is FALSE, without waiver or attribution of every
write. FATX276 directories/6554 files/255 directory clusters has zero errors or
orphans. Five hives, three baseline binaries and two event logs are byte-exact;
QCOW/source/EEPROM checks pass. Event equality adds no Windows shutdown claim.
The cold absence check includes the actual inherited handoff.bin name as well
as the older witness.bin spelling. No Windowshook was installed.

Before preparation, the actual stopped trace body, pagewalk/kernel discovery,
ActualCalls verification callbacks and cleanup ran with an explicitly MODELED
fixture derived from retained513 bytes and516 layout. Host008 covers29 stops,
88 captures,176 injected transport failures and33 negative cases. The other
host tests retain113 invalid trampoline states,4 transport boundaries,12 cleanup
paths plus7 cleanup failures,112 header representation negatives,27-stop full
transaction/91 failures/15 indicator mutations,51 file transport failures/21
mutations, and12 argument/return positives with48 negatives. These host tests
are separate from the actual emulator evidence above.

Preserved host007 failure targeted an unused export-header byte;008 instead
targets the validated export ordinal base and NtCreateFile slot. No observer
gate changed. Before any tests, a broad port substitution was found to have
altered a checksum constant in an unexecuted decoder copy; that copy is retained
under pre-review001 and the executable decoder was restored byte-exact to its
parent. Source review reconstructs26 adapted parent files with explicit changes.
No closed runtime was rerun/recollected/parented.

All272 frozen inputs,107 external inputs and473 private files rehash exactly.
Sessions84393/5276/70230 are CLOSED; synchronous cold/review processes exited0.
The generic final-review session list is empty; sessions.json supplies the actual
command IDs. Physical Xbox, ordinary launcher/startup/720p and Xbox C remain
untouched. Physical514 still has no receipt and its cause/LED sequence remains
unresolved. No GPU/D3D/game/ordinary boot/release promotion. Next518 is a separate
physical516 namespace trial under the existing bounded hardware procedure.
