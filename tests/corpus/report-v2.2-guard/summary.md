# image-simprints test, 2026-11-02

Recipe `image-simprints/2.2`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0. Match settings: `{"tolerance_t": 28, "stop_codes": 1}`.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 58.3% | 58.2% | 29 of 1,307,592 | 4 of 784 | 0.612 |
| 10 | 32 | 1024 | 58.0% | 57.9% | 28 of 1,307,592 | 3 of 784 | 0.613 |
| 10 | 64 | 512 | 59.0% | 58.9% | 29 of 1,307,592 | 4 of 784 | 0.281 |
| 10 | 64 | 1024 | 58.6% | 58.5% | 28 of 1,307,592 | 3 of 784 | 0.264 |
| 20 | 32 | 512 | 68.5% | 68.5% | 36 of 1,307,592 | 4 of 784 | 0.292 |
| 20 | 32 | 1024 | 68.0% | 68.0% | 38 of 1,307,592 | 4 of 784 | 0.285 |
| 20 (default) | 64 | 512 | 70.2% | 70.2% | 36 of 1,307,592 | 6 of 784 | 0.333 |
| 20 | 64 | 1024 | 69.6% | 69.5% | 38 of 1,307,592 | 6 of 784 | 0.316 |
| 50 | 32 | 512 | 75.3% | 75.3% | 44 of 1,307,592 | 6 of 784 | 0.412 |
| 50 | 32 | 1024 | 74.0% | 74.0% | 46 of 1,307,592 | 6 of 784 | 0.365 |
| 50 | 64 | 512 | 79.5% | 79.5% | 48 of 1,307,592 | 6 of 784 | 0.432 |
| 50 | 64 | 1024 | 77.6% | 77.6% | 48 of 1,307,592 | 6 of 784 | 0.411 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 97% | 97% | 150 |
| bright_contrast | identical | 97% | 97% | 150 |
| collage15 | contains | 31% | 31% | 150 |
| collage15 reversed | contained_in | 15% | 15% | 150 |
| collage30 | contains | 61% | 61% | 150 |
| collage30 reversed | contained_in | 43% | 43% | 150 |
| collage50 | contains | 79% | 79% | 150 |
| collage50 reversed | contained_in | 63% | 63% | 150 |
| crop10 | contained_in | 6% | 6% | 150 |
| crop20 | contained_in | 24% | 24% | 150 |
| crop30 | contained_in | 50% | 50% | 150 |
| crop50 | contained_in | 83% | 83% | 150 |
| crop70 | contained_in | 90% | 90% | 150 |
| crop90 | contained_in | 97% | 97% | 150 |
| greyscale | identical | 97% | 97% | 150 |
| identical | identical | 97% | 97% | 150 |
| jpeg60 | identical | 97% | 97% | 150 |
| overlap15 | overlapping | 14% | 14% | 150 |
| overlap30 | overlapping | 53% | 53% | 150 |
| overlap50 | overlapping | 85% | 85% | 150 |
| resize25 | identical | 97% | 97% | 150 |
| resize50 | identical | 97% | 97% | 150 |
| rotate15 | contained_in | 87% | 87% | 150 |
| rotate90 | identical | 97% | 97% | 150 |
| webp60 | identical | 97% | 97% | 150 |

## Time per original (one process, decoding included)

- decode: mean 17.6 ms, median 16.1 ms, p95 33.5 ms (150 images)
- creator at 512: mean 79.8 ms, median 76.5 ms, p95 135.6 ms (150 images)
- verifier at 512: mean 80.8 ms, median 77.4 ms, p95 127.6 ms (150 images)
- verifier at 1024: mean 129.8 ms, median 138.4 ms, p95 185.1 ms (150 images)

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
