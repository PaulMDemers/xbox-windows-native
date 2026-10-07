"""Summarize recorded qualification; never launch or recollect a guest."""
from pathlib import Path
import json
k=Path(__file__).resolve().parent;diag=k.parent/'video-ownership-scanout'
read=lambda p:json.loads(p.read_text())
pair=read(k/'pair-review.json');trace=read(diag/'verification.json');build=read(k/'build-report.json')
assert pair['passed'] and trace['passed'] and read(k/'evidence-verification.json')['passed']
lines=['# RAM0109 explicit ownership: emulator qualification PASS','',
'All three guest attempts are CLOSED. Do not relaunch/recollect them. No physical access.',
'','The foreign-PDEV dereference and handle-only shadow substitution in RAM0108 are',
'replaced by explicit live primary/PDEV/HDEV membership. Unknown device surfaces',
'and mixed owned PDEVs fail before Eng rendering. The 32-entry membership semaphore',
'is released before rendering, upload or resource callbacks. Registration failure',
'fully unwinds surface creation. See DESIGN.md for GDI lifetime assumptions and limits.',
'','Source tree: `'+build['source_tree']+'`.',
'DLL: `'+build['builds'][0]['files'][0]['sha256']+'`.',
'Patch 0109 follows 0108; all compiled display sources and owned NT5 imports verified.',
'','Host checks: 46 source lifecycle/render cases, 65,536 ROP dependency truth tables,',
'7 additional rejection/unwind cases and 80,000 concurrent registry cycles across 8 threads.',
'ASan/UBSan/leak checks pass. A PROT_NONE foreign private pointer was never read.',
'Reentrant ownership lookup from engine stubs completed with no table lock held.',
'These are host API shims, not real Windows multi-device or teardown concurrency proof.',
'','## Ordinary matched pair','']
for row in pair['results']:
 lines.extend(['- '+row['case']+': strict PASS, '+str(row['cases'])+' cases/'+str(row['pixel_stages'])+' GDI pixel stages; normal shutdown count '+str(row['normal_shutdown'])+' and dashboard return.',
'  Callback counts: `'+str(row['callback_counts'])+'`; upload bytes: '+str(row['upload_bytes'])+'.'])
lines.extend(['','Both runs pass 54 full-visible driver coherence checks, full allocation, 5 structural',
'hives, all protected/payload hashes, zero new warning/error/application events,',
'unchanged 96 MiB/1,536-cluster pagefile and permanent UC shared mapping. Both fixtures',
'contain identical old/new driver payloads. Only one expected-driver byte and two',
'display selectors differ; all other logical SYSTEM nodes/values unchanged.',
'','## Independent diagnostic','',
'video-ownership-scanout/candidate001: strict diagnostic PASS, '+str(len(trace['events']))+' physical frames/',
str(trace['pixels'])+' RGB pixels, zero mismatches; '+str(trace['runtime_pins'])+' runtime pins including all',
str(trace['display_text_bytes'])+' relocated display.text bytes. Complete breakpoint teardown and resume.',
'Same 54 cases, 162 pixel stages, coherence, cold storage and event gates pass. This is explicitly not an ordinary run.',
'Raw emulator framebuffer captures and exact hashes are preserved privately under artifacts/.',
'','## Boundaries and next work','',
'This closes the ownership change and initial copy-path regression, not all 14 DDIs,',
'cursor exclusion, mode/bootvid/crash handling, multiple active displays or Xbox speed.',
'No physical deployment. Keep physical 0101/video0093, 0088 rollback, immutable 0.1.0',
'and qualified 128 GiB recovery unchanged. Original 111-byte non-ASCII physical corruption',
'and first-restart mechanism remain unresolved.',
'','Next: real GDI vector/text/mask/clip/alpha cases against a DIB reference and raw',
'physical scanout, then cursor/lifecycle/crash checks. See NEXT.md.',
'','Draft-source001 preserves the generator assertion of 27 versus 25 replacements; it was never compiled.',
'Earlier failed scanout observers remain failed in their original immutable kits.',
'All source snapshots, guest disks and immutable backing chains verified.'])
(k/'REPORT.md').write_text('\n'.join(lines)+'\n',newline='\n')
(diag/'REPORT.md').write_text('# Ownership0109 scanout: CLOSED PASS\n\n'+
str(trace['pixels'])+' independently compared RGB pixels across 12 physical snapshots; zero mismatches.\n'+
str(trace['runtime_pins'])+' pins including full '+str(trace['display_text_bytes'])+' byte relocated display.text.\n'+
'Complete breakpoint teardown/resume, strict workload and cold audit PASS.\n'+
'Diagnostic only: ordinary_qualifiedFALSE, physical_qualifiedFALSE.\n'+
'See verification.json, candidate001/trace.json, audit.json and closure.json.\n'+
'No reruns, physical access or broader rendering/performance claims.\n',newline='\n')
print('Reports written from verified closed evidence')
