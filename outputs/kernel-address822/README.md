# Kernel822 address-aware CR19 verification

Physical821 proves CR19 changes30 to31 at the existing framebuffer-address write. This candidate retains full-byte verification using stride and owned-address fields, with all mode writes unchanged. All prior failures preserved; no driver or Windows changes. Host tests model the register alias and reject every wrong CR19 bit. Kernel result is not native/Windows proof.
