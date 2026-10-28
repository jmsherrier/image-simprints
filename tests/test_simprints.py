import io
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageCms

import image_simprints as s
from image_simprints import recipe as R

V = Path(__file__).parent / "vectors"
SHAPES = V / "shapes.png"


def rgb(path=SHAPES) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def png(img: Image.Image, **kw) -> bytes:
    buf = io.BytesIO()
    img.save(buf, "PNG", **kw)
    return buf.getvalue()


# --- determinism and test vectors --------------------------------------------------------


def test_same_input_same_codes():
    a = s.generate(SHAPES, "creator")
    assert s.generate(SHAPES, "creator") == a
    assert s.generate(SHAPES.read_bytes(), "creator") == a
    assert s.generate(rgb(), "creator") == a
    assert s.generate(SHAPES, "verifier")["codes"][:20] == a["codes"]  # creator codes: the verifier's first N


def test_threads_agree_with_serial():
    want = s.generate(SHAPES, "verifier")
    with ThreadPoolExecutor(4) as ex:
        assert all(r == want for r in ex.map(lambda _: s.generate(SHAPES, "verifier"), range(8)))


@pytest.mark.parametrize("name", ["shapes.png", "portrait.png", "small.png"])
def test_vectors(name):
    want = json.loads((V / "expected.json").read_text(encoding="utf-8"))[name]
    got = json.loads(json.dumps(s.generate(V / name, "creator")))
    differ = [w["chunk_idx"] for w, g in zip(want["codes"], got["codes"]) if w != g]
    assert got == want, f"{len(differ)} of {len(want['codes'])} codes differ: {differ}"


# --- errors ------------------------------------------------------------------------------


@pytest.mark.parametrize("bad", [b"", b"not an image", SHAPES.read_bytes()[:300]])
def test_damaged_input(bad):
    with pytest.raises(s.ImageError):
        s.generate(bad, "creator")


def test_bad_arguments():
    with pytest.raises(TypeError):
        s.generate(123, "creator")
    with pytest.raises(ValueError):
        s.generate(SHAPES, "owner")
    with pytest.raises(ValueError):
        s.generate(SHAPES, "creator", {"codes": 5})
    with pytest.raises(s.ImageError):
        s.generate(np.zeros((64, 64), np.float32), "creator")
    with pytest.raises(FileNotFoundError):
        s.generate(V / "missing.png", "creator")
    a = s.generate(SHAPES, "creator")
    with pytest.raises(ValueError):
        s.match(a | {"recipe_version": "other/1"}, a)


def test_too_small_gives_no_codes_and_a_reason():
    r = s.generate(V / "small.png", "creator")
    assert r["codes"] == [] and "too small" in r["reason"]


# --- decoding ----------------------------------------------------------------------------


def test_exif_orientation_applied():
    img = Image.fromarray(rgb())
    exif = Image.Exif()
    exif[0x0112] = 6  # display rotated 90 degrees clockwise
    out = R.decode(png(img, exif=exif))
    assert (out == np.asarray(img.transpose(Image.Transpose.ROTATE_270))).all()


def test_alpha_flattened_on_white():
    a = np.zeros((40, 40, 4), np.uint8)
    a[..., 0] = 200
    a[:, :20, 3] = 255
    out = R.decode(png(Image.fromarray(a, "RGBA")))
    assert (out[:, :20] == [200, 0, 0]).all() and (out[:, 20:] == 255).all()


def test_16_bit_grey_keeps_high_byte():
    a = (np.arange(64 * 64, dtype=np.uint16) * 16).reshape(64, 64)
    out = R.decode(png(Image.fromarray(a)))
    assert (out[..., 0] == a >> 8).all()


def test_cmyk_and_srgb_profile():
    img = Image.fromarray(rgb())
    buf = io.BytesIO()
    img.convert("CMYK").save(buf, "JPEG", quality=95)
    assert np.abs(R.decode(buf.getvalue()).astype(int) - rgb()).mean() < 8
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    assert np.abs(R.decode(png(img, icc_profile=icc)).astype(int) - rgb()).max() <= 2


def test_animated_uses_first_frame():
    frames = [Image.new("RGB", (40, 40), c) for c in ("red", "blue")]
    buf = io.BytesIO()
    frames[0].save(buf, "GIF", save_all=True, append_images=frames[1:])
    out = R.decode(buf.getvalue())
    assert (out[..., 0] > 200).all() and (out[..., 2] < 50).all()


# --- end to end --------------------------------------------------------------------------


def test_crop_and_collage():
    img = Image.open(SHAPES).convert("RGB")
    w, h = img.size
    creator = s.generate(SHAPES, "creator")
    crop = s.generate(np.asarray(img.crop((0, 0, w * 3 // 4, h * 3 // 4))), "verifier")
    assert s.match(crop, creator)["relationship"] == "contained_in"
    collage = Image.open(V / "portrait.png").convert("RGB")
    collage.paste(img.resize((w * 2 // 3, h * 2 // 3), Image.Resampling.LANCZOS), (40, 100))
    m = s.match(s.generate(np.asarray(collage), "verifier"), creator)
    assert m["relationship"] == "contains" and m["overlap_fraction"]["candidate"] > 0.95
    reverse = s.match(s.generate(SHAPES, "verifier"), s.generate(np.asarray(collage), "creator"))
    assert reverse["relationship"] == "contained_in"
    unrelated = s.match(s.generate(V / "portrait.png", "verifier"), creator)
    assert unrelated == {"relationship": "none", "overlap_fraction": {"verifier": 0.0, "candidate": 0.0},
                         "agreeing_codes": 0}  # fmt: skip
