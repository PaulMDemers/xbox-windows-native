# Unattended handling of known hardware wizards:201 planning only

Human asks why benchmark waits for cancelled wizards and whether they can be
ignored for end-to-end testing. No newhelper/driver/settings/policy implemented,
compiled, deployed or launched here. Finish unchanged200 OFF/ON pair first.

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
