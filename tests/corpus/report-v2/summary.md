# image-simprints test, 2026-10-28

Recipe `image-simprints/2`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 58.8% | 58.6% | 37 of 1,296,182 | 4 of 784 | 1.185 |
| 10 | 32 | 1024 | 54.4% | 54.3% | 31 of 1,296,182 | 4 of 784 | 1.271 |
| 10 | 64 | 512 | 59.3% | 59.2% | 37 of 1,296,182 | 4 of 784 | 0.906 |
| 10 | 64 | 1024 | 54.8% | 54.7% | 32 of 1,296,182 | 4 of 784 | 1.009 |
| 20 | 32 | 512 | 68.6% | 68.6% | 58 of 1,296,182 | 4 of 784 | 1.672 |
| 20 | 32 | 1024 | 63.2% | 63.2% | 43 of 1,296,182 | 4 of 784 | 0.365 |
| 20 (default) | 64 | 512 | 70.0% | 70.0% | 60 of 1,296,182 | 6 of 784 | 0.452 |
| 20 | 64 | 1024 | 64.1% | 64.0% | 44 of 1,296,182 | 6 of 784 | 0.407 |
| 50 | 32 | 512 | 74.8% | 74.8% | 73 of 1,296,182 | 8 of 784 | 0.5 |
| 50 | 32 | 1024 | 67.7% | 67.7% | 52 of 1,296,182 | 6 of 784 | 0.453 |
| 50 | 64 | 512 | 78.1% | 78.0% | 83 of 1,296,182 | 8 of 784 | 0.58 |
| 50 | 64 | 1024 | 69.5% | 69.4% | 58 of 1,296,182 | 6 of 784 | 0.509 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 97% | 97% | 150 |
| bright_contrast | identical | 97% | 97% | 150 |
| collage15 | contains | 33% | 33% | 150 |
| collage15 reversed | contained_in | 17% | 17% | 150 |
| collage30 | contains | 61% | 61% | 150 |
| collage30 reversed | contained_in | 43% | 43% | 150 |
| collage50 | contains | 81% | 81% | 150 |
| collage50 reversed | contained_in | 63% | 63% | 150 |
| crop10 | contained_in | 6% | 6% | 150 |
| crop20 | contained_in | 27% | 26% | 150 |
| crop30 | contained_in | 47% | 47% | 150 |
| crop50 | contained_in | 80% | 80% | 150 |
| crop70 | contained_in | 89% | 89% | 150 |
| crop90 | contained_in | 96% | 96% | 150 |
| greyscale | identical | 97% | 97% | 150 |
| identical | identical | 97% | 97% | 150 |
| jpeg60 | identical | 97% | 97% | 150 |
| overlap15 | overlapping | 15% | 15% | 150 |
| overlap30 | overlapping | 53% | 53% | 150 |
| overlap50 | overlapping | 81% | 81% | 150 |
| resize25 | identical | 97% | 97% | 150 |
| resize50 | identical | 97% | 97% | 150 |
| rotate15 | contained_in | 86% | 86% | 150 |
| rotate90 | identical | 97% | 97% | 150 |
| webp60 | identical | 97% | 97% | 150 |

## Time per original (one process, decoding included)

- decode: mean 37.9 ms, median 34.1 ms, p95 77.6 ms (150 images)
- creator at 512: mean 136.4 ms, median 120.4 ms, p95 242.8 ms (150 images)
- verifier at 512: mean 134.5 ms, median 119.4 ms, p95 234.5 ms (150 images)
- verifier at 1024: mean 184.5 ms, median 167.0 ms, p95 291.8 ms (150 images)

## False matches, default settings (verifier, candidate)

- originals/s054.jpg -> unrelated/u0681.jpg
- originals/s067.jpg -> unrelated/u0791.jpg
- originals/s124.jpg -> originals/s020.jpg
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
- unrelated/u0681.jpg -> unrelated/u0411.jpg
- unrelated/u0681.jpg -> unrelated/u0467.jpg
- unrelated/u0702.jpg -> unrelated/u0704.jpg
- unrelated/u0704.jpg -> unrelated/u0702.jpg
- unrelated/u0727.jpg -> unrelated/u0628.jpg
- unrelated/u0727.jpg -> unrelated/u0728.jpg
- unrelated/u0728.jpg -> unrelated/u0628.jpg
- unrelated/u0728.jpg -> unrelated/u0727.jpg
- unrelated/u0755.jpg -> unrelated/u0756.jpg
- unrelated/u0756.jpg -> unrelated/u0755.jpg
- unrelated/u0761.jpg -> unrelated/u0467.jpg
- unrelated/u0761.jpg -> unrelated/u0763.jpg

## Look-alike false matches, default settings (verifier, candidate)

- set14/0.jpg -> set14/1.jpg
- set41/0.jpg -> set41/1.jpg
- set42/0.jpg -> set42/1.jpg
- set42/1.jpg -> set42/0.jpg
- set43/0.jpg -> set43/1.jpg
- set43/1.jpg -> set43/0.jpg
