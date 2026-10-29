"""Make the test-vector images (seeded, synthetic) and their expected codes.

    python tests/make_vectors.py

Run only when the recipe version changes; commit both the images and expected.json.
"""

import json
import struct
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

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


def linear_profile() -> bytes:
    """A minimal ICC v2 RGB profile: sRGB primaries with linear curves (gamma 1). Applied,
    it would brighten the image a lot; the recipe ignores it."""
    xyz = lambda *v: b"XYZ " + bytes(4) + struct.pack(">3i", *(round(x * 65536) for x in v))  # noqa: E731
    curv = b"curv" + bytes(4) + struct.pack(">IH2x", 1, 256)  # one gamma, u8Fixed8: 1.0
    tags = [(b"wtpt", xyz(0.9642, 1.0, 0.8249)), (b"rXYZ", xyz(0.4361, 0.2225, 0.0139)),
            (b"gXYZ", xyz(0.3851, 0.7169, 0.0971)), (b"bXYZ", xyz(0.1431, 0.0606, 0.7141)),
            (b"rTRC", curv), (b"gTRC", curv), (b"bTRC", curv)]  # fmt: skip
    table, data, offset = b"", b"", 128 + 4 + 12 * len(tags)
    for sig, d in tags:
        table, data = table + sig + struct.pack(">II", offset + len(data), len(d)), data + d
    body = struct.pack(">I", len(tags)) + table + data
    header = struct.pack(">I4sI4s4s4s12x4s28x", 128 + len(body), b"", 0x02100000, b"mntr", b"RGB ", b"XYZ ", b"acsp")
    return (header + xyz(0.9642, 1.0, 0.8249)[8:]).ljust(128, bytes(1)) + body


def main(recipe: int) -> None:
    """Recipe 1 makes the images and expected.json; another recipe, expected_v<n>.json
    from the same images."""
    HERE.mkdir(exist_ok=True)
    images = {"shapes.png": shapes(640, 480, 1), "portrait.png": shapes(480, 720, 2),
              "small.png": shapes(24, 24, 3), "profile.png": shapes(480, 720, 2)}  # fmt: skip
    expected = {}
    for name, rgb in images.items():
        if recipe == 1 and name == "profile.png":  # portrait.png with an embedded profile: the same codes
            Image.fromarray(rgb).save(HERE / name, icc_profile=linear_profile())
        elif recipe == 1:
            cv2.imwrite(str(HERE / name), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        expected[name] = generate(HERE / name, "creator", {"recipe": recipe})
    out = HERE / ("expected.json" if recipe == 1 else f"expected_v{recipe}.json")
    out.write_text(json.dumps(expected, indent=1) + "\n", encoding="utf-8")
    for name, r in expected.items():
        print(name, r["prepared_size"], len(r["codes"]), r["reason"])


if __name__ == "__main__":
    import sys

    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
