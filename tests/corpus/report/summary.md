# image-simprints test, 2026-10-28

Recipe `image-simprints/1`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 53.6% | 51.9% | 36 of 1,296,182 | 4 of 784 | 0.181 |
| 10 | 32 | 1024 | 38.1% | 37.9% | 26 of 1,296,182 | 0 of 784 | 0.141 |
| 10 | 64 | 512 | 53.9% | 52.2% | 36 of 1,296,182 | 4 of 784 | 0.204 |
| 10 | 64 | 1024 | 38.4% | 38.2% | 26 of 1,296,182 | 0 of 784 | 0.157 |
| 20 | 32 | 512 | 61.6% | 60.0% | 48 of 1,296,182 | 4 of 784 | 0.209 |
| 20 | 32 | 1024 | 46.5% | 46.4% | 33 of 1,296,182 | 2 of 784 | 0.174 |
| 20 (default) | 64 | 512 | 62.4% | 60.8% | 48 of 1,296,182 | 4 of 784 | 0.243 |
| 20 | 64 | 1024 | 47.1% | 46.9% | 33 of 1,296,182 | 2 of 784 | 0.192 |
| 50 | 32 | 512 | 65.4% | 63.7% | 53 of 1,296,182 | 4 of 784 | 0.268 |
| 50 | 32 | 1024 | 49.8% | 49.7% | 36 of 1,296,182 | 2 of 784 | 0.225 |
| 50 | 64 | 512 | 67.7% | 65.8% | 54 of 1,296,182 | 4 of 784 | 0.327 |
| 50 | 64 | 1024 | 51.8% | 51.7% | 37 of 1,296,182 | 2 of 784 | 0.344 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 95% | 92% | 150 |
| bright_contrast | identical | 97% | 95% | 150 |
| collage15 | contains | 4% | 4% | 150 |
| collage15 reversed | contained_in | 1% | 1% | 150 |
| collage30 | contains | 36% | 36% | 150 |
| collage30 reversed | contained_in | 24% | 24% | 150 |
| collage50 | contains | 71% | 71% | 150 |
| collage50 reversed | contained_in | 57% | 57% | 150 |
| crop10 | contained_in | 1% | 1% | 150 |
| crop20 | contained_in | 5% | 5% | 150 |
| crop30 | contained_in | 27% | 26% | 150 |
| crop50 | contained_in | 75% | 75% | 150 |
| crop70 | contained_in | 89% | 89% | 150 |
| crop90 | contained_in | 96% | 96% | 150 |
| greyscale | identical | 89% | 82% | 150 |
| identical | identical | 91% | 81% | 150 |
| jpeg60 | identical | 95% | 93% | 150 |
| overlap15 | overlapping | 11% | 11% | 150 |
| overlap30 | overlapping | 49% | 48% | 150 |
| overlap50 | overlapping | 81% | 75% | 150 |
| resize25 | identical | 94% | 94% | 150 |
| resize50 | identical | 95% | 90% | 150 |
| rotate15 | contained_in | 84% | 84% | 150 |
| rotate90 | identical | 97% | 97% | 150 |
| webp60 | identical | 95% | 93% | 150 |

## Time per original (one process, decoding included)

- decode: mean 26.0 ms, median 26.0 ms, p95 53.9 ms (150 images)
- creator at 512: mean 84.2 ms, median 83.0 ms, p95 135.3 ms (150 images)
- verifier at 512: mean 85.9 ms, median 85.8 ms, p95 127.2 ms (150 images)
- verifier at 1024: mean 136.2 ms, median 133.0 ms, p95 191.1 ms (150 images)

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
