# image-simprints test, 2026-10-28

Recipe `image-simprints/2`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0. Match settings: `{"tolerance_t": 28, "stop_codes": 1}`.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 57.9% | 57.8% | 29 of 1,296,182 | 4 of 784 | 0.236 |
| 10 | 32 | 1024 | 53.5% | 53.4% | 27 of 1,296,182 | 3 of 784 | 0.22 |
| 10 | 64 | 512 | 58.5% | 58.4% | 29 of 1,296,182 | 4 of 784 | 0.264 |
| 10 | 64 | 1024 | 53.9% | 53.7% | 27 of 1,296,182 | 3 of 784 | 0.233 |
| 20 | 32 | 512 | 67.8% | 67.8% | 36 of 1,296,182 | 4 of 784 | 0.277 |
| 20 | 32 | 1024 | 62.4% | 62.4% | 33 of 1,296,182 | 4 of 784 | 0.258 |
| 20 (default) | 64 | 512 | 69.2% | 69.2% | 36 of 1,296,182 | 6 of 784 | 0.314 |
| 20 | 64 | 1024 | 63.1% | 63.1% | 33 of 1,296,182 | 6 of 784 | 0.279 |
| 50 | 32 | 512 | 73.8% | 73.8% | 44 of 1,296,182 | 6 of 784 | 0.344 |
| 50 | 32 | 1024 | 66.7% | 66.7% | 39 of 1,296,182 | 6 of 784 | 0.311 |
| 50 | 64 | 512 | 77.1% | 77.1% | 48 of 1,296,182 | 6 of 784 | 0.404 |
| 50 | 64 | 1024 | 68.5% | 68.5% | 41 of 1,296,182 | 6 of 784 | 0.345 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 97% | 97% | 150 |
| bright_contrast | identical | 97% | 97% | 150 |
| collage15 | contains | 30% | 30% | 150 |
| collage15 reversed | contained_in | 16% | 16% | 150 |
| collage30 | contains | 61% | 61% | 150 |
| collage30 reversed | contained_in | 43% | 43% | 150 |
| collage50 | contains | 79% | 79% | 150 |
| collage50 reversed | contained_in | 63% | 63% | 150 |
| crop10 | contained_in | 5% | 5% | 150 |
| crop20 | contained_in | 23% | 23% | 150 |
| crop30 | contained_in | 46% | 46% | 150 |
| crop50 | contained_in | 79% | 79% | 150 |
| crop70 | contained_in | 87% | 87% | 150 |
| crop90 | contained_in | 96% | 96% | 150 |
| greyscale | identical | 97% | 97% | 150 |
| identical | identical | 97% | 97% | 150 |
| jpeg60 | identical | 97% | 97% | 150 |
| overlap15 | overlapping | 13% | 13% | 150 |
| overlap30 | overlapping | 51% | 51% | 150 |
| overlap50 | overlapping | 79% | 79% | 150 |
| resize25 | identical | 97% | 97% | 150 |
| resize50 | identical | 97% | 97% | 150 |
| rotate15 | contained_in | 85% | 85% | 150 |
| rotate90 | identical | 97% | 97% | 150 |
| webp60 | identical | 97% | 97% | 150 |

## Time per original (one process, decoding included)

- decode: mean 26.5 ms, median 26.4 ms, p95 55.1 ms (150 images)
- creator at 512: mean 82.3 ms, median 83.9 ms, p95 123.6 ms (150 images)
- verifier at 512: mean 83.5 ms, median 84.1 ms, p95 129.9 ms (150 images)
- verifier at 1024: mean 119.2 ms, median 117.7 ms, p95 160.8 ms (150 images)

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
- unrelated/u0653.jpg -> unrelated/u0654.jpg
- unrelated/u0702.jpg -> unrelated/u0704.jpg
- unrelated/u0704.jpg -> unrelated/u0702.jpg
- unrelated/u0727.jpg -> unrelated/u0628.jpg
- unrelated/u0755.jpg -> unrelated/u0756.jpg
- unrelated/u0756.jpg -> unrelated/u0755.jpg
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

- set14/0.jpg -> set14/1.jpg
- set41/0.jpg -> set41/1.jpg
- set42/0.jpg -> set42/1.jpg
- set42/1.jpg -> set42/0.jpg
- set43/0.jpg -> set43/1.jpg
- set43/1.jpg -> set43/0.jpg
