# Unchanged probe provenance

probe.c, artifacts/probe.exe and build-review.json are exact copies of the
already reviewed outputs/video-cache-handoff probe107 inputs. The source and
binary hashes are checked during preparation and preflight. No new probe was
compiled in this kit. The build_script_sha256 inside build-review.json refers
to that historical probe build script, not this kit's driver Build.ps1.

This kit's driver builds are recorded separately in build-report.json,
control001/build.json, candidate001/build.json and pe-review.json. They compile
the same source tree with the shared mapping option OFF/ON. The guest receives
only the corresponding miniport and boot-video override, plus the identical
one-shot drawing probe/startup/trace seed in both children.
