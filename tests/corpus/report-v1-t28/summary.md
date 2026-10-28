# image-simprints test, 2026-10-28

Recipe `image-simprints/1`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0. Match settings: `{"tolerance_t": 28}`.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 57.0% | 56.9% | 41 of 1,296,182 | 4 of 784 | 0.339 |
| 10 | 32 | 1024 | 44.5% | 44.3% | 29 of 1,296,182 | 2 of 784 | 0.287 |
| 10 | 64 | 512 | 57.3% | 57.2% | 41 of 1,296,182 | 4 of 784 | 0.379 |
| 10 | 64 | 1024 | 44.9% | 44.7% | 29 of 1,296,182 | 2 of 784 | 0.329 |
| 20 | 32 | 512 | 65.1% | 65.1% | 50 of 1,296,182 | 4 of 784 | 0.391 |
| 20 | 32 | 1024 | 51.8% | 51.8% | 38 of 1,296,182 | 2 of 784 | 0.335 |
| 20 (default) | 64 | 512 | 66.3% | 66.2% | 50 of 1,296,182 | 4 of 784 | 0.463 |
| 20 | 64 | 1024 | 52.6% | 52.5% | 38 of 1,296,182 | 2 of 784 | 0.362 |
| 50 | 32 | 512 | 69.6% | 69.6% | 56 of 1,296,182 | 4 of 784 | 0.484 |
| 50 | 32 | 1024 | 55.5% | 55.4% | 42 of 1,296,182 | 2 of 784 | 0.408 |
| 50 | 64 | 512 | 72.1% | 72.1% | 59 of 1,296,182 | 4 of 784 | 0.573 |
| 50 | 64 | 1024 | 57.3% | 57.3% | 43 of 1,296,182 | 2 of 784 | 0.802 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 97% | 97% | 150 |
| bright_contrast | identical | 97% | 97% | 150 |
| collage15 | contains | 9% | 9% | 150 |
| collage15 reversed | contained_in | 3% | 3% | 150 |
| collage30 | contains | 49% | 49% | 150 |
| collage30 reversed | contained_in | 35% | 35% | 150 |
| collage50 | contains | 77% | 77% | 150 |
| collage50 reversed | contained_in | 63% | 63% | 150 |
| crop10 | contained_in | 3% | 3% | 150 |
| crop20 | contained_in | 10% | 10% | 150 |
| crop30 | contained_in | 37% | 37% | 150 |
| crop50 | contained_in | 79% | 79% | 150 |
| crop70 | contained_in | 89% | 89% | 150 |
| crop90 | contained_in | 96% | 96% | 150 |
| greyscale | identical | 97% | 97% | 150 |
| identical | identical | 97% | 97% | 150 |
| jpeg60 | identical | 97% | 97% | 150 |
| overlap15 | overlapping | 15% | 15% | 150 |
| overlap30 | overlapping | 51% | 51% | 150 |
| overlap50 | overlapping | 81% | 81% | 150 |
| resize25 | identical | 96% | 96% | 150 |
| resize50 | identical | 97% | 97% | 150 |
| rotate15 | contained_in | 85% | 85% | 150 |
| rotate90 | identical | 97% | 97% | 150 |
| webp60 | identical | 97% | 97% | 150 |

## Time per original (one process, decoding included)

- decode: mean 31.5 ms, median 33.3 ms, p95 68.0 ms (150 images)
- creator at 512: mean 108.5 ms, median 109.6 ms, p95 159.9 ms (150 images)
- verifier at 512: mean 109.8 ms, median 112.1 ms, p95 162.9 ms (150 images)
- verifier at 1024: mean 173.9 ms, median 179.4 ms, p95 226.0 ms (150 images)

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
- unrelated/u0640.jpg -> unrelated/u0641.jpg
- unrelated/u0641.jpg -> unrelated/u0636.jpg
- unrelated/u0641.jpg -> unrelated/u0640.jpg
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
