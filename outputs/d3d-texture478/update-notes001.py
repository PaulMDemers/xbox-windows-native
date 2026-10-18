"""Prepend current closure without normalizing historical continuation bytes."""
from pathlib import Path
W=Path(__file__).resolve().parents[2]
header='''# Current: 479 PC and478 Xbox scoped D3D7 texture PASS, closed;477 failure preserved

Read outputs/d3d-texture477,478,479 REPORT/DESIGN/NEXT/final-review and actual
records. New work commit/push pending final repository/stage checks. Previous
pushed0d05d913. All owned processes CLOSED:477runtime72092/cold34007,3264;
479runtime3068/cold72913,57419/actual62361;478stage36858/launchobserver58932,
collection synchronous/module read closed/actual74139. Console at UnleashX,
no next test queued. 478hook removed FIRST to E:/xwn478-kit/startup-used.cmd;
original6240launcher/da47startup/protected720p unchanged. ConsoleC untouched.
Never relaunch/recollect/parent these cases. Next unused experiment480.

New public texture.c/cmd and graphics_texture.py, build --sample texture.
Same sample PC/Xbox20398B SHA0cf77cd741d0f066ee5a3fc4ad10508f3e6d8cb962c8a89c90fc19d6ee832f91.
Both default/HEL actualRGBsoftware devices enumerate10formats, selectRGB32.
Owned8x8 texture64distinct colors renders point/clamp/no mip into64x64RAMtarget.
Per case4096clear/576safe interior/1071exterior RGBchecks;2449boundarypaletteonly.
256sourcebytes unchanged afterdraw,8captures66560rawB/control. Exactedges/Xbyte
unqualified. Actual11module snapshots/PEimagesizes match cold bytes. NoGPU,
presentation/depth/blend/performance/game claim, no driver/sharedSDK change.
3synthetic tests/8704pixel-source mutations; eachactualcontrol18288metadata/pixel
negatives rejected. No expected pixels changed afterruntime.

479fresh404child (not477parent): valid1474560Bfloppy independently decoded twice,
66clusters/2exactEXEs;39hostnegatives includeactual477badlength.148frozeninputs
archived,29independentNTFSfiles agree. Cold6489files309dirs,5hivesclean/rawagreement,
protectedbinaries/source/floppy exact. NormalrestartQEMUexit0/nohostquit/deadline.
Selectedeventdelta noerror/warning only, NOT wholesystemqualification. No full
NTFSallocationaudit; inheritedSOFTWARE DRMtype1004 limitation retained.

478singlephysical accepted03:32:58UTC ->dashboard03:34:25UTC2026-10-18.
Bothprocess0/completed2/normalrestartprivilege+request1/fresh6006. Five beforeafter
hivesclean/header/rawagreement;10DLLpins prelaunch anddouble-read after. New
system614..620:Ft49,6009,6005,Tcpip4201,2xPopup26 rundll32DLLinitializationfailed
becausewindowstationshuttingdown,6006. InitiatingcommandUNKNOWN. No appdelta.
StrictFALSE. No fullFATXscan (latest463). Historicalbootintermittency UNRESOLVED.
BootSHA15f27b3927d7df281c7536c3bae38b34c0df0948b233826a517043d1e2de3ae3
namespace-only471child/Windows payloadBYTEEXACT.104actualwrapperMODELEDkernel/IO,
8actualdispatcherMODELEDFTPpaths,171records37truncations;34frozeninputs archived;
176actualprimarytruncations reject. Preparationphase6alone nothandoffproof.

477failed BEFORE sample execution: unrestricted477namespace replacement changed
1474560->1477560floppysize; WindowsDIRA:empty, noxwn477resultnamespace. Manually
normalWindowsSecurityRestart, QEMUexit0/nohostquit/deadline; cold6475files308dirs,
shutdowncount+1/source+badfloppyunchanged. Allinputs/UIjournals preserved. Explicit
20mskeyholds/200msspacing added duringdiagnosis, notprovedcausal anddidnotfixmedia.
479uses token-bounded substitution andnewfloppyvalidator. Neverrepair/rerun477.
478prepare-kit001 reviewanchor miss preserved beforebuild/deploy;002 completed,
unexecuted dependencyadvancedto479. No oldfailure requalification.

NEXT separate depth thenalpha-blend rung08b: actual enumerated depthformats,
fixedoverlap/order/referencepixels, ownedresources, completecleanup/unsupported
refusals, hostnegativechecks thenfreshPC anddistinctXbox. No repeatedtexture-only
boot. Presentation/transforms/scenestability later, noGPUdriver/gameclaim.
Preserve allhistoric failures/rollbacks/Ft49/recovery256. 720p baseline,1080i paused.
Public build/run/check docs updated. C24349065216B,E21499871232B atcloseout;
20GiBprojectedreserve, newprivateartifactsC/WSL, no offload/backingmove/deletion.
Historicaluntracked files untouched. All owned guest/build/host/review processes
closed; finalrepo/exactstagecheck andcommit/push follow.

'''
p=W/'outputs/engineering-notes/CONTINUATION.md';old=p.read_bytes();assert not old.startswith(header.splitlines()[0].encode());p.write_bytes(header.encode()+old)
status='''# Latest: D3D7 software textures pass on PC and Xbox

Rung08a now passes default and HEL texture upload, unchanged source readback,
orientation and point-sampling checks on Windows2000 PC479 and Xbox478. Both
use the same binary and fixed oracle; both restart normally. No GPU acceleration,
depth/blending, D3D presentation, game compatibility or performance qualification.

The Xbox is at UnleashX with the temporary hook removed. Normal launcher/startup
and720p configuration are unchanged. Ftdisk49 and two shutdown-time rundll32
initialization popups keep overall qualification FALSE; their initiating command
and historical boot intermittency remain unresolved. No full FATX scan repeated.

477 is a preserved failed PC attempt: namespace generation corrupted the floppy
size, so the sample did not run. New479 uses bounded naming and an independent
FAT12 preflight. No repair/relaunch of477. Build/run/check docs and source are
updated. Next: separate depth and alpha-blending controls, PC first then Xbox.

All owned processes are closed and no hardware test is queued. Final repository
check, exact staged-byte verification and commit/push follow this status update.

'''
p=W/'outputs/engineering-notes/STATUS.md';p.write_bytes(status.encode()+p.read_bytes())
