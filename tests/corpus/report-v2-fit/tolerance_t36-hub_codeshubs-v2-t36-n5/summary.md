# image-simprints test, 2026-10-28

Recipe `image-simprints/2`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0. Match settings: `{"tolerance_t": 36, "hub_codes": "tests/corpus/hubs-v2-t36-n5.json"}`.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 60.0% | 59.9% | 37 of 1,293,906 | 6 of 784 | 0.239 |
| 10 | 32 | 1024 | 55.6% | 55.4% | 35 of 1,293,906 | 6 of 784 | 0.224 |
| 10 | 64 | 512 | 60.5% | 60.4% | 39 of 1,293,906 | 6 of 784 | 0.268 |
| 10 | 64 | 1024 | 56.0% | 55.7% | 36 of 1,293,906 | 6 of 784 | 0.24 |
| 20 | 32 | 512 | 69.4% | 69.4% | 59 of 1,293,906 | 6 of 784 | 0.281 |
| 20 | 32 | 1024 | 63.9% | 63.9% | 48 of 1,293,906 | 8 of 784 | 0.263 |
| 20 (default) | 64 | 512 | 70.8% | 70.7% | 65 of 1,293,906 | 6 of 784 | 0.317 |
| 20 | 64 | 1024 | 64.8% | 64.7% | 50 of 1,293,906 | 8 of 784 | 0.284 |
| 50 | 32 | 512 | 75.3% | 75.2% | 76 of 1,293,906 | 8 of 784 | 0.347 |
| 50 | 32 | 1024 | 68.2% | 68.2% | 59 of 1,293,906 | 9 of 784 | 0.319 |
| 50 | 64 | 512 | 78.7% | 78.6% | 96 of 1,293,906 | 8 of 784 | 0.404 |
| 50 | 64 | 1024 | 70.1% | 70.0% | 69 of 1,293,906 | 9 of 784 | 0.348 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 97% | 97% | 150 |
| bright_contrast | identical | 97% | 97% | 150 |
| collage15 | contains | 36% | 36% | 150 |
| collage15 reversed | contained_in | 20% | 20% | 150 |
| collage30 | contains | 61% | 61% | 150 |
| collage30 reversed | contained_in | 45% | 45% | 150 |
| collage50 | contains | 79% | 79% | 150 |
| collage50 reversed | contained_in | 65% | 65% | 150 |
| crop10 | contained_in | 7% | 7% | 150 |
| crop20 | contained_in | 29% | 27% | 150 |
| crop30 | contained_in | 49% | 48% | 150 |
| crop50 | contained_in | 81% | 81% | 150 |
| crop70 | contained_in | 88% | 88% | 150 |
| crop90 | contained_in | 96% | 96% | 150 |
| greyscale | identical | 97% | 97% | 150 |
| identical | identical | 97% | 97% | 150 |
| jpeg60 | identical | 97% | 97% | 150 |
| overlap15 | overlapping | 17% | 17% | 150 |
| overlap30 | overlapping | 54% | 54% | 150 |
| overlap50 | overlapping | 81% | 81% | 150 |
| resize25 | identical | 97% | 97% | 150 |
| resize50 | identical | 97% | 97% | 150 |
| rotate15 | contained_in | 87% | 87% | 150 |
| rotate90 | identical | 97% | 97% | 150 |
| webp60 | identical | 97% | 97% | 150 |

## Time per original (one process, decoding included)

- decode: mean 26.5 ms, median 26.4 ms, p95 55.1 ms (150 images)
- creator at 512: mean 82.3 ms, median 83.9 ms, p95 123.6 ms (150 images)
- verifier at 512: mean 83.5 ms, median 84.1 ms, p95 129.9 ms (150 images)
- verifier at 1024: mean 119.2 ms, median 117.7 ms, p95 160.8 ms (150 images)

## False matches, default settings (verifier, candidate)

- originals/s054.jpg -> unrelated/u0681.jpg
- unrelated/u0039.jpg -> unrelated/u0832.jpg
- unrelated/u0081.jpg -> unrelated/u0082.jpg
- unrelated/u0082.jpg -> unrelated/u0081.jpg
- unrelated/u0108.jpg -> unrelated/u0107.jpg
- unrelated/u0145.jpg -> unrelated/u0144.jpg
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
- unrelated/u0393.jpg -> unrelated/u0103.jpg
- unrelated/u0411.jpg -> originals/s038.jpg
- unrelated/u0411.jpg -> unrelated/u0681.jpg
- unrelated/u0418.jpg -> unrelated/u0419.jpg
- unrelated/u0419.jpg -> unrelated/u0418.jpg
- unrelated/u0464.jpg -> unrelated/u0465.jpg
- unrelated/u0465.jpg -> unrelated/u0464.jpg
- unrelated/u0468.jpg -> unrelated/u0469.jpg
- unrelated/u0469.jpg -> unrelated/u0468.jpg
- unrelated/u0541.jpg -> unrelated/u0542.jpg
- unrelated/u0542.jpg -> unrelated/u0541.jpg
- unrelated/u0591.jpg -> unrelated/u0467.jpg
- unrelated/u0628.jpg -> unrelated/u0727.jpg
- unrelated/u0628.jpg -> unrelated/u0728.jpg
- unrelated/u0636.jpg -> unrelated/u0638.jpg
- unrelated/u0636.jpg -> unrelated/u0639.jpg
- unrelated/u0636.jpg -> unrelated/u0640.jpg
- unrelated/u0636.jpg -> unrelated/u0641.jpg
- unrelated/u0637.jpg -> unrelated/u0638.jpg
- unrelated/u0638.jpg -> unrelated/u0637.jpg
- unrelated/u0639.jpg -> unrelated/u0636.jpg
- unrelated/u0639.jpg -> unrelated/u0640.jpg
- unrelated/u0639.jpg -> unrelated/u0641.jpg
- unrelated/u0640.jpg -> unrelated/u0636.jpg
- unrelated/u0640.jpg -> unrelated/u0639.jpg
- unrelated/u0641.jpg -> unrelated/u0636.jpg
- unrelated/u0653.jpg -> unrelated/u0654.jpg
- unrelated/u0681.jpg -> originals/s038.jpg
- unrelated/u0702.jpg -> unrelated/u0704.jpg
- unrelated/u0704.jpg -> unrelated/u0702.jpg
- unrelated/u0727.jpg -> unrelated/u0628.jpg
- unrelated/u0727.jpg -> unrelated/u0728.jpg
- unrelated/u0728.jpg -> unrelated/u0628.jpg
- unrelated/u0728.jpg -> unrelated/u0727.jpg

## Look-alike false matches, default settings (verifier, candidate)

- set14/0.jpg -> set14/1.jpg
- set41/0.jpg -> set41/1.jpg
- set42/0.jpg -> set42/1.jpg
- set42/1.jpg -> set42/0.jpg
- set43/0.jpg -> set43/1.jpg
- set43/1.jpg -> set43/0.jpg
