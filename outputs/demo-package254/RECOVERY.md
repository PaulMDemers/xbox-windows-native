# Recovery and deployment boundaries

Preserve three independent checkpoints: immutable0.1.0, the pre-integration252
capture and the post-audio/pre-video253 capture. The new private demo recovery
snapshot records the combined installed state; it is file-level, not a disk image
or proof of a tested bare-metal restore. Its manifest specifies every included
file and ZIP hash. Windows binaries and user profiles stay in private archives.

Do not copy a saved SYSTEM hive over a later installation to apply this overlay.
Audio must be installed through the exact-ID SetupAPI package. Video requires
exactly the two checked InstalledDisplayDrivers value changes from
video-binding-changes.json on a fresh hive, preserving every other semantic value.
An actual native console may need the reviewed legacy ACI bootstrap before the
genuine audio installer; the guarded252 workflow records that transition.

The reviewed253 workflow captures original video bytes and SYSTEM companions,
records its launch once, restores ordinary startup first when collecting, then
audits the result. If it fails, rollback.py restores only its video/SYSTEM changes
after checking preserved evidence; the genuine audio install remains intact.
Restored allocation checks are required. The252 recovery path restores the
earlier audio state separately. Never replay a completed or uncertain launch.

UnleashX F: contains the installation that Windows calls C:. The dashboard's C:
can be a shadow partition. Do not format, repartition, rewrite drive boundaries,
copy an unrelated C: tree, or change the dashboard boot chain for this overlay.
The existing root Windows entry launches E:\Applications\XWNFBoot\default.xbe.
No installer or recovery action runs merely by unpacking this ZIP.
