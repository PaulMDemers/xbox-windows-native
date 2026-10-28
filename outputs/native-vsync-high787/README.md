# Native CR07 vertical-sync overflow — Test787

Source-only extension of native785 and kernel786; closed runtimes are not inputs.
`lineage001.json` pins retained source inputs. Exact active sources and public
qualification receipts are pinned by `sources001.json` and `review001.json`.

The only added hardware write changes CR07 bits7/2, F0 ->74 ->F0, for the pinned
low-resolution target crtcvstart489. CR10 staysD4. Eight adjacent/shared CRTC bytes
are captured and checked; failure inhibits output restoration. Earlier prefix,
horizontal/vertical writes and own saved-value recovery remain required.

Build/qualification order in fresh unique directories: payload_build005.py,
link_review007.py, model.py, host_build005.py, cpu002.py build/run,
integration005.py, optical_review002.py, source_review.py, build006.py,
page_review003.py, page_boundary004.py, plan_review003.py, linked_review004.py,
review_prepare002.py. Use project build/emulator leases, pinned GCC12/nxdk,
projected20GiB guard and fresh attempt IDs. These scripts deliberately refuse
existing output directories/receipts. Do not reopen a closed runtime to reproduce.

`restore_reports.py` reconstructs the lossless split public model001.json and
checks each part and full SHA256. Executables, photos and private records remain
outside the public repository. No firmware/media/Windows binaries are distributed.

The report deliberately holds. Thirteen optical rows use white1/black0, MSBleft;
see optical-schema001.json. Only eight of21masks are shown; finalsuccess requires
all21. Same-value CR02 and NVVVALIDSTART drops remain indistinguishable. Host
models/CPU fixtures prove tested control flow and bounds, not physical semantics.
No full native mode-switch, Windows1.6 or acceleration claim.
