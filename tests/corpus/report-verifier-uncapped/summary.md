# image-simprints test, 2026-10-28

Recipe `image-simprints/1`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0. Verifier settings: `{"sift_features": 0, "candidates": 4096}`.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 54.9% | 54.8% | 38 of 1,296,182 | 4 of 784 | 0.319 |
| 10 | 32 | 1024 | 41.5% | 41.2% | 26 of 1,296,182 | 0 of 784 | 0.258 |
| 10 | 64 | 512 | 55.2% | 55.1% | 38 of 1,296,182 | 4 of 784 | 0.351 |
| 10 | 64 | 1024 | 42.0% | 41.8% | 26 of 1,296,182 | 0 of 784 | 0.22 |
| 20 | 32 | 512 | 62.8% | 62.8% | 48 of 1,296,182 | 4 of 784 | 0.257 |
| 20 | 32 | 1024 | 51.8% | 51.5% | 34 of 1,296,182 | 2 of 784 | 0.225 |
| 20 (default) | 64 | 512 | 63.8% | 63.7% | 48 of 1,296,182 | 4 of 784 | 0.298 |
| 20 | 64 | 1024 | 52.8% | 52.6% | 34 of 1,296,182 | 2 of 784 | 0.269 |
| 50 | 32 | 512 | 66.8% | 66.8% | 53 of 1,296,182 | 4 of 784 | 0.314 |
| 50 | 32 | 1024 | 56.6% | 56.5% | 40 of 1,296,182 | 2 of 784 | 0.402 |
| 50 | 64 | 512 | 69.5% | 69.5% | 55 of 1,296,182 | 4 of 784 | 0.564 |
| 50 | 64 | 1024 | 60.9% | 60.7% | 43 of 1,296,182 | 2 of 784 | 0.347 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 97% | 97% | 150 |
| bright_contrast | identical | 97% | 97% | 150 |
| collage15 | contains | 4% | 4% | 150 |
| collage15 reversed | contained_in | 1% | 1% | 150 |
| collage30 | contains | 36% | 36% | 150 |
| collage30 reversed | contained_in | 24% | 24% | 150 |
| collage50 | contains | 72% | 72% | 150 |
| collage50 reversed | contained_in | 57% | 57% | 150 |
| crop10 | contained_in | 1% | 1% | 150 |
| crop20 | contained_in | 5% | 5% | 150 |
| crop30 | contained_in | 27% | 26% | 150 |
| crop50 | contained_in | 78% | 78% | 150 |
| crop70 | contained_in | 90% | 90% | 150 |
| crop90 | contained_in | 96% | 96% | 150 |
| greyscale | identical | 97% | 97% | 150 |
| identical | identical | 97% | 97% | 150 |
| jpeg60 | identical | 97% | 97% | 150 |
| overlap15 | overlapping | 12% | 12% | 150 |
| overlap30 | overlapping | 51% | 51% | 150 |
| overlap50 | overlapping | 83% | 83% | 150 |
| resize25 | identical | 94% | 94% | 150 |
| resize50 | identical | 97% | 97% | 150 |
| rotate15 | contained_in | 85% | 85% | 150 |
| rotate90 | identical | 97% | 97% | 150 |
| webp60 | identical | 97% | 97% | 150 |

## Time per original (one process, decoding included)

- decode: mean 32.3 ms, median 33.4 ms, p95 71.3 ms (150 images)
- creator at 512: mean 109.0 ms, median 109.5 ms, p95 161.6 ms (150 images)
- verifier at 512: mean 152.0 ms, median 144.4 ms, p95 317.3 ms (150 images)
- verifier at 1024: mean 337.9 ms, median 299.2 ms, p95 579.8 ms (150 images)

## False matches, default settings (verifier, candidate)

- unrelated/u0081.jpg -> unrelated/u0082.jpg
- unrelated/u0082.jpg -> unrelated/u0081.jpg
- unrelated/u0150.jpg -> unrelated/u0151.jpg
- unrelated/u0151.jpg -> unrelated/u0150.jpg
- unrelated/u0167.jpg -> unrelated/u0169.jpg
- unrelated/u0169.jpg -> unrelated/u0167.jpg
- unrelated/u0236.jpg -> unrelated/u0237.jpg
- unrelated/u0237.jpg -> unrelated/u0236.jpg
- unrelated/u0279.jpg -> unrelated/u0280.jpg
- unrelated/u0280.jpg -> unrelated/u0279.jpg
- unrelated/u0324.jpg -> unrelated/u0326.jpg
- unrelated/u0326.jpg -> unrelated/u0324.jpg
- unrelated/u0418.jpg -> unrelated/u0419.jpg
- unrelated/u0419.jpg -> unrelated/u0418.jpg
- unrelated/u0464.jpg -> unrelated/u0465.jpg
- unrelated/u0465.jpg -> unrelated/u0464.jpg
- unrelated/u0468.jpg -> unrelated/u0469.jpg
- unrelated/u0469.jpg -> unrelated/u0468.jpg
- unrelated/u0541.jpg -> unrelated/u0542.jpg
- unrelated/u0542.jpg -> unrelated/u0541.jpg
- unrelated/u0628.jpg -> unrelated/u0727.jpg
- unrelated/u0628.jpg -> unrelated/u0728.jpg
- unrelated/u0636.jpg -> unrelated/u0638.jpg
- unrelated/u0636.jpg -> unrelated/u0640.jpg
- unrelated/u0636.jpg -> unrelated/u0641.jpg
- unrelated/u0639.jpg -> unrelated/u0640.jpg
- unrelated/u0639.jpg -> unrelated/u0641.jpg
- unrelated/u0640.jpg -> unrelated/u0636.jpg
- unrelated/u0640.jpg -> unrelated/u0639.jpg
- unrelated/u0641.jpg -> unrelated/u0636.jpg
- unrelated/u0702.jpg -> unrelated/u0704.jpg
- unrelated/u0704.jpg -> unrelated/u0702.jpg
- unrelated/u0727.jpg -> unrelated/u0628.jpg
- unrelated/u0727.jpg -> unrelated/u0728.jpg
- unrelated/u0728.jpg -> unrelated/u0628.jpg
- unrelated/u0728.jpg -> unrelated/u0727.jpg
- unrelated/u0755.jpg -> unrelated/u0756.jpg
- unrelated/u0756.jpg -> unrelated/u0755.jpg
- unrelated/u0761.jpg -> unrelated/u0763.jpg
- unrelated/u0763.jpg -> unrelated/u0761.jpg
- unrelated/u0781.jpg -> unrelated/u0782.jpg
- unrelated/u0782.jpg -> unrelated/u0781.jpg
- unrelated/u0800.jpg -> unrelated/u0801.jpg
- unrelated/u0801.jpg -> unrelated/u0800.jpg
- unrelated/u0812.jpg -> unrelated/u0814.jpg
- unrelated/u0814.jpg -> unrelated/u0812.jpg
- unrelated/u0963.jpg -> unrelated/u0964.jpg
- unrelated/u0964.jpg -> unrelated/u0963.jpg

## Look-alike false matches, default settings (verifier, candidate)

- set42/0.jpg -> set42/1.jpg
- set42/1.jpg -> set42/0.jpg
- set43/0.jpg -> set43/1.jpg
- set43/1.jpg -> set43/0.jpg
