# Integrated private demo and public-release preparation

The demo retains tested FATX0101, display303/HD boot, audio004 and standard
keyboard/mouse. Unqualified PCI/XID prototypes and unproved GPU/cache changes
are excluded. The small preference add-on passed fresh377 tests before physical
deployment378. Current physical resolution remains1080i. E720p has scoped
emulator qualification and an explicit physical-pending label.

Two private archives were assembled and every member read back:

- preview001/xwn-demo-preview-20261013.zip:364070 bytes,
  SHA2e5bbfec36381681663ec31f7541c91a0ca32200ddfc4bd5c1ced36188090162.
  Drag utility, commands, guides, E mode selector/policy and720p/1080i launchers.
  No Windows media, firmware, EEPROM or hives.
- system001/xwn-private-E-demo-20261013.zip:326632201 bytes,
  SHA f1a6b7c22b8aab813ab86c9739e870e46c26b96c6f862b60a2704ffab53c0528.
 6579 entries,6571 E payload files. Reconstructs verified343 plus the add-on and
  one-time startup; not a fresh capture, generic installer or tested full restore.
  Contains owned Windows/user data and must remain private.

Current root documentation is now concise; the chronological README is archived
byte-for-byte. Guides cover demo, display, rollback, builds, contributing and
public-release gates. New E selector host tests pass; read-only physical
inspection matched its shared prerequisites and current1080i launcher.

The public history scan examined22951 blobs:3202 machine-path hits,585 private
address hits,172 credential-literal review hits and5 email-review hits. These
are review categories, not a claim that every match is secret. It reinforces a
fresh allowlisted public export rather than exposing forensic history. No public
upload, tag change, blanket relicensing or history rewrite occurred. Complete
current-stack reconstruction, component licenses, installer qualification and
final export review remain required.

Two independent driver threads have completed initial work; exact IDs/handoff
hashes are in driver-threads.json. GPU collector host005 passed8805 host-only
checks; actual full provider/worker integration remains. Framebuffer review
identified the missing crash-time scanout fallback and extra-buffer memory cost.
Neither is a runtime speedup or merged into this demo.
