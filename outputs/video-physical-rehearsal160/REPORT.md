# Dependency capture and failed preparation160

Read-only physical dependency capture passed. Kernel/user/display/storage/network
dependencies and installed display INF files were read twice exactly; SYSTEM and
SOFTWARE still matched159. HidServ exists at19728 bytes with the owned matching
SHA256031a1fb5ca4194284d6ecfbfe8afe63589700c1376873267f131ead06946dc6a.
No physical writes or launch occurred.

Control001 preparation failed before a guest launch: its existing-only restore
helper required xboxvnt5.pre-dim, which is absent from the old r15 filesystem.
Preserve preparation-failure.json, prepare.py and the partial private QCOW. No
seed, completed preflight or runtime result exists. Never repeat this identity
or boot the partial child. New161 uses explicit missing/existing/growing-file
restoration on fresh overlays and retains these immutable captured inputs.
