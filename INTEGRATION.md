# Integrating image-simprints

These are instructions for wiring the package into an app, written for a coding
agent such as Claude Code. There are two call sites. The creator side runs once,
when a work is declared. The verifier side runs when an image is checked, and
calls `match` on each candidate the index returns.

## 0. Install

Add `image-simprints` to the app's dependencies, from this repository or a built
wheel. It pins `numpy==2.5.1`, `opencv-python-headless==5.0.0.93` and
`pillow==12.3.0`. Keep those pins: codes are compared bit by bit, so all creator
and verifier codes should come from the same versions. If the app already
depends on `opencv-python` (with GUI), replace it with the headless build; the
two conflict.

## 1. Creator side, at declaration

```python
from image_simprints import ImageError, generate

try:
    simprint = generate(upload_bytes, "creator")   # bytes, a path, or an RGB uint8 numpy frame
except ImageError as e:
    return reject(f"Image could not be read: {e}")
if not simprint["codes"]:
    return reject(simprint["reason"])              # e.g. too small, or no detail (a flat graphic)
store(declaration_id, simprint)                    # the whole dict, as JSON (about 3 KB)
index_codes(declaration_id, simprint["codes"])     # see 3
```

- Store the whole result, including `recipe_version` and `prepared_size`.
  `match` needs both.
- Never mix recipe versions. Filter stored codes by `recipe_version` before
  matching, or re-generate them when the version changes.
- For video, decode frames yourself (for example with `cv2.VideoCapture`),
  convert BGR to RGB, and pass each frame as a numpy array.

## 2. Verifier side

```python
from image_simprints import generate, match

query = generate(image_bytes, "verifier")
hits = []
for declaration_id in candidates_from_index(query["codes"]):        # see 3
    result = match(query, load_simprint(declaration_id))
    if result["relationship"] != "none":
        hits.append((declaration_id, result))
hits.sort(key=lambda h: -h[1]["agreeing_codes"])
```

`relationship` is from the verifier's point of view:

| value | meaning |
| --- | --- |
| `identical` | same picture: each image covers at least 95% of the other |
| `contained_in` | the checked image is a part of the declared one (a crop) |
| `contains` | the declared image is inside the checked one (a collage, a page) |
| `overlapping` | they share a region, neither contains the other |
| `none` | no evidence of shared content |

`overlap_fraction.verifier` and `overlap_fraction.candidate` give the share of
each image that the other covers.

## 3. The index (the app's job)

`match` compares two images. It does not search. The app needs an index that
turns the verifier's codes into a short list of candidate declarations.

- **Simplest, up to roughly 10⁵ declarations**: keep all creator codes in
  memory as one `(n, 4)` uint64 array with an owner column. Compute Hamming
  distances to the query codes and take every owner with a code within
  `tolerance_t` (24). `image_simprints.recipe.hamming`, `parse` and `votes` do
  this batched (see `false_matches` in `testmode.py`).
- **Larger**: split each 256-bit code into 16 bands of 16 bits. Index every
  band value exactly, as `(band number, value) → declaration ids`. Candidates
  are the declarations sharing at least one band with any query code. This is
  the research's banded index. It loses some recall compared with a full scan,
  so measure it on your data.

Either way, a candidate needs at least `min_votes` (2) agreeing codes to
match, so you can drop owners with only one code hit before calling `match`.

## 4. Operations

- **Threads**: `generate` and `match` keep no state between calls and are safe
  in threads and in long-lived processes. They are CPU-bound, so use a process
  pool for throughput.
- **Cost**: `generate` takes a few hundred ms per image, mostly decoding and
  SIFT, and more for very large files. `match` takes about 1–2 ms per pair.
  `image-simprints test` measures both on your hardware.
- **Errors**: unreadable, truncated or unsupported files raise `ImageError`, a
  subclass of `ValueError`. A missing path raises `FileNotFoundError`. A wrong
  source type raises `TypeError`. Bad settings, an unknown role, or codes from
  another recipe raise `ValueError`.
- **Limits**: flat graphics, line art and very small images may yield few or
  no codes. The default creator keeps 20 codes, so small crops and small
  collage inserts (under about 30% of the area) are often missed. Raising
  `creator_codes` to 50 finds more, at more storage and index load. Run test
  mode on your own images before choosing.
