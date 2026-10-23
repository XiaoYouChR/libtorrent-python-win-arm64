# libtorrent-python-win-arm64

[libtorrent](https://github.com/arvidn/libtorrent) Python wheels for Windows ARM64, which PyPI does not provide. Used by [Ghost Downloader](https://github.com/XiaoYouChR/Ghost-Downloader-3); build details are in [`scripts/build_libtorrent_wheel.py`](scripts/build_libtorrent_wheel.py).

Like the PyPI `win_amd64` wheels, they need `msvcp140.dll` from the [Visual C++ Redistributable](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist).

## Releases

One wheel per release, tagged `v{libtorrent}-py{python}-{build}`. The build number is also the wheel's build tag and only goes up on rebuilds. Releases are immutable; verify a wheel with `gh release verify-asset <tag> <wheel> -R XiaoYouChR/libtorrent-python-win-arm64`.

## License

Scripts: BSD 3-Clause. The wheels contain libtorrent (BSD 3-Clause), Boost (BSL-1.0), OpenSSL (Apache-2.0), libdatachannel and libjuice (MPL-2.0), usrsctp (BSD 3-Clause), plog and nlohmann/json (MIT).
