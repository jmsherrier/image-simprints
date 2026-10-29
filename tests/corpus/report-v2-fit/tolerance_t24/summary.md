# image-simprints test, 2026-10-28

Recipe `image-simprints/2`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0. Match settings: `{"tolerance_t": 24}`.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 56.8% | 56.7% | 31 of 1,296,182 | 4 of 784 | 0.235 |
| 10 | 32 | 1024 | 52.7% | 52.6% | 29 of 1,296,182 | 3 of 784 | 0.214 |
| 10 | 64 | 512 | 57.4% | 57.3% | 31 of 1,296,182 | 4 of 784 | 0.261 |
| 10 | 64 | 1024 | 53.1% | 52.9% | 29 of 1,296,182 | 3 of 784 | 0.232 |
| 20 | 32 | 512 | 66.5% | 66.5% | 39 of 1,296,182 | 4 of 784 | 0.274 |
| 20 | 32 | 1024 | 61.2% | 61.2% | 38 of 1,296,182 | 4 of 784 | 0.253 |
| 20 (default) | 64 | 512 | 68.0% | 68.0% | 39 of 1,296,182 | 6 of 784 | 0.315 |
| 20 | 64 | 1024 | 62.0% | 62.0% | 38 of 1,296,182 | 6 of 784 | 0.279 |
| 50 | 32 | 512 | 72.9% | 72.9% | 48 of 1,296,182 | 8 of 784 | 0.343 |
| 50 | 32 | 1024 | 65.8% | 65.8% | 44 of 1,296,182 | 6 of 784 | 0.31 |
| 50 | 64 | 512 | 76.5% | 76.4% | 53 of 1,296,182 | 8 of 784 | 0.401 |
| 50 | 64 | 1024 | 68.0% | 68.0% | 46 of 1,296,182 | 6 of 784 | 0.342 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 97% | 97% | 150 |
| bright_contrast | identical | 97% | 97% | 150 |
| collage15 | contains | 27% | 27% | 150 |
| collage15 reversed | contained_in | 15% | 15% | 150 |
| collage30 | contains | 59% | 59% | 150 |
| collage30 reversed | contained_in | 37% | 37% | 150 |
| collage50 | contains | 77% | 77% | 150 |
| collage50 reversed | contained_in | 63% | 63% | 150 |
| crop10 | contained_in | 5% | 5% | 150 |
| crop20 | contained_in | 20% | 20% | 150 |
| crop30 | contained_in | 43% | 43% | 150 |
| crop50 | contained_in | 79% | 79% | 150 |
| crop70 | contained_in | 87% | 87% | 150 |
| crop90 | contained_in | 96% | 96% | 150 |
| greyscale | identical | 97% | 97% | 150 |
| identical | identical | 97% | 97% | 150 |
| jpeg60 | identical | 97% | 97% | 150 |
| overlap15 | overlapping | 10% | 10% | 150 |
| overlap30 | overlapping | 48% | 48% | 150 |
| overlap50 | overlapping | 79% | 79% | 150 |
| resize25 | identical | 97% | 97% | 150 |
| resize50 | identical | 97% | 97% | 150 |
| rotate15 | contained_in | 81% | 81% | 150 |
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
- unrelated/u0636.jpg -> unrelated/u0640.jpg
- unrelated/u0639.jpg -> unrelated/u0641.jpg
- unrelated/u0640.jpg -> unrelated/u0636.jpg
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
