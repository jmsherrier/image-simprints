# image-simprints

[![CI](https://github.com/jmsherrier/image-simprints/actions/workflows/ci.yml/badge.svg)](https://github.com/jmsherrier/image-simprints/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/jmsherrier/image-simprints)](https://github.com/jmsherrier/image-simprints/releases)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](pyproject.toml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![Status: proof of concept](https://img.shields.io/badge/status-proof%20of%20concept-orange)](#status)

Granular image codes. Each image gets a short list of 256-bit codes, one per
distinctive spot (SIFT keypoint). Comparing two lists tells you whether one image
is inside the other, contains it, overlaps it, or is the same picture. This holds
after crops, resizing, re-encoding, colour changes and rotation.

This is a proof of concept for Liccium. It is ported from the bakau research
code. Everything runs on the CPU: no GPU, no network, no model downloads.

<a id="status"></a>**Status:** proof of concept. Recipe 2.1 settles colour profiles (they
are ignored, so a browser decodes the same pixels); the recipe may still change
with further tuning, so treat codes as test data.

On the test split at default settings it finds 97% of re-encoded, resized and
colour-changed copies, 96% of 90% crops, 77% of 50% crops and 76% of pictures
filling half a collage; 67.9% of all modified copies, with no false match
between truly unrelated photos ([report](tests/corpus/report-v2.1/summary.md)).

```sh
pip install git+https://github.com/jmsherrier/image-simprints@v0.1.0   # Python 3.12
pip install .            # from a checkout; numpy, opencv-python-headless, pillow (pinned)
```

```python
from image_simprints import generate, match

# Creator side, at declaration: store this with the declaration.
creator = generate("original.jpg", "creator")      # path, bytes, or an RGB numpy frame

# Verifier side: codes for the image being checked...
verifier = generate("found_online.jpg", "verifier")

# ...compared with each candidate your index returned.
result = match(verifier, creator)
print(result["relationship"], result["overlap_fraction"], result["agreeing_codes"])
```

`generate` returns `{recipe_version, prepared_size: (w, h), codes: [{chunk_idx,
code, x, y, scale, angle}], reason}`. `code` is 64 hex characters, and `x`, `y`
are fractions of the prepared width and height. `reason` explains an empty list,
for example an image that is too small.

`match` returns:
- `relationship`: one of `identical`, `contained_in` (the verifier's image is
  inside the candidate's), `contains`, `overlapping` or `none`.
- `overlap_fraction`: `{verifier, candidate}`, the share of each image the other
  covers.
- `agreeing_codes`: how many codes agreed.

Settings and their defaults: `recipe=2`, `creator_codes=20`, `verifier_codes=64`,
`tolerance_t=24`, `min_votes=2`, `prepared_size=512`, `span_check=0.05`. Each
can be overridden, for example `generate(src, "verifier", {"prepared_size":
1024})`. Overrides are recorded in `recipe_version`. A damaged or unsupported
file raises `image_simprints.ImageError`.

## Test mode

```sh
image-simprints test path/to/originals --unrelated path/to/unrelated --out report
```

Test mode manipulates each original in memory: crops, resizing, JPEG, WebP and
AVIF re-encoding, colour changes, rotation, collages and overlaps. It reports
the match rate per manipulation. It also reports false matches between every
pair of unrelated images, compared offline, and the time per image. It sweeps
`creator_codes` over {10, 20, 50}, `verifier_codes` over {32, 64} and the
verifier's `prepared_size` over {512, 1024}. Output: `report/report.json` and
`report/summary.md`. To test your own modified copies instead, use
`--modified DIR`, with files named `<original stem>__<label>.<ext>`.
`--lookalikes DIR` takes a folder of subfolders. Each subfolder holds different
photos by one photographer, and their false matches are reported separately.
`--verifier-settings '{"candidates": 4096}'` changes settings for the verifier
only.

## Test corpus

[`tests/corpus/manifest.csv`](tests/corpus/manifest.csv) lists 2,618 CC0 and
public-domain photographs from Wikimedia Commons. For each one it gives the page,
the file URL, the licence and a SHA-256. The set is the bakau research
benchmark's test split (150 originals, 400 unrelated photos, 208 look-alikes in
44 sets of photos by one photographer), plus 600 more unrelated photos from the
same Commons category. It also lists the research's tuning split (60 originals,
200 unrelated photos) and 1,000 more unrelated tuning photos; recipe 2 was
fitted on these only. The images are not in the repository. `fetch-corpus`
downloads them and checks every hash; it is the package's only network use.

```sh
image-simprints fetch-corpus      # into .cache/corpus (gitignored)
image-simprints test .cache/corpus/originals --unrelated .cache/corpus/unrelated \
    --lookalikes .cache/corpus/lookalikes
```

At default settings recipe 2.1 finds 67.9% of modified copies (recipe 2:
68.0%, recipe 1: 63.3%), with no false match between truly unrelated photos.
The current report is [`report-v2.1`](tests/corpus/report-v2.1/summary.md); the
other reports in `tests/corpus/` are history (recipes 1 and 2, fits and
experiments).

## Documents

- [RECIPE.md](RECIPE.md): the recipe, precisely enough to reimplement, with
  test vectors.
- [INTEGRATION.md](INTEGRATION.md): how to wire this into an app. Its stop
  codes, an index-side option, guard against images that match too many others.
- [image-simprints-js](https://github.com/jmsherrier/image-simprints-js): the
  recipe in the browser, on a custom OpenCV.js build.

## Tests

```sh
pip install -e ".[test]" && pytest
```

Apache-2.0. © 2026 Joseph Sherrier.
