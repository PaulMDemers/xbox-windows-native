# Next: rung07 software-device creation and pixels

473 is CLOSED: one physical boot, both D3D7 inventories complete, normal restart, hook removed and selected cold audit complete. Never rerun/recollect it. Original720p boot/driver/startup unchanged. Ftdisk49 and historical intermittent boots remain unresolved; do not claim general stability.

Implement an original bounded offscreen D3D7 sample using the actual RGB GUID a4665c60-2673-11cf-a31a-00aa00b93356. Check reported format support, create an owned system-memory render target, CreateDevice, clear and one pretransformed triangle. Explicit viewport/render states; independently verify background and interior reference pixels with predefined edge coverage. Preserve actual HRESULTs, cleanup and failure paths. First qualify against fresh owned NT5 PC, then a distinct Xbox namespace/controller. Extend actual helper-DLL provenance as needed; static imported DLLs do not establish complete loaded-module identity.

Do not bypass the private desktop primary or advertise a HAL. No primary/scanout/GPU ownership, driver replacement, textures, game compatibility or speed claims from inventory. Keep native Windows GPU ownership/PTE/cache/deferred-release work separate. All prior failed boots, refused diagnostics and metadata remain immutable. No console C access or F-warning cleanup.
