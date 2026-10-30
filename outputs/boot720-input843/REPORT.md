# Test843 closed after manual restart

Windows 2000 desktop and mouse worked with the mouse connected before boot. The console stayed on the shutdown screen and the user restarted it. UnleashX authenticated and collection and cold audit completed once. Console left at the dashboard. No hook or owned host processes. No relaunch, recollection or runtime parenting of 843.

The 14,266 new SetupAPI bytes confirm HID mouse installation, completed OpenHCD installation for instance ending in 10 and full installation started for instance ending in 18. The second completion line is absent. Both persisted instances have the openhci service and driver class binding. All five primary hives were readable through a full offline key/value walk. System event 403 (EventLog 6006) records the event service stopping. Physical power-off did not complete. The final SetupAPI entry does not establish the shutdown blocker.

For the next shutdown investigation, distinguish pending device installation from a later power-off stall. A fresh owned run should record the pending-install state and second controller's live status before shutdown, then record the last shutdown stage reached. Keep the fixed 720p boot profile. See shutdown-analysis001.json, registry-cold001.json and closed001.json.

# Test843 shutdown requested, dashboard return pending

The user initiated shutdown after confirming desktop and mouse operation. The photograph shows the Found New Hardware banner for the Standard OpenHCD PCI to USB Host Controller. The user reports force-ending the banner with no interactive setup wizard seen. Shutdown completion and the cause of the apparent stall are unresolved. A dashboard check timed out. The photo is retained privately and identified in shutdown-screen001.json.

Await the user's power outcome. If Windows remains stalled, use the power button off/on, then independently authenticate UnleashX. No hook was installed. Collect once via physical004.py, audit the cold files, and compare SetupAPI and system event history to the end of the retained 842 logs. The 843 preflight restored primary hives and their transaction logs. It left the earlier SetupAPI and event history in place.

# Test843 reached the Windows 2000 desktop with working mouse input

The user confirmed the desktop and mouse are working on the physical Xbox 1.6. The mouse was connected before launch. This is the second desktop boot with the fixed 720p profile, following a fresh restoration of the baseline registry for 843.

843 remains open at the desktop. Next, request Shut down from Windows and record the observed final screen or power state. After power-off, turn the Xbox on to UnleashX, authenticate the dashboard independently, then collect once with physical004.py and audit the cold files. No hook or owned host runtime. See outputs/boot720-input843/desktop-input001.json.

# Test843 launched once: waiting for desktop and mouse input

Single SITE accepted 2026-10-30T17:07:27.515955+00:00. Mouse left connected before boot per user. Preparation 6c4188b7 pushed. Windows expected to stay running; desktop, input and shutdown not yet verified. No hook or owned host runtime. Do not retry or collect while running. Use physical004.py only. Once at desktop, user can move mouse and open Start to test both movement and click. If ineffective, leave Windows running and report exactly what is visible; if successful, normal Windows shutdown and independent dashboard authentication are the next separate checks. Test842 remains CLOSED, with unclean dashboard return.

843 staged with nine owned files read back byte-for-byte; all ten installed critical hashes match the working baseline. Build003 refused a transcription change in the expected SDK ID before invoking make; failure preserved. Build004 used the verified original SDK ID and passed. Use physical004.py only. All 13 diskless CPU fixtures closed. No startup hook. No SITE sent at staging.

# Test843: fixed 720p boot with mouse connected at launch

Fresh source-only reproduction of the successful 842 profile. Only attempt identifiers, diagnostics and owned paths changed. No USB, display, startup or mode-setting change. Five immutable primary hives and matching logs were verified against the installed package; preimages preserved privately. The prior post-desktop trace and SetupAPI delta remain preserved. This is a fresh baseline boot, not persistence validation.

842 is CLOSED. Dashboard authenticated; no hook. Use physical004.py for unique /E/Applications/XWN16Boot843 only. Stage/readback, verify exact Git bytes, commit/push, one bounded SITE; never retry accepted/uncertain launch. Observe desktop and test cursor movement/Start button. Leave Windows running until input is established; if it works, request ordinary Windows shutdown to qualify that separate milestone. Do not infer return, shutdown, or USB success from a timeout. No unrelated historical probes or automation.
