# Shared Xbox development skill

The versioned [xbox-native-bringup](xbox-native-bringup/SKILL.md) skill captures
native OS/driver validation, FATX lifetime lessons and release/display handoff.
Its installed copy belongs in `~/.codex/skills/xbox-native-bringup`; it is not
specific to this repository's machine address, credentials or private fixtures.

Copy that directory into the shared skills root to install it. Validate with the
skill-creator `scripts/quick_validate.py` helper. Other chats can invoke
`$xbox-native-bringup`; existing chats may need a fresh turn/session to discover
a newly installed skill. The original homebrew-console-dev skill remains the
entry point for ordinary nxdk applications and shared SDK setup.

Versioned references are the maintenance source. Update the installed copy after
reviewing changes. Project-specific evidence remains in the repository reports;
the skill transfers workflows and invariants rather than past PASS claims.
