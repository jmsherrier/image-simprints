# Third-party notices

image-simprints is Apache-2.0 and does not include the packages below; `pip`
installs them. Versions are the pins in [`pyproject.toml`](pyproject.toml).
Licences are read from the installed packages' metadata and licence files, on
Windows x86-64 with Python 3.12.

## Runtime

| package | version | licence | link |
| --- | --- | --- | --- |
| NumPy | 2.5.1 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | [github.com/numpy/numpy](https://github.com/numpy/numpy) |
| opencv-python-headless | 5.0.0.93 | Apache-2.0 | [github.com/opencv/opencv-python](https://github.com/opencv/opencv-python) |
| OpenCV (inside that package) | 5.0.0 | Apache-2.0 | [github.com/opencv/opencv](https://github.com/opencv/opencv) |
| Pillow | 12.3.0 | MIT-CMU | [github.com/python-pillow/Pillow](https://github.com/python-pillow/Pillow) |

These wheels bundle other libraries under their own licences, which depend on
the platform:

- **NumPy**: OpenBLAS (BSD-3-Clause), LAPACK (BSD-3-Clause-Open-MPI), the GCC
  runtime (GPL-3.0-or-later WITH GCC-exception-3.1). See `numpy-2.5.1.dist-info/licenses/`.
- **opencv-python-headless**: among others FFmpeg (LGPL-2.1, as a separate
  library that image-simprints does not call), libjpeg-turbo, libwebp, libavif,
  aom, OpenJPEG, libtiff, Protobuf and FlatBuffers; more on Linux and macOS. See
  `cv2/LICENSE-3RD-PARTY.txt`.
- **Pillow**: brotli, FreeType, HarfBuzz, littleCMS, libavif, libjpeg-turbo,
  libpng, libwebp, OpenJPEG, libtiff, xz and zlib-ng. See
  `pillow-12.3.0.dist-info/licenses/LICENSE`.

Anyone redistributing these wheels (in a container image or an installer, say)
takes on those licences' terms.

## Tests and build only

| package | version | licence | link |
| --- | --- | --- | --- |
| pytest | 9.2.0 | MIT | [github.com/pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| iniconfig (via pytest) | 2.3.1 | MIT | [github.com/pytest-dev/iniconfig](https://github.com/pytest-dev/iniconfig) |
| packaging (via pytest) | 26.3 | Apache-2.0 OR BSD-2-Clause | [github.com/pypa/packaging](https://github.com/pypa/packaging) |
| pluggy (via pytest) | 1.7.0 | MIT | [github.com/pytest-dev/pluggy](https://github.com/pytest-dev/pluggy) |
| Pygments (via pytest) | 2.21.0 | BSD-2-Clause | [github.com/pygments/pygments](https://github.com/pygments/pygments) |
| colorama (via pytest, Windows) | 0.4.6 | BSD-3-Clause | [github.com/tartley/colorama](https://github.com/tartley/colorama) |
| setuptools (build backend) | >=77 | MIT | [github.com/pypa/setuptools](https://github.com/pypa/setuptools) |

Only pytest is pinned; the packages it pulls in are the versions installed here.

## Test corpus

The photographs are not in this repository and are not redistributed.
[`tests/corpus/manifest.csv`](tests/corpus/manifest.csv) only lists them, with
each one's Wikimedia Commons page, file URL, licence and SHA-256: 2,607 CC0 and
11 under the Public Domain Mark. `fetch-corpus` downloads them from Wikimedia
Commons.

## Patent

SIFT's US patent ([US 6,711,293](https://patents.google.com/patent/US6711293B1/en)) expired in March 2020.
