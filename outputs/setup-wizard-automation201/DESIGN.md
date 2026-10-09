# Current design: verified normal Cancel button, with genuine completion gates

Build006 sends BM_CLICK to the actual Cancel BUTTON after held process identity,
full whitelisted command, welcome-page text, parent/button ownership, enabled state
and active/foreground state are revalidated immediately after logging. It never
activates a dialog. Physical mode allows only four recorded exact instances and
excludes QEMU target5; DevInstallUiOnly and unknown commands/pages remain manual.
One action per process creation lifetime, eight actions/120 seconds, bounded reads
and sends, 1MiB CREATE_NEW log. Unknown or failed operations remain failures.

Guardian requires joined helper0, continuous five-second actual queue idle and a
final query, then requests normal restart without force flags. New hardware test
changes only own helpers/backups and temporary startup; normal startup restored
FIRST on collection. No permanent PnP/device/driver/registry changes. Welcome or
unfamiliar dialogs and benchmark visibility are separate issues. Two fresh cold
emulator lifecycles passed; physical201 single launch accepted20:14:28UTC October9,
observer38963 active. Whole-boot event qualification remains separate and strict.

# Earlier design/evidence (historical)

# Unattended handling of known hardware wizards:201 implementation and passive validation

Human authorizes targeted cancellation for end-to-end testing. Build001 helper
compiled and actual owned NT5 import review passed;237 policy adversaries passed
ASan/UBSan. Only passive observe001 launched in a fresh owned immutable188 child.
No Cancel action or physical201 deployment yet; physical200 remains unchanged.
Static/import/host results are not UI or lifecycle qualification. Preliminary
PowerShell parser and incorrect host freeze environment refusals are preserved;
neither reached resources or a guest launch. Passive runtime/cold result pending.

The helper uses PSM_PRESSBUTTON/PSBTN_CANCEL, the property sheet Cancel path.
A send acknowledgment alone never proves cancellation. Hold and revalidate the
original process object/creation time/full instance command, current window and
actual enabled Cancel before sending; then await closure and real queue idle.
No repeated action for the same process lifetime. Eight-action/120-second total
bounds and a 1MiB write-through log cap apply. Pure host policy tests do not
exercise window reuse, Windows message behavior or queue completion.
Reference: https://learn.microsoft.com/windows/desktop/Controls/psm-pressbutton
Modern API minimum metadata is not proof of NT5 runtime behavior.

Current194compiled guard waits up to900000ms for observed5000ms installeridle,
records actual zero/pending258 status, queries around each sample/checkpoint and
again before normal restart.200control actual wait80505ms included pending258,
then5100ms observedidle. Five samples had zero boundaryqueries and304564-byte
identical actualSetupAPI measurementbookends. No measurementevents; wholeboot
Ft49 remains strictfailure. The wait is our deliberate measurement/lifecycle
protocol; Windows can run applications while these dialogs remain active.

Microsoft documents CMP_WaitNoPendingInstallEvents as testing pendingPnP activity,
including activeFoundNewHardwareWizard. ModernCM docs cite an internalPnP event
and immediate state, not a guarantee against futureinstalls. Modernrequirements
sayXP; actualownedNT5 setupapi export/import pins and194/189/200 runtime are our
Windows2000 availability/behavior evidence, not those modernrequirements.
Sources: https://learn.microsoft.com/en-us/windows-hardware/drivers/install/checking-for-in-progress-installations
and https://learn.microsoft.com/en-us/windows/win32/api/cfgmgr32/nf-cfgmgr32-cm_waitnopendinginstallevents

Physical188/189 actual read-only observer proved queueactivity and ownerprocess.
189 initial rundll32 newdev.dll,DevInstallUiOnly1812 placeholder had titleFoundNew
Hardware/class#32770, transientstaticcontrols and no recordedCancelbutton. Later
actualaudio01B0 installer appeared. SetupAPI separately records actual01B0/01B4/
01C1/USBffff:ffff DevInstall commands and no-compatible-driver0xe0000228. Human
cancelled/no-driver searches, but identical prompts recurrednextboot with unchanged
PCIEnum state. This is currentbootqueue handling, not durabledevicesupport.
USBffff:ffff function not positively identified; nevercall it gamepad support.

Proposed NEW helper must inventory actualtop-level/childwindows, PID/owner,
processimage/command and supportedbutton identity in freshownedemulator before
sendinganything. Reuse bounded188 read-only inventory first. Onlya verified real
NewDevwizard for exactwhitelistedunsupportedinstance and enabledactualCancel
control is eligible. SkipDevInstallUiOnly transientplaceholder. Displaytitlealone
or genericPCIDevice label cannot authorize cancellation. Rejectunknownwizard,
unknownPID/instance/processbinary, changed/reusedHWND or inconsistentcontrols.
Do not killrundll32/processes, clickNext/Finish/install, disabledevices, stage
nullINFs, changeConfigFlags, suppresswarnings or declarependingasidle.

After observedmatchingCancel action, awaitwindowclosureandactualinstalleridle.
Recordbefore/action/after and newSetupAPI/eventbytes, boundedretries/totalwait,
no repeatedaction againstreusedwindow. Unexpectedinstall/errorrequiresmanual
attention; successfulUIautomationdoesnotwaiveevent/storage/pixelgates. Helper
muststop/join beforemeasurement, retain194idle/boundary/restartguardunmodified.
Firsttest success/noaction on exactmatching dialogs and rejectunrelateddialogs,
missingCancel, staleHWND, wrongdevice/PID, disabledbutton, pendingwithoutwizard,
queuechainandtimeout. Ordinarycoldhive/allocation/protected/events/startup plus
normalshutdown qualifyfixture; debuggerUIobservationseparate. EmulatorQEMUdevice
policy explicitlyemulator-only, notphysicalwhitelist. Onlythen NEWphysicaltrial
withfreshrollback andactualmanual/automationstatecompared. No changesinside200pair.

A later durablecorrectdevicebinding is separateconfiguration/support work. New
Windows SuppressNewHWUI registrysettings mustnotbeassumedvalidonWindows2000;
blankethidingUIwouldnotprovethatqueuehascompleted. Verifiedtargetedcancellation
is the closest automation of human behavior with minimalpolicychange.
