# Gates after the shared UC prototype

Control001/candidate001 are CLOSED ordinary PASS, with full cold gates and
pair-review.json passed. Do not relaunch or recollect either. All owned sessions
are closed; inspect closure.json and continuation for exact identities.

A successful ordinary pair qualifies only boot/drawing/normal restart. Next use
a NEW bounded read-only debugger child to pin actual bootvid/provider/miniport
code and capture publication, acquisition and handoff order. Compare the desktop
pointer to bootvid globals and independently enumerate all current resident page
tables for direct/aperture aliases. Do not infer TLB invalidation from PTE absence.

Then a sacrificial controlled bugcheck on the new shared mapping must demonstrate
bootvid rendering after desktop use and preserve the crash disk/cold integrity
result. No dump/recovery claim from a visible BSOD alone. Keep the existing
completed128GiB recovery evidence and earlier failures separate.

The provider intentionally keeps the UC mapping forever. Its reference count
records borrowers; it does not prove drawing quiescence. WC needs a separately
reviewed transition protocol covering boot/error renderer, GDI consumers, all
aliases and cache/TLB ordering after kernel WC support becomes available. Do not
flip the early kernel flag, mutate private kernel fields, or mix UC/WC aliases.
Generic PnP stop/remove remains unqualified. Physical console unchanged.
