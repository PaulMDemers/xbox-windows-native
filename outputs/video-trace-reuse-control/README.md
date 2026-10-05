# Original miniport shutdown control

One emulator boot of the untouched v0.1.0 miniport with a clean valid diagnostic seed and the exact settled runner/probe used in video-trace-reuse-settled. No hardware access. This isolates whether the shutdown-time rundll32 popup also exists without candidate0093. The original candidate strict audits remain unchanged.

Result: PASS. One normal boot, four pixel checks, five timing loops, normal restart, EventLog6006, unchanged payloads and no new application popup. This single control does not reproduce candidate0093 shutdown popups; it does not prove causality or eliminate timing variability.
