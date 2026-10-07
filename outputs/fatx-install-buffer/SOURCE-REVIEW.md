# Review of emulator-only capture tools

The runners require a fresh attempt directory, pinned emulator/seed hashes and
completed allocation preflight. Local FTP is fixed to127.0.0.1:4596. Preparation
makes a new backing overlay; it does not edit the immutable guest input. Cold
collection requires owned cleanup and adopts each already-recorded stage.

Trace changes retain exact prior sources per attempt. Arguments/buffers are
bounded, live instruction bytes checked, buffers SHA256-addressed, incomplete
pairing/read failures retained. The finally path attempts breakpoint removal and
resume; setup-buffer001 records its cleanup failure honestly after runner exit.
That concurrency gap is corrected in the subsequent target-buffer supervisor,
which waits for tracer termination before allowing normal teardown.

The copied audit pipeline is unchanged except for diagnostic classification,
fixture paths and mode lookup. It checks log alignment independently of capture
coverage. No clean-cold result is promoted to ordinary or physical qualification.
Raw buffer contents and oversized unfiltered trace metadata stay local. The
versioned summaries/analyses retain hashes, counts and failure classifications.

verify-evidence.py checks source/site/trace hashes, every preserved buffer,
collection-stage hashes and staged bytes. Repository checks exclude binaries,
private media and credential patterns. No filesystem driver was modified.
