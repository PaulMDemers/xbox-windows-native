# Next diagnostic: capture the first failure without bypassing it

The tested732 RAM recorder is a component, not a staged hardware probe.
The next owned attempt must answer which original setup read fails first, with
expected/actual values and actual CPU context. Do not repeat a full-mode black
screen merely to see whether it succeeds this time.

1. Preserve the original phase4 write order and rejection predicate. Keep the
   RAM recorder's one-read-per-entry behavior and first-failure short circuit.
   Record actual GR04 before the operation separately; do not change it to force
   FF. This extra observation must be outside the original read sequence and
   have its selector save/restore independently checked. Its timing is a new
   diagnostic perturbation, not an exact replay of708/709.
2. Stop at the setup boundary regardless of pass/fail, before geometry, encoder
   writes or framebuffer reconfiguration. Give this stop its own diagnostic
   status; do not label stopping before geometry as a full transaction success.
   A pure RAM trace under the original reblank is not observable after power-off.
3. Provide a separately reviewed held framebuffer report using this run's owned
   retained720p allocation, pitch and pixel format. Reporting must occur AFTER
   the original first-failure decision. Any output restore is a diagnostic
   recovery action, not part of the original outcome. Prove its exact bounded
   operations against the prior blank/restore evidence, then host-test failure
   paths and rendering. If safe reporting cannot be established, do not launch.
4. Resolve the admission issue explicitly: original phase4 contains CR22/CR33
   writes whose full restoration/access contracts are not established by731.
   Do not silently reuse ordinary byte-storage semantics or write a saved CR22
   read value as a restore value. Review primary access evidence or narrow the
   experiment to a justified prefix; identify precisely what that prefix can
   and cannot answer. Preserve every cleanup mismatch. No firmware-state replay.
5. Use a new source/binary freeze, negative host tests, linked-byte review,
   resource lease, projected space check and unique E-only stage/readback.
   Obtain watcher/reset readiness only once the concrete probe is staged.
   One SITE request with20second reply bound; never retry accepted/uncertain.
   Record photo/raw observations before reset, collect once at dashboard, close.

No CR22/CR33 write is newly authorized by this host model. This is an engineering
admission requirement, not a request for another broad user permission. Existing
routine hardware authorization remains in effect once the test is justified.
No gate waiver, FF-to-FE substitution, forced plane3, pending-bit clearing,
functional driver patch or native/Windows/acceleration promotion.
