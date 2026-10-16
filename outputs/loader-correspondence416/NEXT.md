# Ready for an observed direct launch

Read stage001, comparison002, restore-tests001 and actual activation/restore
records before any console operation. Stage001 completed: six loader files plus
owner marker under E:/xwn416-stage, all read back. The active demo is unchanged.
The user has been asked once whether they are near the console for observation.
Do not send a SITE EXEC or infer a boot from staging/FTP availability.

If the user is ready at UnleashX, execute activate.py activate ONCE with the
existing environment credentials. It rechecks ownership/protected files/stage,
uploads and verifies three temporary files, journals each rename, preserves
same-directory originals and verifies the resulting active candidate. It does
not launch. Any failed activation requires inspecting the actual journal and
known-file states; do not simply rerun it. The restore planner covers partial
rename states and refuses unknown bytes.

Then ask the user to launch E:\Applications\XWNEBoot\default.xbe through
UnleashX File Explorer, observe Xromwell and Windows, open
C:\xwndemo407\play.cmd, and normally restart to the dashboard afterward. This
is the same entry/configuration/Windows installation, with only the three
reconstructed loader artifacts temporarily changed. Capture the exact user
observation separately from machine evidence. No scheduled soak/startup change.

On dashboard return run activate.py restore ONCE. It captures event logs and
startup before restoring known originals and readback-checking code/startup.
Preserve candidate files as .416used and private captures; no blind overwrite or
rollback from unknown data. Analyze event deltas using actual pre-run records
before making any clean-runtime claim. A successful observed boot is scoped;
the existing strict event and clean-install namespace failures remain.

If the user is not available, leave the inactive stage and original demo intact.
No hardware experiment is necessary merely to repeat the solved byte comparison.

No old runtime was relaunched/recollected/parented. build001 partial FreeLoader
comparison remains false; build002 is a separate metadata reconstruction. Never
run consumed IDs. No full-install deployment, public tag, source behavior patch
or launch-path rewrite is authorized by a metadata-only correspondence result.
