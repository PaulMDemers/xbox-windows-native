# Discriminator

The original screenshot uses the driver's shadow-read path. This probe adds the
existing read-only scanout escape, whose exact implementation reads the mapped
framebuffer through volatile ULONG loads and compares RGB24 with the shadow.
The escape neither changes mode nor fixes data. Sampling before/after each phase
does not atomically capture the two interlaced fields or external signal.

One 1024x512 pattern contains single-row stripes, two-row stripes, ten binary row
bits, and a parity color band. Four phases are static, one-row parity shift,
actual SetWindowPos motion, then static. The independent Python oracle compares
every RGB byte; only unused X bytes are ignored. Caption text is visible but is
not part of the independent pixel oracle. Eight CREATE_NEW readback files and a
CREATE_NEW log prevent accidental reuse. Only the two specified HD modes pass.

Each physical case has its own startup directory, before-events and exact code
checks. A sent launch is not retried. Collection first removes only its hook,
then retrieves each result twice and checks protected code and original startup.
No font, interlace, register, driver, service or event policy is modified.
