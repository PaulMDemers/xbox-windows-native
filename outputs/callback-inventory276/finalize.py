"""Closed276 evidence review and exact continuation. No guest operations."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(k/'emu001/prepared.json');a=read(k/'emu001/inventory-analysis.json');cold=read(k/'emu001/audit.json');delta=read(k/'emu001/disk-delta.json');t=read(k/'emu001/trace.json')
assert a['scoped_refused_inventory_observation_passed'] and not a['admission_passed']
assert all(sha(Path(path))==digest for path,digest in p['dependencies'].items())
assert all(cold['source_pins'].values()) and all(cold['immutable_copies'].values()) and all(cold['dependencies'].values())
assert cold['eeprom_unchanged'] and all(x['returncode']==0 for x in cold['checks'].values())
assert delta['changed_bytes']==1 and delta['all_file_system_bytes_inherited_unchanged']
pins={}
for attempt in ['001','002','003']:
    r=read(k/('renderer-build'+attempt+'.json'));assert r['borrowed_sources_restored']
    art=Path('E:/Codex-archive/xbox-windows-native/callback276-build'+attempt)
    for name,digest in r['inputs'].items():assert sha(art/'inputs'/name)==digest;pins[str(art/'inputs'/name)]=digest
    if r['passed']:assert sha(art/'xemu-callback276.exe')==r['executable_sha256'];pins[str(art/'xemu-callback276.exe')]=r['executable_sha256']
for n,h in read(k/'source-review.json')['private_source_files'].items():assert sha(Path(n))==h;pins[n]=h
for report in ['host-tests001.json','host-tests003.json']:
    test=read(k/report);assert test['passed'];stem='001' if '001' in report else '003'
    art=Path('E:/Codex-archive/xbox-windows-native/callback276-host'+stem)
    for name,h in test['files'].items():assert sha(art/name)==h;pins[str(art/name)]=h
private=0
for item in t['monitor']:
    if 'private_reply' in item:assert sha(Path(item['private_reply']))==item['sha256'];private+=1
r=dict(closed=True,scoped_inventory_observation_passed=True,strict_passed=False,admission_passed=False,
    actual_callbacks=len(a['matched_callbacks']),all_four_dirty=True,matched_current_native_allocations=2,other_native_allocation_provenance_unresolved=2,
    full_graph_rows=a['complete_graph_rows'],full_graph_pages=a['complete_graph_pages'],ui_pages=a['ui_pages'],
    shader_work_functions_returned=a['extra_graph_scope']['original_work_returned'],thread_exit_or_join_proved=False,
    private_raw_hmp_replies_rehashed=private,native_captures_rehashed=a['native_captures_rehashed'],frozen_dependencies=len(p['dependencies']),private_capsule_pins=pins,
    actual_owner_range_mutations_rejected=a['actual_owner_range_mutations_rejected'],host_getter_checks=17688,host_publication_races=1024,
    independent_wire_mutations=30,actual_no_arm_branch_checks=4128,windows_sharing_tests_passed=True,
    descriptor_count=15,independent_framebuffer_bytes=720,source_guard_bytes=16384,vertex_bytes=384,
    callback_gate_unchanged=True,observer_never_armed=True,release_installed=False,normal_guest_terminal=False,normal_windows_restart=False,
    guest_quarantined=True,frontend_reopened=True,breakpoints_removed=True,physical_mode_restored=True,orderly_host_exit=0,fallback_kill=False,
    qcow_clean=True,eeprom_unchanged=True,whole_disk_equal=False,reserved_sector_changed_bytes=1,filesystem_bytes_inherited_unchanged=True,
    physical_access=False,native_gpu_grant=False,performance_qualified=False,failed_builds_and_reviews_preserved=True)
dest.write_text(json.dumps(r,indent=2)+'\n')
note='''#276 CLOSED — four refused callbacks matched; no release/admission promotion

Read outputs/callback-inventory276/REPORT.md, DESIGN.md, NEXT.md,
source-review.json, final-review.json and emu001/inventory-analysis.json.
All owned processes CLOSED: builds59297/93288/39349, runtime40686. Never
relaunch/recollect/parent276emu001 or old closed cases. Physical unchanged.

Actual observation PASS, admission/strictFALSE. Launch01:00:01->closed01:00:30UTC.
CPU-exclusive epoch1 identified4 callbacks, each bijective with surface graph
identity/range; common actual function/region/device, original classifierPASS.
All four draw_dirty1. Offsets/bytes:54329344/2457600 and53100544/1228800 unbound
with native provenance unresolved;60276736/1228800 currentdepth and
59047936/1228800 currentextra color target exact native matches. None overlaps
four owned texture allocations. Addresses apply ONLY this run. Complete55624
rows/218pages plus8UIpages;48shader workfunctions returned (notthreadjoin),
264indexed rows305known attachments.12actualowner/range mutations rejected.
Native phase11 exact720pixels16384source/guard384vertices and15descriptors.
34native captures/private rawHMP replies rehashed,82frozen dependencies exact.

No observer arm, second CPU acknowledgment, guestreuse or lifetime/retirement
proof. Explicit observe276 preserves reason14 and returns27 for unexpected
zero count BEFORE arm. New getter copies acknowledged immutableCPUmetadata;
saved pointers never dereferenced. Full originalrenderer source reconstructed.
Host17688checks1024publication races30wire mutations;4128actual no-arm cases.
RealWindows sharing transient/permanent tests pass; runtime fullpage collection
works. One status-reader sharing denial did not affect controller. Frontend
reopened, breakpoint/physicalmode teardown, quarantinedguest, orderlyexit0.
ColdQCOW/EEPROMclean,strict8GiB equalityFALSE reservedsector1536onebyte;fullmap/
65536overlay provesfilesystem inheritedunchanged,writerunattributed/no waiver.

Reviewed renderer003 E:/Codex-archive/xbox-windows-native/callback276-build003/
xemu-callback276.exe SHA7a19d5c3c3125b522cd7ca8699b1b6a78356f6b6976732a2c00de01be40de502,
191777779bytes.79inheritedwarnings/no new,19borrowedfilesrestored.001failed
missingpublicdeclaration;002compiled butnewformatwarning reviewFAILED;003adds
gnu_printf annotation and exactgetterretested.001/002 neverlaunched. Host002
branchtest succeeded thenwarningreviewfailed;freshhost004 review passed.

NEXT review NEW narrow transaction contract, not a count4 exception. Complete
CPU callback<->locked SurfaceBinding bijection with identity/range/function/
region/opaque, rejectunknown/duplicate/missing/overflow/overlap with four owned
textures, two acknowledged CPU boundaries pertransaction, stable tuples and
actual owner/context/fences. Keep every dirty surface/callback registered and
unchanged. No downloads/removal/release/joins/pendingclearing or globalreset.
Resolve whether two unbound surfaces can remain outside narrow unit transaction;
if guest allocation ownership needed, NEW capture actual pb framebuffer/extra
allocation globals, not address guesses or firmware labels. No repeatedboot
forluck. Only reviewed/tested explicit contract supports NEW no-release four-
generation actual unchanged source/RGBA/framebuffer control; only qualifying
control supports later separate268release. No whole-backend/nativeGPUgrant.

Closed185non-backing portable hashverified/offloadedE with originaljunction;
outputs/task-storage-offload/portable-276.json. No backingchains moved.
C last21635239936bytes,E39481114624bytes; retain20GiB projectedguard.
All physicaldemo/recovery/strict limitations below remain unchanged.

--- Previous continuation (preserved) ---

'''
path=k.parent/'engineering-notes/CONTINUATION.md';assert not path.read_text().startswith('#276 CLOSED');path.write_text(note+path.read_text())
print(json.dumps({x:y for x,y in r.items() if x!='private_capsule_pins'},indent=2))
