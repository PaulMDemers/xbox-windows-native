#321 exact conditional-read diagnostic

320 error25/failure-stage4 is real, but current_crtc data from a combined two-byte register read is not authoritative: prmcio_read returns the selected index value for that access. Preserve320 original record and mark data-byte attribution invalid. The source also exposes unimplemented PRAMDAC total/start readbacks.

This new run adds bounded one-shot hardware breakpoints at actual316 CR39 conditional branch02603948 and timing-loop branch02603968, then the prior apply return. Capture actual register result, independently read expected stack/profile value, EFLAGS and complete resident text at each stop. Read CRTC index/data separately with one-byte accesses; never write the selector or guest registers. Remove every point and restore debugger physical mode/resume before cold audit. Same unused immutable317 seed; no changed loader or physical operation. No ordinary qualification.
