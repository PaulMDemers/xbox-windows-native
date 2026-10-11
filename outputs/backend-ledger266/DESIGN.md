#266 byte-exact observation transport

Use265/DESIGN.md for unchanged compiled renderer/native protocol and its limits.
266 changes only page write/reread to UTF8 bytes, plus distinct attempt paths.
The raw HMP response bytes, including CRLF/ANSI echo, are retained and hashed;
immutable reread compares bytes without text-mode translation. Six tests cover
CRLF, LF, CR, ANSI/quoted response, empty and Unicode text. Five altered responses
are rejected; the original Windows CRLF conversion failure is reproduced.

The source fixture is265's never-executed, readback-verified standalone preparation;
266's runner makes a separate private runtime disk copy. The interrupted265 guest
disk is not a parent. Runtime review asserts the exact narrow host diff and
byte-identical native attestor, discovery, cold audit helpers and renderer binary.
All2013 inherited/new inputs and108 host dependencies are frozen before launch.
Shader actor completion remains UNKNOWN; no retirement/native grant is authorized.
