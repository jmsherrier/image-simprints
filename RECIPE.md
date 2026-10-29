# Recipe `image-simprints/2.1`

This document specifies how to turn an image into codes and how to compare two
sets of codes. It is meant to be enough to reimplement the recipe. The reference
implementation is [`src/image_simprints/recipe.py`](src/image_simprints/recipe.py).
The recipe is ported from the bakau research code
(`research/granular_constraints`, `research/granular_followup`). That research
picked the variant "topf-20 | rootsift256 | m2", with 64 verifier codes and a
span check of 0.05.

Recipe 2 is the default. It differs from recipe 1 (the research's) in one step:
each descriptor is computed at its keypoint's own octave (§5.1), with thresholds
refitted for that (§5). Recipe 1 stays available with the setting `recipe: 1`.
Version 2.1 (and 1.1) ignores embedded colour profiles (§2), so that a browser
can decode the same pixels.

Every operation is one OpenCV.js also has (SIFT needs a custom OpenCV.js build),
or is plain arithmetic.

## 1. Version and settings

| setting | default | used by |
| --- | --- | --- |
| `recipe` | 2 | generate: 2, or 1 for the research's descriptors |
| `creator_codes` | 20 | generate, role `creator`: keep the top N |
| `verifier_codes` | 64 | generate, role `verifier`: keep up to N |
| `prepared_size` | 512 | generate: longer side of the prepared image |
| `tolerance_t` | 24 | match: maximum Hamming distance for two codes to agree |
| `min_votes` | 2 | match: agreeing codes needed on one transform |
| `span_check` | 0.05 | match: minimum spread of the agreeing verifier keypoints |

The version string is `image-simprints/2.1` for recipe 2 and
`image-simprints/1.1` for recipe 1. Each other setting that differs from its
default is appended as `;name=value`, in the order of the table above (for
example `image-simprints/2.1;prepared_size=1024`). `match` refuses
codes of an unknown recipe, and never compares codes of two different recipes.

Fixed constants (not settings): `MIN_SIDE = 32`, `CANDIDATES = 512`,
`SIFT_FEATURES = 1500`, `SIZE_FLOOR = 0.02`, `DETAIL_FLOOR = 200`,
`PATCH_SIDE = 32`, `PATCH_FACTOR = 2`, `SCALE_RANGE = [0.1, 10]`,
`CONTAINED = 0.95`, `BACKGROUND = 255`.

## 2. Decoding

The source is a file path, encoded bytes, or a decoded frame. The output is an
RGB uint8 image. **Colour profiles are ignored**: an embedded ICC profile, or any
other colour-space tag (PNG `gAMA`, `cHRM`, `sRGB`; the primaries and transfer
of CICP), is not applied, and the decoded values are taken as sRGB. In a
browser: `createImageBitmap(blob, {colorSpaceConversion: "none",
imageOrientation: "from-image", premultiplyAlpha: "none"})`, drawn to a canvas.

- **Decoded frame** (for video): uint8, shaped `(h, w)` grey, `(h, w, 3)` RGB or
  `(h, w, 4)` RGBA. The channel order is RGB; convert OpenCV's BGR frames first.
  Grey is copied to all three channels. RGBA is flattened as below. Any other
  dtype or shape is an error.
- **File or bytes**, decoded with Pillow, in this order:
  1. Open the file and decode the **first frame** (animated GIF, PNG, WebP).
     Any decoding failure raises `ImageError`.
  2. Apply the **EXIF orientation** (Pillow `ImageOps.exif_transpose`).
  3. **16-bit grey** (Pillow modes `I;16*`, `I`): clip to 0–65535 and keep the
     high byte (`v >> 8`).
  4. **Transparency** (an alpha channel, or a transparent palette entry or
     colour): convert to RGBA and keep the alpha. Convert the colour to RGB.
  5. Convert to RGB (Pillow `convert("RGB")`). CMYK, profile or not:
     `R = ((255 - C) * (255 - K) + 127) // 255`, and so on for G (M) and B (Y).
  6. **Flatten** the alpha onto white, per channel, in integers:
     `out = (c * a + 255 * (255 - a) + 127) // 255`.

## 3. Preparation

1. **Greyscale**: OpenCV `cvtColor(RGB2GRAY)`. For uint8 this is
   `Y = (4899 R + 9617 G + 1868 B + 8192) >> 14`.
2. **Resize**: if the longer side exceeds `prepared_size`, let
   `f = prepared_size / max(w, h)`. Resize to
   `(max(1, round(w f)), max(1, round(h f)))` using OpenCV `INTER_AREA` (area
   averaging). Here `round` rounds half to even. Images are never upscaled.
3. If the prepared image is under `MIN_SIDE` (32 px) on either side, return no
   codes with the reason `too small`.

`prepared_size = (w, h)` in the output is the size of this prepared image.

## 4. Keypoints

1. **Detect**: OpenCV SIFT with `nfeatures = 1500` and the defaults
   (`nOctaveLayers = 3`, `contrastThreshold = 0.04`, `edgeThreshold = 10`,
   `sigma = 1.6`), on the prepared grey image. Each keypoint becomes a row
   `(x, y, size, angle, response)`. Two keypoints at one point with different
   angles are two rows.
2. **Rank**: sort by response, highest first. Break ties by `y` ascending, then
   `x` ascending. Keep the first `CANDIDATES` (512).
3. **Detail floor**: drop keypoints whose patch detail is below 200 (see below).
4. **Size floor**: drop keypoints with `size < 0.02 * min(w, h)`.
5. **Select**: keep the first N, where N is `creator_codes` or `verifier_codes`
   by role. Creator codes are therefore always a prefix of the verifier codes of
   the same image at the same `prepared_size`. If none remain, return no codes
   with the reason `no keypoints with enough detail`.

**Patch detail.** Build a pyramid: level 0 is the prepared image as float32.
Add `pyrDown` levels while the shorter side of the last level is above 64. For a
keypoint `(x, y, size, angle)`:

```
extent = 2 * size
level  = clamp(floor(log2(max(extent, 1) / 32)), 0, levels - 1)
f      = 2^level ;  sc = extent / f / 32 ;  a = radians(angle)
c, s   = cos(a) * sc, sin(a) * sc ;  cx, cy = x / f, y / f
M      = [[c, -s, cx - 16 c + 16 s],
          [s,  c, cy - 16 s - 16 c]]
patch  = warpAffine(level image, M, (32, 32), INTER_LINEAR | WARP_INVERSE_MAP, BORDER_REFLECT)
```

Let `D[k][n] = 2 cos(pi k (2n + 1) / 64)` for `k < 8, n < 32` (an unnormalised
DCT-II). Compute `L = D · patch · Dᵀ` in float64, an 8×8 block. Take the 63
coefficients after `L[0][0]` (row-major) and call them `ac`. The detail is
`median(|ac − median(ac)|)`.

## 5. Codes

1. **Descriptors**: OpenCV SIFT descriptors on the prepared grey image.
   - Recipe 2: detect and describe in one call (`detectAndCompute`, same
     parameters as §4.1) and keep each selected keypoint's own descriptor. Each
     is computed at the octave the detector found it in.
   - Recipe 1: for each selected keypoint, make `cv2.KeyPoint(x, y, size,
     angle)` (octave 0, response 0) and `compute` descriptors for these. Every
     descriptor is then computed at octave 0 with no upsampled base. This is
     how the research computed them.
2. **RootSIFT**, in float32 at every step: `d = d / (sum(d) + 1e-7)`, then
   `r = sqrt(d) * 255`, clip to 0–255, then truncate to uint8.
3. **Projection**: `bit[j] = (Σᵢ r[i] · P[i][j]) > T[j]` for `j < 256`.
   Compute it exactly. Every constant is a multiple of 2⁻⁴⁰, so the reference
   implementation scales them by 2⁴⁰ to int64 and uses integer arithmetic. In
   float64 (JavaScript), the bit can only differ when the sum lands within
   float64 rounding error of `T[j]`. In that case, recompute exactly (BigInt).
4. **Hex**: bit 0 is the most significant bit of the first byte. The 32 bytes
   are written as 64 lower-case hex characters.

**Constants**: one file per recipe, 132,096 bytes of little-endian float32. It
holds `P` (128×256, row-major) and then `T` (256 values). The package checks the
SHA-256 on first use.

| recipe | file | SHA-256 |
| --- | --- | --- |
| 2 | [`projection_v2.f32`](src/image_simprints/projection_v2.f32) | `eb70f802f0ec95e1b177abc3da4438144af276a0b34c2deed0ecf09ff8f96921` |
| 1 | [`projection.f32`](src/image_simprints/projection.f32) | `3e1e7c2d35d72966a2cd3b6252b69c57eaad1379f9a9f4d74911f034c0853eed` |

`P` is the same in both: `numpy.random.default_rng(20261013).normal(size=(128,
256))`. `T` is the per-dimension median of the projected descriptors of the
research's tuning split: for recipe 1 as the research fitted it, for recipe 2
refitted on 12,705 descriptors computed the recipe 2 way
([`scripts/fit_recipe_v2.py`](scripts/fit_recipe_v2.py)). They are never
regenerated.

**Output**, one entry per selected keypoint, in rank order:
`{chunk_idx, code, x, y, scale, angle}`.
- `x = x / w` and `y = y / h`, rounded to 6 decimals (fractions of the prepared
  size).
- `scale = size / min(w, h)`, rounded to 6 decimals.
- `angle` is the SIFT angle in degrees, rounded to 3 decimals.

## 6. Matching

`match(verifier, candidate)` takes two `generate` results. In the research
terms, the verifier is the query and the candidate is the reference.

1. **Geometry** in short-side units, per image with prepared `(w, h)` and
   `short = min(w, h)`: `X = x w / short`, `Y = y h / short`, `S = scale`,
   `A = angle`. The image rectangle is `(w / short) × (h / short)`.
2. **Agreeing pairs**: every (verifier code, candidate code) with Hamming
   distance `≤ tolerance_t`.
3. **Transform per pair**, candidate → verifier:
   - `s = Sq / max(Sr, 1e-9)`
   - `da = radians(((Aq − Ar + 180) mod 360) − 180)`
   - `tx = Xq − s (cos da · Xr − sin da · Yr)`
   - `ty = Yq − s (sin da · Xr + cos da · Yr)`

   Drop pairs with `s` outside `[0.1, 10]`.
4. **Bins**: `ls = round(log2(max(s, 1e-9)) / 0.5)`,
   `ab = round(degrees(da) / 30) mod 12`, `bx = round(tx / 0.15)`,
   `by = round(ty / 0.15)`. Here `round` rounds half to even.
5. **Vote**: a bin's count is the smaller of its distinct verifier codes and its
   distinct candidate codes. The winner is the bin with the highest count. On a
   tie, the bin with the smallest key wins, where
   `key = (((ls + 32) · 16 + ab) · 2000 + bx + 1000) · 2000 + by + 1000`.
   `agreeing_codes` is the winner's count. If it is below `min_votes`, the
   result is `none`.
6. **Transform** from all pairs in the winning bin:
   - With one pair, build the similarity from its `s`, `da`, `tx`, `ty`.
   - With more, use OpenCV `estimateAffinePartial2D(candidate XY, verifier XY,
     LMEDS)`. If that fails, use the first pair. If the result is not finite (all
     pairs at one point), also use the first pair.
7. **Footprint**: map the candidate rectangle into the verifier, in float64.
   Clip it to the verifier rectangle `[0, w] × [0, h]` (Sutherland–Hodgman
   against the four sides, a point on a side counting as inside) and take the
   area of what is left (shoelace formula).
   Then `share_candidate = min(1, area / |det| / area_candidate)` and
   `share_verifier = min(1, area / area_verifier)`, where `det` is the
   determinant of the transform's 2×2 part.
8. **Span check**: take the largest distance between any two verifier keypoints
   in the winning bin. Divide it by
   `sqrt(max(share_verifier · area_verifier, 1e-9))`. If the result is not at
   least `span_check`, the result is `none`.
9. **Relationship**, with `c = 0.95`:
   - `identical` if both shares are at least `c`.
   - otherwise `contains` if `share_candidate ≥ c` (the whole candidate is in
     the verifier's image).
   - otherwise `contained_in` if `share_verifier ≥ c`.
   - otherwise `overlapping` if both shares are above 0.01.
   - otherwise `none`.

   `overlap_fraction` is `{verifier: share_verifier, candidate: share_candidate}`,
   rounded to 4 decimals, or zeros for `none`.

## 7. Test vectors

The images are in [`tests/vectors/`](tests/vectors/). The expected `creator`
output, for every code, is in
[`tests/vectors/expected_v2.json`](tests/vectors/expected_v2.json) (recipe 2,
default settings) and [`tests/vectors/expected.json`](tests/vectors/expected.json)
(recipe 1). The images are synthetic and seeded
([`tests/make_vectors.py`](tests/make_vectors.py)). Both recipes select the same
keypoints; only the codes differ. `profile.png` is `portrait.png` with an
embedded profile (linear sRGB) that would brighten it a lot if applied; its
codes must equal `portrait.png`'s.

| image | SHA-256 (first 16) | prepared | codes | first keypoint |
| --- | --- | --- | --- | --- |
| shapes.png (640×480) | 902012a8c25b8141 | 512×384 | 20 | x 0.753158, y 0.360695, scale 0.065891, angle 100.702 |
| portrait.png (480×720) | 5d4418a54c8dc9ce | 341×512 | 20 | x 0.684841, y 0.864998, scale 0.106013, angle 87.277 |
| small.png (24×24) | d256eeb4f84d86be | 24×24 | 0 | reason `too small` |
| profile.png (480×720) | 0befb18822bf6488 | 341×512 | 20 | as portrait.png |

| image | first code, recipe 2 | first code, recipe 1 |
| --- | --- | --- |
| shapes.png | `2bcb4b7b9865c349220b08eb45a5a5f7e5d608a02719b55efd6d44b56224ebb0` | `52cb6b5fbb6fc205600b09eb0524896584d204646719b51cf90848bd1224aa80` |
| portrait.png | `d5c5038d2b060ae650a6d7053a4bf68a9009e0b1e40960d8fa043d25afa5650d` | `55cd239825262be272a4d3d7f25b768f340db7b12411eb46bc8531a7f0e54cdc` |

These vectors were produced with OpenCV 5.0.0 (opencv-python-headless
5.0.0.93), NumPy 2.5.1 and Pillow 12.3.0. With those pins the codes are
bit-identical on Windows x86-64, Linux x86-64 and macOS on Apple Silicon (CI
checks all three). `x`, `y` and `scale` can differ by 1 in the sixth
decimal: SIFT keeps keypoints in float32, which rounds differently on each
platform. The test therefore compares codes exactly and geometry within 1e-5.
Another OpenCV build or a reimplementation may differ in a few bits of rare
codes.

## 8. Where this differs from the research code

- **Descriptors** (recipe 2): the research computed every descriptor at octave
  0. A keypoint found at a coarse octave is then described from the
  full-resolution image, so its descriptor shifts when the image size changes:
  with recipe 1, a verifier at 1024 px finds 47.1% of modified copies, against
  63.3% at 512 px. Recipe 2 describes each keypoint at its own octave. On the
  test split (150 originals, 1,000 unrelated photos) at default settings it
  finds 68.0%, and 62.0% with the verifier at 1024 px. Neither recipe has a
  false match between truly unrelated photos at default settings. Every false
  match was checked by eye; the others are duplicates, the same picture, or the
  same scene. `T` and `tolerance_t` were fitted on the tuning split only; the
  fit chose `tolerance_t = 24` for recipe 2. Reports:
  [recipe 2](tests/corpus/report-v2-fit/tolerance_t24/summary.md),
  [recipe 1](tests/corpus/report/summary.md).

- **Preparation**: the research converted to grey with Pillow
  (`convert("L")`) and resized with Pillow's `LANCZOS`. Neither is in OpenCV,
  so this recipe uses OpenCV's grey conversion and `INTER_AREA`. Given the same
  grey image, this package reproduces the research keypoints and codes bit for
  bit (checked on 14 photographs: 260 of 260 codes). The two preparations give
  different exact codes, but similar match rates (see the test report).
- **Projection** is computed exactly, where the research used a float32 matrix
  product. The two agreed on every code checked.
- **Decoding** adds what the research did not need: alpha flattening (the
  research dropped alpha), 16-bit grey, and the minimum size.
- **Colour profiles** (version 2.1): versions 1 and 2 converted an embedded ICC
  profile to sRGB with littleCMS. A browser converts with its own colour
  engine, which moved 7% of the keypoints of the 150 test originals (all in
  originals carrying a profile).
  Version 2.1 ignores profiles, which a browser does exactly
  (`colorSpaceConversion: "none"`). On the 150 test originals, with the copies
  made from the converted pixels (the case that favours converting), ignoring
  finds 67.8% against 68.0%. Converting with littleCMS compiled to WebAssembly
  closed the browser gap as well, at the cost of a WebAssembly module and an
  ICC parser for each file format. Details:
  [image-simprints-js](https://github.com/jmsherrier/image-simprints-js).
- **Matching** is the research's follow-up matcher (`followup.match`,
  `geometry`, `codematch.classify`) for one pair, with its footprint check
  reduced to the span check that was chosen (`spread ≥ 0.05`; the other
  cut-offs were off).
- **Footprint**: the research intersected the two outlines with OpenCV's
  `intersectConvexConvex`. That function returns 0, or a partial area, when the
  outlines nearly coincide, which is exactly the identical-image case (an
  identity transform with residues around 1e-6). On the 150 test originals,
  28 plain re-encodes were therefore called `none` or `overlapping`. This
  package clips the polygon itself (§6.7). Only 4 such failures remain, and all
  4 are images with 0 or 1 codes. The research's numbers were probably
  affected in the same way.
