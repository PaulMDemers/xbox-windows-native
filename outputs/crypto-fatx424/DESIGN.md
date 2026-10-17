# 424 design: compare actual security APIs without changing FATX

The question is whether the six long-name exclusions are harmless historical
files or affect actual native Windows behavior. The original MIT 423 witness
exercises the installed Microsoft enhanced RSA CSP and CryptProtectData APIs.
It deliberately uses short caller-selected container names and a short probe
directory; providers choose their own private storage filenames.

Use identical 423 build001 binaries on a new disposable child of the owned 406
customized-SP4 FATX assembly. Never copy user/machine private keys or blobs from
the successful NTFS control. The two environments share Windows media lineage
but not kernel, hardware or full provisioning, so results are a useful contrast
and direct API evidence, not a perfectly controlled filesystem-only experiment.

Creation and reopen executables have different compiled modes. Each exclusively
creates its own log; reopen verifies the saved SID, existing RSA key/signature,
fresh signature with saved public material, and exact unprotected synthetic
plaintext. It does not create missing keysets. The in-memory CSP context
distinguishes basic provider loading from persistent storage. Direct 41/42/43/69
byte filename cases test the boundary independently. All errors remain numeric
observations and count toward failure; completed logging is not API success.

The runner holds the shared emulator lease, uses the restricted local fixture
forward, sends one launch request and has a finite bound. Ordinary keyboard
input logs into the existing private fixture account, opens Run and types the
reviewed path. A screenshot verifies the path before one submit. No hardware
wizard is dismissed and no startup hook is installed. The probe requests a
normal Windows restart. The dashboard observer signals one orderly host closure.
Only then does the read-only cold collector enumerate files, decode events,
compare protected binaries, independently inspect five hives and audit the full
FATX E allocation. Parent hashes and all frozen inputs must remain unchanged.

The phase-two gate permits first-phase API failures because failure persistence
is the experiment. It requires completed logging, normal restart, orderly host
exit, clean allocation/hives and exact protected binaries. It does not turn the
first failure into a PASS or relax the public clean-install gate.

Collection uses the pinned CP437-aware reader, not lossy ASCII name conversion.
No names are shortened or hashed; no key path is redirected; no driver, ACL,
service, registry policy or event setting is altered. The physical demo and
Xbox C are untouched. The native probe is compatibility diagnostics, not a
recommendation to use its legacy RSA key size for production cryptography.

The exact failing CreateFile/NtCreateFile path/status is not observed here.
Provider error codes and cold files constrain the next trace but do not replace
it. COM+ behavior, arbitrary SP4 media, physical clean installation, recovery,
other hardware revisions and general Windows feature compatibility remain open.
