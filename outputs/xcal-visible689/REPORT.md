# 689 native read preflight — physical attempt closed without success evidence

One launch was accepted at 2026-10-27 00:12:10 UTC. The user observed **solid amber
and a black screen**, rather than the expected alternating green/amber. They
then power-cycled the console as requested and returned it to UnleashX. Staged
bytes were read back twice unchanged; unrelated E-root/application directory
entries were unchanged. No identical retry occurred.

This result does not qualify the native reader. The stopping point is unknown:
the boot could fail before the diagnostic, a CPU/PCI/configuration/SMBus check
could reject it, or the indication could fail. No retained native RAM snapshot
was collected. Solid amber is not assigned a diagnostic meaning by this build.
Dashboard availability after a manual reset is not native completion or normal
Windows shutdown evidence.

## Candidate and validation

689 preserves688's early read preflight and adds two bounded SMC LED writes,
register8 value `0x5f` followed by register7 value1, only after all seven reads
and the final status check succeed. Each write refuses inherited busy/terminal
status, polls at most100,000 times, prioritizes error flags and acknowledges
only its own result. IF is preserved. No timeout retry, reset command or pending
status repair is present. Other failures do not try to signal over an unsafe bus.

The intended signal is green/amber alternation. Even if visible, it would only
prove the code reached the first indicator write after read success: a previously
enabled LED controller could show the new pattern before the second write's
acknowledgement. It would not expose captured register values or qualify GPU output.

The fresh full image passed32 linked-image fixtures under explicit PCI/SMBus
models. These include688's27 cases plus busy/error/timeout indication cases,
with exact transaction order, no legacy startup fallthrough, IF preservation,
PCI-selector restoration and hold behavior. Source/binary pins matched before
staging. No encoder/EEPROM configuration write, GPU setup, Windows boot, file
write from native code or startup hook was intended. The ordinary launcher and
original720p installation were not changed.

See [build](build001.json), [compiled cases](compiled001.json),
[review](review001.json), [stage](stage001.json), [launch](launch001.json),
[user observation](observation001.json), [manual reset](reset001.json),
[collection](collection001.json), and [closure](closure001.json).
The owned E/Applications/XWNXcal689 directory is retained; no hook or host process
is outstanding. The directory comparison is not a whole-volume health audit.
All invoked host fixtures and this runtime are closed. Never rerun/recollect them.

Next: [improve early result observability](NEXT.md) before another native launch.
