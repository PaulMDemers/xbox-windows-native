# Xbox 1.0 fixed-profile switch controller (847)

This host-side controller supports one fixed target profile per attempt on the
reviewed Xbox 1.0 at `192.168.50.242`. It can move among the verified 720p,
720x480 progressive and experimental 1080i packages. It does not change a
Windows mode live, merge profile files, or install a mode selector. A different
profile means a new fixed-mode boot through the existing default launcher.
1024x576 remains outside this controller.

The two new candidate archives are private and have not been boot-tested:

| Target | Archive SHA-256 | Mode-changing files | Evidence and limit |
| --- | --- | --- | --- |
| 720x480 progressive | `02dac3111407e5f5bae2bab94e534ba4fd83f8cbc8f8f79dbefb5bdf5cbab032` | `default.xbe` | Original console 638/642 observed drawing, text input, saved-file reopening, mouse dragging and normal restart. This newly assembled archive is not boot-tested. |
| 1080i | `ef1a678f47a3ad9d429df4264acdac487f025ab390a41b071fc15360b881c738` | `default.xbe`, `xwnfatx.sys` | Experimental only. Historic viewing showed lost fine text strokes and motion/drag artifacts; field and scanout quality remain unresolved. The archive is not boot-tested. |

The 720p archive is the known return profile. The three package manifests have
6,566 identical E files after excluding exactly two profile-dependent paths:
`E/Applications/XWNEBoot/default.xbe` and
`E/winnt/system32/drivers/xwnfatx.sys`. Their canonical common-tree digest is
`5ff67b5019578504472b9ced1da1bb1a1e7e674d911a2dd814b80c8f9e7a99cf`. The
controller verifies the complete selected ZIP hash and this shared-tree digest,
then changes only the mode launcher and, for 1080i, the matching FATX driver.
This leaves changed hives, logs, documents and other user data in place. Before
any write it also streams a complete backup of all five managed E roots,
including extra files, plus the preserved 642 owner markers.

The existing `xwnsetup.cmd` must match the common package hash and be the only
`.cmd` in the Startup folder. It is checked and left untouched. A detected
startup command or hook stops the attempt. Every profile transfer requires a
recent conservative E free-space observation and preserves the host's 20 GiB
reserve. If FATX free space cannot be measured conservatively, transfer stops.

## Pinned sources

- 480p archive: `D:\xwn844\xbox10-480p-001\xbox10-480p-001.zip`, 326,269,059 bytes.
  Launcher `a53a09427f80411efee73ef53da0ec9829f8af0d27d404f5a3ff818e96b4bde4`;
  FATX driver `41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126`.
- 1080i archive: `D:\xwn844\xbox10-1080i-002\xbox10-1080i-002.zip`, 326,268,424 bytes.
  Launcher `ede6b4f2639b9979a76e5fdec2e9a1d5dd319ef5abf71fc9e09437b2d6ca4034`;
  FATX driver `ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9`.
- All profiles share FreeLoader `8723fc175cc490f0c3cd1650e9c91ab97e9ed04108734ad6202e6f0653804697`, rosload
  `62f3620183cb2c7b1aa575d9908df3e54e043cd5bf62c1c8a291954e9876f4b1`, and
  startup script `257ec9b4c77199f0ac046289912c41acdaba3a30750bf81dfb4c09cbb003af2d`.
- Identity uses `D:\xwn846\identity001.json` with SHA-256
  `a6f313636b36b0bfed3eeadf0ea38a5358b9f40987fff65b6ded2a9aebf6ca2c`, plus
  the completed 846 preflight receipt and its preserved local owner-marker files.
- The active private FTP config is `C:\xwn626\session.py`. It is parsed as
  literal AST data, never executed, copied or logged. The shared 846 helper
  checks the existing hardware ticket, `.242` allowlist and a cross-profile
  host lease. Runtime locks and receipts are excluded by `.gitignore`.

## One attempt

Choose a new lowercase `--attempt` ID and a new private external receipt folder
for each transition. Run the read-only preflight first. Example: change from
720p to 480p after 846 has finished and the original owner markers are still
present. Supply the final 846 receipt hash after verifying its `completed` flag.

```powershell
python outputs\bundle-deploy847\source\preflight.py `
  --profile e-720x480 --source-profile e-720p --attempt switch480001 `
  --archive D:\xwn844\xbox10-480p-001\xbox10-480p-001.zip `
  --archive-sha256 02dac3111407e5f5bae2bab94e534ba4fd83f8cbc8f8f79dbefb5bdf5cbab032 `
  --identity D:\xwn846\identity001.json `
  --identity-sha256 a6f313636b36b0bfed3eeadf0ea38a5358b9f40987fff65b6ded2a9aebf6ca2c `
  --base-receipt D:\xwn846\preflight002\preflight.json `
  --base-receipt-sha256 <completed-846-receipt-sha256> `
  --config C:\xwn626\session.py --dashboard-ip 192.168.50.242 `
  --destination D:\xwn847\e-720x480\switch480001
```

Review the receipt and verify a recent capacity report before the separate
transfer step. The transfer revalidates the source profile, owner markers,
exact two-file delta, all private preimages, endpoint and capacity. It writes
the FATX driver first if needed and the mode launcher last. An uncertain FTP
write leaves an intent journal; never retry that attempt. Use a new attempt
only after manual recovery and independent verification.

After a completed transfer, inspect its journal, then request one separate
launch using `launch.py`. It records durable intent before sending one
`SITE EXEC E:\Applications\XWNEBoot\default.xbe`. It never retries an accepted
or uncertain launch. Screen observation, normal Windows shutdown, dashboard
return and dashboard authentication are distinct evidence; this tool claims
none of them. Each later profile transition requires a new read-only preflight
and fresh receipt. Restore to 720p through the same single-profile flow.

This code has not been used against the console. Do not run it until parent
review and the per-attempt user workflow are ready.

## Offline checks

Run `python outputs\bundle-deploy847\source\test_profiles.py`. The suite
verifies both final archive hashes and manifests, common-tree equality, exact
launcher/driver deltas, startup-hook refusal, current-profile checks that leave
user files outside the profile delta untouched, and stale-capacity refusal.
The tests use local archives or mocked FTP only; they do not connect to a
console or invoke an XBE.
