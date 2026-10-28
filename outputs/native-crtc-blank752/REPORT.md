# Test752 closed: native CR02 checkpoint passed

One accepted SITE launch at2026-10-28T00:54:42.207124UTC. User observed green
and a held report. All416 photo bits independently decoded: signature7520000d,
return752, forward752, five cleanup masks0, CR02before9f/after59/restored9f,
selectors1, nativeCR04001003b. See photo002.json and photo-review001.json.

First photo decoder found31/32 bottom-row cells because a reflection raised
one dark cell above its cutoff. Failed photo001 and decoder001 are retained.
Decoder002 uses a global maximum-channel AND mean-channel dark rule. Every
cell agrees across five positions and three threshold sets, with352 adjacent-row
checks. Maximum dark median123; minimum white mean215.33. No expected bit
substitution. Photo remains private at C:/xwn752/photo001.jpg.

User manually power-cycled and confirmed Ready. Nine preparation reports were
collected once, each double-read. Audit001 passed2026-10-28T00:58:21.453502UTC:
exact private/public/staged sources and binaries; allocation/alias disjointness;
unchanged unrelated E directory entries. Preparation PCI/CRTC/SEQ/allocation/
geometry match closed749. Last persisted phase is handoff_armed. Kernel
pre-arm CPU context remains distinct from native optical context.

Native CR00/04/05 neighbor values and individual recovery words are not exposed;
forward status and aggregate recovery masks cover those checks. No native disk
persistence, full mode switch, Windows1.6 boot, or normal shutdown is proved.
Console authenticated at UnleashX. No startup hook or owned process/VM.
All752/prior runtimes CLOSED; do not rerun/recollect/parent.
