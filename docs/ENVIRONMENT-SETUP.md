# Fresh build environment setup

Reconstruct the build environment from the project inputs below; an export of
the old WSL distribution is not required. A clean-machine bootstrap has not yet
been verified. [building.md](building.md) describes build behavior and
[BUILD-CURRENT.md](BUILD-CURRENT.md) records component lineage and limits.
Windows media, firmware and private recovery material are separate inputs for
installation or recovery, not compiler dependencies.

## Host prerequisites

On a new Windows host, install WSL and Ubuntu from an elevated PowerShell,
following [Microsoft's WSL instructions](https://learn.microsoft.com/en-us/windows/wsl/install):

```powershell
wsl --list --online
wsl --install -d Ubuntu
```

Restart if prompted and finish Ubuntu's initial user setup. Check the installed
release with `cat /etc/os-release` and WSL version with `wsl --list --verbose`.
The recorded host was Ubuntu 26.04.1 LTS (resolute), x86-64, WSL 2. The
default Ubuntu image may change: use an available 26.04 image if offered and
check the release before expecting the recorded GCC package to match.

Use Linux or WSL 2 and prefer its Linux filesystem for the repository, caches,
toolchain and outputs. The bootstrap requires Python 3.12+ with
`tarfile.data_filter`, Git, GCC/G++, binutils, GNU Make, Texinfo (`makeinfo`),
m4, bzip2, tar, pkg-config, zlib development headers, `find`, `grep`, and
`taskset`. It also requires a `python` command resolving to Python 3; installing
`python3` alone may not supply that alias. Install the equivalent packages with
your distribution's package manager. On Ubuntu, install the build tools and
the nxdk prerequisites with:

```sh
sudo apt-get update
sudo apt-get install ca-certificates findutils grep build-essential git python3 python-is-python3 texinfo m4 bzip2 tar pkg-config zlib1g-dev util-linux gcc-12 gcc-12-multilib clang lld llvm bison flex cmake
git clone https://github.com/PaulMDemers/xbox-windows-native.git "$HOME/xbox-windows-native"
cd "$HOME/xbox-windows-native"
git rev-parse HEAD
git status --short
```

Use the intended repository revision and preserve any local work separately;
the remote's default branch can advance. The script checks prerequisites but
does not install them. Check free space on both the Linux filesystem and the Windows
volume backing the WSL virtual disk. The tools enforce a 20 GiB free-space
reserve; that is not a total build-size estimate.

The observed development host was Ubuntu 26.04.1 LTS with Python 3.14.3,
binutils 2.46, Make 4.4.1 and GCC 12.5.0. Its login shell did not resolve
`python`, so that shell alone does not establish the bootstrap's original PATH.
Distribution and complete package versions are not locked by the repository.
After cloning this repository, run from its root:

```sh
python3 --version
python --version
git --version
gcc --version
g++ --version
make --version
makeinfo --version
pkg-config --exists zlib && echo 'zlib development files found'
command -v as bzip2 find grep m4 tar taskset
```

If `python` is absent, an isolated PATH entry supplies it without changing the
system default. In the same shell that runs the bootstrap:

```sh
mkdir -p "$HOME/.local/xwn-host-bin"
ln -s "$(command -v python3)" "$HOME/.local/xwn-host-bin/python"
export PATH="$HOME/.local/xwn-host-bin:$PATH"
python --version
```

If that link already exists, inspect it before reuse. Record the actual
interpreter and PATH.

## Fetch and bootstrap RosBE

[dependencies.json](../upstream/dependencies.json) pins ReactOS base
`afc0127e8f937ab68503d715d948844973756aa1`, Cromwell base
`9fc54d0c7cbed7bc3c70373642d833684853011f`, and RosBE Unix 2.2.1 archive
SHA-256 `d720c0a77dc08c6da3929fd282de3fe7af6d697b6fb104889a0362e770742565`.
The fetch uses the URLs in that file, checks identities and disables Git
credential helpers. The bootstrap verifies and applies the pinned Ninja Python
compatibility adjustment, then builds RosBE in a private prefix. These paths
must not exist and must be outside the repository. Use new names after failure.

```sh
DEPS="$HOME/xwn-dependencies-001"
BOOTSTRAP="$HOME/xwn-rosbe-001"
python3 tools/setup-dependencies.py fetch --output "$DEPS"
python3 tools/setup-dependencies.py bootstrap --archive "$DEPS/RosBE-Unix-2.2.1.tar.bz2" --output "$BOOTSTRAP"
python3 tools/toolchain_receipt.py --bootstrap "$BOOTSTRAP/bootstrap.json" --output "$BOOTSTRAP/toolchain.json"
```

Keep `fetch.json`, `bootstrap.json`, `bootstrap.log` and `toolchain.json`.
The receipt inventories this local bootstrap; it is not a publisher signature
or evidence of identical historical compiler binaries. The documented
development-host bootstrap and eight component builds passed on a host with
prerequisites and launcher compiler already installed, not a pristine image.

## Reconstruct and build components

Set these variables again in each new shell using the paths actually chosen:

```sh
DEPS="$HOME/xwn-dependencies-001"
BOOTSTRAP="$HOME/xwn-rosbe-001"
ROSBE="$BOOTSTRAP/RosBE-2.2.1"
python3 tools/xwn.py list
python3 tools/xwn.py verify
```

Build each ReactOS profile in a fresh output directory outside the repository,
cache and toolchain. The manifest specifies its overlay, expected tree,
definitions, targets and outputs. These are NT5/ReactOS builds using RosBE's
i686 compiler, separate from nxdk applications.

```sh
for profile in fatx framebuffer loader display audio hal network; do
  python3 tools/xwn.py build --profile "$profile" --cache "$DEPS/reactos" \
    --rosbe "$ROSBE" --toolchain-receipt "$BOOTSTRAP/toolchain.json" \
    --output "$HOME/xwn-build-$profile-001" || break
done
```

The Cromwell launcher checks the resolved GCC 12 executable SHA-256 against
`e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4`.
The development host's matching executable came from Ubuntu's `gcc-12` package
version `12.5.0-9ubuntu1`. Check whether that version is offered, install it and
matching multilib package, and verify the actual executable before building:

```sh
apt-cache policy gcc-12 gcc-12-multilib
sudo apt-get install gcc-12=12.5.0-9ubuntu1 gcc-12-multilib=12.5.0-9ubuntu1
sha256sum "$(readlink -f /usr/bin/gcc-12)"
python3 tools/xwn.py build --profile launcher --cache "$DEPS/cromwell" \
  --gcc12 /usr/bin/gcc-12 --output "$HOME/xwn-build-launcher-001"
```

A package called GCC 12 alone is insufficient. On November 8, 2026, the
[Ubuntu archive package](https://archive.ubuntu.com/ubuntu/pool/universe/g/gcc-12/gcc-12_12.5.0-9ubuntu1_amd64.deb)
was downloaded and checked against apt's SHA-512 metadata. Its compiler,
extracted as a stream, matched the SHA-256 above. This confirms that package's
compiler identity, not a fresh installation or build. If the version is absent
from configured repositories, use the archive package with compatible Ubuntu
dependencies. An attempted `dpkg-deb -x` onto `/mnt/d` failed creating a
symlink; extract packages on the Linux filesystem. If the hash differs, the strict
build refuses it; do not bypass the check or change the pin without a reviewed
toolchain change. The launcher defaults to E/720p. Preserve source and build
records and logs. On a shared machine, coordinate with its existing build
lease. See [building.md](building.md) for the display-preference utility.

## Separate nxdk hardware-report utility

The hardware report is an Xbox XBE, built separately from NT5 components. Use
[nxdk](https://github.com/XboxDev/nxdk) commit
`58427c078b4ccb0121f359b6b6c536b3b2914976` with its pinned submodules and
runtime libraries built for that revision:

```sh
git clone https://github.com/XboxDev/nxdk.git "$HOME/nxdk-xwn"
git -C "$HOME/nxdk-xwn" checkout --detach 58427c078b4ccb0121f359b6b6c536b3b2914976
git -C "$HOME/nxdk-xwn" submodule update --init --recursive
git -C "$HOME/nxdk-xwn" submodule status --recursive
```

The checkout's Dockerfile builds tools and runtime libraries with these commands.
The `activate -s` output sets the nxdk tool wrappers on PATH in the current
shell. The first `make` builds host tools; the second builds SDK libraries:

```sh
cd "$HOME/nxdk-xwn"
make tools -j4
eval "$(./bin/activate -s)"
make NXDK_ONLY=y -j4
cd "$HOME/xbox-windows-native"
mkdir "$HOME/xwn-hardware-report-001"
cp src/utilities/hardware-report/main.c src/utilities/hardware-report/pci_probe.h src/utilities/hardware-report/Makefile "$HOME/xwn-hardware-report-001/"
cd "$HOME/xwn-hardware-report-001"
make NXDK_DIR="$HOME/nxdk-xwn" V=1
```

Outputs are `bin/default.xbe` and `hardware-report.iso`; see
[tester-bundles.md](tester-bundles.md#build-the-hardware-report-xbe). The recorded utility
build used prebuilt SDK libraries; a fresh SDK build has not been validated.
The repository does not pin the nxdk host compiler, package set or SDK output
hashes, so it cannot yet guarantee reproduction of that environment.

## Validation and remaining scope

Record the host distribution and package versions, repository commit, fetched
identities, receipt, commands, logs and artifact hashes. Inspect each output's
`source.json`, `build-command.json` and `build.json` and retain failures.
Compilation is distinct from byte identity and console qualification. Full
clean-machine validation and a pinned and verified fresh nxdk SDK bootstrap
remain open. The component builds do not make a complete OS installer; the
[build-to-boot guide](build-to-boot.md) describes additional inputs and gaps.
