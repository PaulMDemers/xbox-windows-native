# Private HD staging overlay assembled

D:/Codex-archive/xbox-windows-native/hd-staging325/xwn-hd-staging325.zip contains21 entries: six matched720p files, six matched1080i files, six incoming baseline recovery files, instructions, manifest and qualification record. Every ZIP entry was decompressed and compared byte-for-byte to its expected content; the archive hash is recorded in bundle.json.

Both physical workload scopes pass, but1080i visual confirmation is pending and Ftdisk49 remains a strict failure. This archive is explicitly staging-only; no0.2.0 tag, release publication, installation or hardware write was performed. It targets the existing qualified demo rather than an arbitrary Xbox or an original0.1.0 installation.

The two existing private256 system/boot recovery archives were rehashed against their prior records and referenced without recapture or modification. The small overlay is not a new full-system image or a tested full restore. The builder's own hash and usage-document hash are included alongside the base Git revision, so uncommitted packaging source is not falsely attributed to that earlier revision.
