# image-simprints test, 2026-11-02

Recipe `image-simprints/2.2`; 150 originals, 1000 unrelated images, 205 look-alikes in 44 sets, 3750 positive pairs; Windows-11-10.0.26200-SP0, Python 3.12.10, OpenCV 5.0.0.

## Sweep

| creator codes | verifier codes | verifier size | found | label correct | false matches | look-alike false matches | ms per match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | 32 | 512 | 57.2% | 57.1% | 31 of 1,307,592 | 4 of 784 | 0.404 |
| 10 | 32 | 1024 | 57.2% | 57.1% | 30 of 1,307,592 | 3 of 784 | 0.783 |
| 10 | 64 | 512 | 57.9% | 57.8% | 31 of 1,307,592 | 4 of 784 | 0.278 |
| 10 | 64 | 1024 | 57.7% | 57.6% | 30 of 1,307,592 | 3 of 784 | 0.648 |
| 20 | 32 | 512 | 67.1% | 67.1% | 40 of 1,307,592 | 4 of 784 | 0.701 |
| 20 | 32 | 1024 | 66.8% | 66.8% | 42 of 1,307,592 | 4 of 784 | 0.751 |
| 20 (default) | 64 | 512 | 68.9% | 68.9% | 40 of 1,307,592 | 6 of 784 | 0.805 |
| 20 | 64 | 1024 | 68.4% | 68.4% | 42 of 1,307,592 | 6 of 784 | 0.789 |
| 50 | 32 | 512 | 74.3% | 74.3% | 49 of 1,307,592 | 8 of 784 | 0.857 |
| 50 | 32 | 1024 | 73.0% | 73.0% | 50 of 1,307,592 | 6 of 784 | 0.834 |
| 50 | 64 | 512 | 78.8% | 78.8% | 54 of 1,307,592 | 8 of 784 | 1.067 |
| 50 | 64 | 1024 | 76.9% | 76.9% | 53 of 1,307,592 | 6 of 784 | 0.408 |

## Per manipulation, default settings

| manipulation | expected | found | label correct | pairs |
| --- | --- | --- | --- | --- |
| avif50 | identical | 97% | 97% | 150 |
| bright_contrast | identical | 97% | 97% | 150 |
| collage15 | contains | 29% | 29% | 150 |
| collage15 reversed | contained_in | 15% | 15% | 150 |
| collage30 | contains | 59% | 59% | 150 |
| collage30 reversed | contained_in | 38% | 38% | 150 |
| collage50 | contains | 79% | 79% | 150 |
| collage50 reversed | contained_in | 63% | 63% | 150 |
| crop10 | contained_in | 5% | 5% | 150 |
| crop20 | contained_in | 21% | 21% | 150 |
| crop30 | contained_in | 44% | 44% | 150 |
| crop50 | contained_in | 82% | 82% | 150 |
| crop70 | contained_in | 89% | 89% | 150 |
| crop90 | contained_in | 97% | 97% | 150 |
| greyscale | identical | 97% | 97% | 150 |
| identical | identical | 97% | 97% | 150 |
| jpeg60 | identical | 97% | 97% | 150 |
| overlap15 | overlapping | 11% | 11% | 150 |
| overlap30 | overlapping | 50% | 50% | 150 |
| overlap50 | overlapping | 84% | 84% | 150 |
| resize25 | identical | 97% | 97% | 150 |
| resize50 | identical | 97% | 97% | 150 |
| rotate15 | contained_in | 82% | 82% | 150 |
| rotate90 | identical | 97% | 97% | 150 |
| webp60 | identical | 97% | 97% | 150 |

## Time per original (one process, decoding included)

Measured with another corpus run on the same machine, so about four times slower than idle; see report-v2.1 for times on an idle machine.

- decode: mean 76.4 ms, median 66.7 ms, p95 167.4 ms (150 images)
- creator at 512: mean 353.3 ms, median 343.2 ms, p95 747.5 ms (150 images)
- verifier at 512: mean 364.5 ms, median 337.3 ms, p95 791.9 ms (150 images)
- verifier at 1024: mean 660.6 ms, median 713.3 ms, p95 1248.3 ms (150 images)

## False matches, default settings (verifier, candidate)

- originals/s067.jpg -> unrelated/u0330.jpg
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
