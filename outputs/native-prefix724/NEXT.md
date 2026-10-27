# Next: isolate CR1b change during native cleanup

724 CLOSED; never relaunch/recollect/parent its runtime. Console is at UnleashX
after user power cycle; no hook, owned process or VM. Nine prep files audited.
See REPORT.md, observation001.json, photo002.json, audit001.json.

Native724 returned7245: immediate forward11MMIO+4CRTC checks pass, thenCR1b85
at cleanup rather than05. Kernel723 had05 at cleanup. CR1951,CR22fe. Other
cleanup values are unexported; no assumption thatCR1b is the only mismatch.

Prepare a fresh diagnostic with the SAME forward/cleanup write sequence, adding
bounded CR1b read samples after immediate05 check, CR19 restore,680630 restore,
output gate4, SEQ1 restore, and final cleanup reads. Export those samples and
cleanup status; preserve final selectors/output behavior. Every added access
is instrumentation and may perturb timing; report limits. No retry, CR1b85
write, mask waiver, CR22 data write, encoder/timing programming or pending-bit
clear. Keep the result beforeCR22; no full modeset experiment yet.

Validate the changed result offsets/relocations, compiled cleanup model,
independent optical renderer and owned native bridge/CPU fixtures before fresh
XBE stage. If source evidence rules out a candidate, document it rather than
assume hardware semantics. Obtain watcher/photo/reset availability for a held
run, one SITE request20second bound, photo before power-cycle, then collect once.
Ordinary720p remains protected. No native1.6 mode-switch/Windows promotion.
