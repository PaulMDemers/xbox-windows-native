# Test843 reached the Windows 2000 desktop with working mouse input

The user confirmed the desktop and mouse are working on the physical Xbox 1.6. The mouse was connected before launch. This is the second desktop boot with the fixed 720p profile, following a fresh restoration of the baseline registry for 843.

843 remains open at the desktop. Next, request Shut down from Windows and record the observed final screen or power state. After power-off, turn the Xbox on to UnleashX, authenticate the dashboard independently, then collect once with physical004.py and audit the cold files. No hook or owned host runtime. See outputs/boot720-input843/desktop-input001.json.

# Test843 launched once: waiting for desktop and mouse input

Single SITE accepted 2026-10-30T17:07:27.515955+00:00. Mouse left connected before boot per user. Preparation 6c4188b7 pushed. Windows expected to stay running; desktop, input and shutdown not yet verified. No hook or owned host runtime. Do not retry or collect while running. Use physical004.py only. Once at desktop, user can move mouse and open Start to test both movement and click. If ineffective, leave Windows running and report exactly what is visible; if successful, normal Windows shutdown and independent dashboard authentication are the next separate checks. Test842 remains CLOSED, with unclean dashboard return.

843 staged with nine owned files read back byte-for-byte; all ten installed critical hashes match the working baseline. Build003 refused a transcription change in the expected SDK ID before invoking make; failure preserved. Build004 used the verified original SDK ID and passed. Use physical004.py only. All 13 diskless CPU fixtures closed. No startup hook. No SITE sent at staging.

# Test843: fixed 720p boot with mouse connected at launch

Fresh source-only reproduction of the successful 842 profile. Only attempt identifiers, diagnostics and owned paths changed. No USB, display, startup or mode-setting change. Five immutable primary hives and matching logs were verified against the installed package; preimages preserved privately. The prior post-desktop trace and SetupAPI delta remain preserved. This is a fresh baseline boot, not persistence validation.

842 is CLOSED. Dashboard authenticated; no hook. Use physical004.py for unique /E/Applications/XWN16Boot843 only. Stage/readback, verify exact Git bytes, commit/push, one bounded SITE; never retry accepted/uncertain launch. Observe desktop and test cursor movement/Start button. Leave Windows running until input is established; if it works, request ordinary Windows shutdown to qualify that separate milestone. Do not infer return, shutdown, or USB success from a timeout. No unrelated historical probes or automation.
