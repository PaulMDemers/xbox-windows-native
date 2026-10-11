# Source and reproducible build inputs

The separate corresponding-source archive contains the complete ReactOS0016
source tree, including its original licenses, plus cumulative0210. It contains
no Windows installation, BIOS, disk image, keys or supplied NT5 provider DLLs.
The source tree ID is5c302cf16ce08e7f2748be580e3d2e60d7d2441b; the upstream starting
commit isafc0127e8f937ab68503d715d948844973756aa1. Source-build004.json records the
final AC97 source hashes and resulting candidate binary hash.

Extract reactos0016.tar.gz into a new owned directory and apply only
0210-waveonly-cumulative.patch with git apply. Do not apply0207/0208/0209 as well.
Those older experiments, including failures, are retained in the private branch
for review. The complete0016 archive already includes the historical native-NT5
source series; do not apply that historical series twice.

Use the pinned RosBE2.2.1 i386 toolchain. Toolchain-observed001.json records the
actual compiler, C++ compiler, linker and assembler hashes used here. The original
toolchain is not included or modified by this package. In the RosBE environment,
configure a separate build directory with the following settings, replacing only
the owned source/build paths:

```sh
cmake -S SOURCE -B BUILD -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=SOURCE/toolchain-gcc.cmake \
  -DARCH=i386 -DSARCH=xbox -DOARCH=pentium -DCMAKE_BUILD_TYPE=Release \
  -DPCH=OFF -DENABLE_CCACHE=OFF -DXBOX_NT5_HAL=ON \
  -DXBOX_NATIVE_PREFLIGHT=OFF -DXBOX_NATIVE_IO_PREFLIGHT=OFF
cmake --build BUILD --target ac97xnt5 ac97 -- -j4
```

The experimental package renames the ac97xnt5.sys output to xwnaci207.sys without
changing its bytes. The normal ac97 target is a compile check, not a hardware
qualification. Both names in source-build004.json distinguish these outputs.
Native imports were checked against the user's actual NT5 files; those proprietary
provider binaries are not redistributed. Rebuilding requires separate validation,
and tool timestamps may prevent a byte-identical result without reproducing the
entire build environment. Do not substitute a rebuilt file into a frozen trial.

Helper source and its setup/restart policy headers accompany the source bundle.
Build-State.ps1, Build-Install.ps1 and Build-HardwareRunners001.ps1 show the exact
compiler/linker flags. They preserve failures and require fresh output paths;
adapt owned paths in a new copy, never rerun them over retained experiment output.
The physical runners differ only by selecting /cancel-physical instead of
/cancel-emulator. Host import checks and that exact source comparison are recorded;
physical execution is untested.

The edited AC97 directory carries Microsoft's MIT license and historical file
notices. The linked ReactOS stdunk implementation refers to the root GPL2 license;
other runtime/support files retain their own notices and licenses. The combined
binary is not described as wholly MIT. Keep the complete corresponding source,
all source notices and the packaged license texts with any redistribution.
