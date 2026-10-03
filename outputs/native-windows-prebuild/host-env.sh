#!/usr/bin/env bash
# Source in a task shell only. Does not change global PATH or compiler defaults.
export XWN_ROOT=/home/paul/xbox-windows-native
export PATH="$XWN_ROOT/host-deps/bin:$XWN_ROOT/host-deps/root/usr/bin:$PATH"
export PERL5LIB="$XWN_ROOT/host-deps/root/usr/share/texinfo:$XWN_ROOT/host-deps/root/usr/share/perl5:$XWN_ROOT/host-deps/root/usr/lib/x86_64-linux-gnu/perl5/5.40:$XWN_ROOT/host-deps/root/usr/lib/x86_64-linux-gnu/texinfo${PERL5LIB:+:$PERL5LIB}"
export TEXINFO_XS=omit
# Use the installed matching host compiler pair to bootstrap RosBE.
# These host compilers do not generate the Windows loader itself.
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++
