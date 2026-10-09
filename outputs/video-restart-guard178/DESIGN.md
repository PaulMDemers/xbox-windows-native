# Refuse automatic restart during pending PnP installation

177 resident-pinned runtime proves PnP's console logoff cleanup closes/clears its
saved token while the installer's outer creation still uses it. This changes the
owned five-sample runner to ask CMP_WaitNoPendingInstallEvents with a bounded30s
wait and again with zero timeout immediately before requesting restart. Pending,
failed or unexpected results record a blocked reason and exit without requesting
restart. No Windows binary/driver/settings/device policy/service/UI/event changes.

The exact same gate header is host-tested with ASan/UBSan: idle, first timeout,
stale idle then timeout, failures at both queries, unexpected values at both,
and restart API failure. Source/binary/tool pins and actual NT5 imports/export
checked; preparation must cold-match every provider including the dynamically
resolved actual SetupAPI library. A clang host-tool refusal is retained; installed
GCC runs identical header/cases/ASan/UBSan flags, with no guest from the refusal.

One fresh ordinary child from immutable162candidate, same112/v4 display probe,
five independent samples and unchanged30s settling interval, new namespace
xwnvg178. No debugger/UI intervention or physical access. Same strict event gates.
If the guard blocks, the host closes the owned emulator at210s, preserving its
disk; that is an intentional host stop, not a normal shutdown or completed soak.
Cold audit distinguishes display workload, guard behavior, normal restart,
allocation/hive/protected integrity and strict qualification. No held test PASS
substituted for normal lifecycle qualification. Existing failures remain failed.

Even two idle observations cannot atomically prevent future queued work. An idle
return, absent popup or a refused restart alone does not prove device setup is
complete, unsupported hardware works, or the popup/Windows race has been fixed.
Manual completion or supported drivers may still be required before a clean
ordinary reboot. No automatic unidentified dialog actions or device suppression.
