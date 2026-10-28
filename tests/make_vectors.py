"""Make the test-vector images (seeded, synthetic) and their expected codes.

    python tests/make_vectors.py

Run only when the recipe version changes; commit both the images and expected.json.
"""

import json
from pathlib import Path

import cv2
import numpy as np

from image_simprints import generate

HERE = Path(__file__).parent / "vectors"


def shapes(w, h, seed) -> np.ndarray:
    """Overlapping filled shapes in random colours, lightly blurred, with grain."""
    rng = np.random.default_rng(seed)
    img = np.full((h, w, 3), 128, np.uint8)
    for _ in range(160):
        colour = tuple(int(c) for c in rng.integers(0, 256, 3))
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        r = int(rng.integers(2, max(w, h) // 8 + 3))
        if rng.random() < 0.5:
            cv2.circle(img, (x, y), r, colour, -1)
        else:
            cv2.rectangle(img, (x - r, y - r // 2), (x + r, y + r // 2), colour, -1)
    img = cv2.GaussianBlur(img, (0, 0), 1.0)
    return np.clip(img + rng.normal(0, 4, img.shape), 0, 255).astype(np.uint8)


def main() -> None:
    HERE.mkdir(exist_ok=True)
    images = {"shapes.png": shapes(640, 480, 1), "portrait.png": shapes(480, 720, 2),
              "small.png": shapes(24, 24, 3)}  # fmt: skip
    expected = {}
    for name, rgb in images.items():
        cv2.imwrite(str(HERE / name), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        expected[name] = generate(HERE / name, "creator")
    (HERE / "expected.json").write_text(json.dumps(expected, indent=1) + "\n", encoding="utf-8")
    for name, r in expected.items():
        print(name, r["prepared_size"], len(r["codes"]), r["reason"])


if __name__ == "__main__":
    main()
