# Next: one watched native checkpoint

694 is built, host-tested and staged; NOT launched. Read REPORT.md, review001.json
and stage001.json. All eleven invoked host VMs are closed; no owned host process
or startup hook. Build/emulator leases released, hardware ticket retained.
Incoming1.6 last verified at its HDMI dashboard during staging. Automation paused.

1. Obtain fresh watch/reset availability. The question is pending in this chat.
   Do not infer availability from earlier tests. This probe deliberately holds.
2. Record the reply in ready001.json with continue_authorized and
   watch_reset_confirmed true only when supported. Run physical.py launch once;
   it verifies source/build/staged pins and issues one SITE with a20-second bound.
   Accepted or uncertain launch is never retried.
3. Ask whether the top bar went BLUE then GREEN, stayed blue, showed red, or went
   black, and whether it held or returned automatically. Record exact observation.
   LED color is not this probe's success signal. No Windows should start.
4. If held, ask the user to power-cycle after recording the observation. On their
   dashboard confirmation, record collection-ready001.json and collect once.
   Distinguish manual reset from an automatic refusal return. No normal Windows
   shutdown can be claimed. Preserve failure receipts and exact report phases.
5. Update REPORT/continuation with actual physical scope before proposing any
   next probe. Green only supports this post-paging inherited-framebuffer write.
   Native SMBus/Xcalibur reads and Windows1.6 remain unqualified. No ordinary
   launcher patch, gate waiver, firmware recipe transplant or closed-run retry.

Keep build001, cpu-build001 and cpu-run002 failures. Current sources are build002;
stub001.S preserves the initial assembly. Private binaries/configuration remain
under C:/xwn694; public evidence contains no credentials or proprietary payload.
