# Shared permanent UC framebuffer prototype

Bootvid remains the lifetime owner of its existing uncached direct-RAM4MiB map.
New versioned exports lend the same pointer to the miniport with bounded counted
references and exact geometry checks. No second desktop framebuffer mapping is
created. No cache policy, PAT/MTRR, PTE or display mode changes are implemented.
Mapping lifetime is permanent, including zero desktop references and bugcheck.

The44-byte x86 view ABI carries size/version/address/physical/reserved and visible
lengths/geometry/hidden backbuffer boundary/cache type. The provider refuses early
ownership, user-address requests, mismatched geometry, wrong owners, underflow
and reference overflow. A permanent boot reference prevents unmap on release or
unload. The descriptor publishes once before consumers; reinitialization must
not replace the pointer. Miniport unload drains its owner's accounting only
after VideoPort unload. This does not establish generic PnP consumer quiescence.

Use an explicitly named import library targeting the loader's actual module
name bootvid.dll. Retain every NT5 Vid export and ordinal. A real emulator boot
must prove loader resolution and acquisition; static imports alone are not PASS.

InbvCheckDisplayOwnership is an acquisition precondition, not a lock against
future boot/error drawing. That is acceptable for this UC prototype because no
pointer or cache policy ever changes; it is insufficient for a WC transition.
The crash renderer does not take the provider lock or allocate a new mapping.
Test the compiled provider under hostile caller ordering before guest staging.
Then compare fresh ordinary reconstructed UC control and shared-UC candidate,
with unchanged54-case/162-stage probe, normal shutdown, cold allocation/hive/
binary/configuration/pagefile and strict event gates. Runtime alias proof is a
separate bounded diagnostic, not a timing run. Physical hardware stays unchanged.
