# Selective syscall trace completed without target capture

Case001 launched once at05:35:21UTC7October2026 and returned normally. It
observed27104 NtWriteFile entries and99 unreadable bounded buffers, retaining
20 error examples. No full matching warning string was captured before dashboard
return. Breakpoints were removed and Windows resumed before owned runner cleanup.

The trace retained matching warning requests only, with an8192-byte buffer cap.
It cannot rule out larger, split, unreadable or non-NtWriteFile logging writes.
It does not prove that the installer never writes the warning. Cold checks found
the exact220-byte warning at270225, normal shutdown, clean allocation and the
expected installation. No physical or ordinary stability qualification follows.

The subsequent FATX-specific diagnostic observes writes by file path rather than
matching the full string. No physical access or guest-driver change occurred.
