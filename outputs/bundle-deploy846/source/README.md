# Bundle deploy 846: Xbox 1.0 fixed-720p preflight

This is a host-only, read-only FTP preflight for one fixed profile. It is
intentionally limited to the Xbox 1.0 720p archive and the reviewed dashboard
IP `192.168.50.242`. It rejects Xbox 1.6, all other IPs and all other bundle
profiles before connecting. It never uploads, creates, deletes, changes startup,
or sends a launch command.

The preflight verifies the ZIP hash and package manifest, checks the operator's
identity JSON against its supplied hash, verifies each marker against its cited
historic evidence receipt, authenticates to the explicitly supplied dashboard
IP, checks the pinned F-volume owner marker, and readbacks the identity markers.
It then inventories and preserves every file and directory below the five
managed E roots, including extras, plus the two historical owner-marker files.
It records exact target casing, all archive target hashes and sizes, before
hashes for present files, and absent paths. Existing files are streamed to a
fresh private local receipt directory and verified by a second local hash.
Files larger than 256 MiB are supported (up to the explicit 8 GiB per-file and
128 GiB total capture limits); unrelated files directly under E are listed to
resolve root names but are never downloaded.

The `capacity.status` remains `insufficient-evidence`: FTP listing file sizes
do not measure free FATX clusters or allocation. A completed read-only receipt
is not authorization to copy or launch the bundle. A separate, recent capacity
measurement and parent review are required before a transfer stage can use it.

## Inputs

- `D:\xwn844\xbox10-720p-002\xbox10-720p-002.zip`, SHA-256
  `e1837395ac915fd1446bf115fc713a9e267df9c79667a2cff018f11cb8415915`.
- The private operator identity JSON `D:\xwn846\identity001.json`, SHA-256
  `a6f313636b36b0bfed3eeadf0ea38a5358b9f40987fff65b6ded2a9aebf6ca2c`.
- Active private FTP config `C:\xwn626\session.py`. The script parses only
  literal `os.environ.update(...)` values with Python AST; it never executes
  the file, records credentials, or prints them. It requires the host to match
  the explicit `--dashboard-ip` and the `.242` allowlist.
- Existing shared `demo251` hardware ticket and the local deployment lease.
  A conflicting or missing ticket/lease fails before connecting.
- A new absolute destination outside the repository. It must have enough free
  space for the entire managed-root preimage plus 128 MiB temporary headroom,
  while retaining at least 20 GiB free on the host volume.

## Invocation (after parent review only)

```powershell
python outputs\bundle-deploy846\source\preflight.py `
  --archive D:\xwn844\xbox10-720p-002\xbox10-720p-002.zip `
  --archive-sha256 e1837395ac915fd1446bf115fc713a9e267df9c79667a2cff018f11cb8415915 `
  --identity D:\xwn846\identity001.json `
  --identity-sha256 a6f313636b36b0bfed3eeadf0ea38a5358b9f40987fff65b6ded2a9aebf6ca2c `
  --config C:\xwn626\session.py `
  --dashboard-ip 192.168.50.242 `
  --destination D:\xwn846\preflight002
```

Never reuse a receipt destination. A partial or failed receipt is retained for
manual review; do not resume it as if it were complete. This preflight does not
perform the separate full-E user backup required by `D:\xwn844\COPYING.txt`.

## Offline mock checks

Run `python outputs\bundle-deploy846\source\test_preflight.py`. The mocks
exercise a multi-level tree, a case-insensitive launcher match, extra files in
managed roots, two owner markers, an unrelated 805,306,368-byte root file,
read-only FTP command constraints, Xbox 1.6 rejection, `.66` endpoint rejection
and marker mismatch. No real FTP connection is made by the test suite.
