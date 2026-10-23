#!/usr/bin/env python3
"""Build the libtorrent win_arm64 wheel from the upstream tag.

PyPI has no win_arm64 wheel. OpenSSL follows the upstream tag's own
cibuildwheel config, so the wheel matches the x64 one on PyPI. Boost uses the
latest release instead of the upstream one, because the windows-11-arm runner
only has Visual Studio 2026, and b2 knows it since Boost 1.91.

Usage:
    python scripts/build_libtorrent_wheel.py <libtorrent version> <python version> <output folder>
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

UPSTREAM = "https://github.com/arvidn/libtorrent.git"
BOOST = "https://github.com/boostorg/boost.git"
# 上游 pyproject 写死了这两个路径
BOOST_FOLDER = Path(r"C:\boost")
OPENSSL_FOLDER = Path(r"C:\Program Files\OpenSSL")


def run(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    subprocess.run(args, cwd=cwd, env=env, check=True)


def fetchLatestBoostVersion() -> str:
    tags = subprocess.run(("git", "ls-remote", "--tags", "--refs", BOOST, "boost-*"),
                          capture_output=True, text=True, check=True).stdout
    versions = re.findall(r"refs/tags/boost-(\d+\.\d+\.\d+)$", tags, re.MULTILINE)
    return max(versions, key=lambda v: tuple(map(int, v.split("."))))


def installBoost(version: str) -> None:
    archive = Path(os.environ["RUNNER_TEMP"]) / "boost.tar.gz"
    run("curl", "-L", "-o", str(archive),
        f"https://archives.boost.io/release/{version}/source/boost_{version.replace('.', '_')}.tar.gz")
    BOOST_FOLDER.mkdir(exist_ok=True)
    run("tar", "-xzf", str(archive), "-C", str(BOOST_FOLDER), "--strip-components", "1")
    # 上游的 bootstrap.sh 会编出 x64 的 b2，b2 再把所有东西编成 x64
    run("cmd", "/c", "bootstrap.bat", cwd=BOOST_FOLDER)
    run(str(BOOST_FOLDER / "b2.exe"), "headers", cwd=BOOST_FOLDER)


def main() -> None:
    version, pythonVersion, outputFolder = sys.argv[1:]
    source = Path(os.environ["RUNNER_TEMP"]) / "libtorrent"

    run("git", "clone", "--depth=1", f"--branch=v{version}",
        "--recurse-submodules", "--shallow-submodules", UPSTREAM, str(source))
    libdatachannel = source / "deps" / "libdatachannel"
    run("git", "apply", "../patch-libdatachannel-32bit-builds.patch", cwd=libdatachannel)
    # 让 libdatachannel 能用 VS 2026 编译
    run("git", "apply", str(Path(__file__).with_name("patch-libdatachannel-vs2026.patch").resolve()), cwd=libdatachannel)

    run("vcpkg", "install", "--triplet=arm64-windows-static", cwd=source / "tools")
    shutil.rmtree(OPENSSL_FOLDER, ignore_errors=True)
    run("cmd", "/c", "mklink", "/J", str(OPENSSL_FOLDER),
        str(source / "tools" / "vcpkg_installed" / "arm64-windows-static"))

    installBoost(fetchLatestBoostVersion())

    env = os.environ | {
        "CIBW_BUILD": f"cp{pythonVersion.replace('.', '')}-win_arm64",
        "CIBW_ARCHS_WINDOWS": "ARM64",
        "CIBW_TEST_SKIP": "*",
        # delvewheel 改名后的 msvcp140.dll 加载不到，上游 x64 wheel 也不修复
        "CIBW_REPAIR_WHEEL_COMMAND_WINDOWS": "",
    }
    run("uvx", "cibuildwheel", "--output-dir", str(Path(outputFolder).resolve()), cwd=source, env=env)


if __name__ == "__main__":
    main()
