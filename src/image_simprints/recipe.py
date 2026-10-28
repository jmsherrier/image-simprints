"""The recipe: decode, prepare, detect, select, code; and the matcher.

RECIPE.md describes every step; keep the two in step. Ported from
bakau research/granular_constraints (features.py, codematch.py, grid.py) and
research/granular_followup (followup.py: asymmetric queries, footprint check).
"""

import hashlib
import io
import math
from functools import cache
from importlib.resources import files
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageCms, ImageOps

RECIPE = "image-simprints/1"
DEFAULTS = {
    "recipe": 1,  # 1: descriptors at octave 0, as the research; 2: at each keypoint's octave (experimental)
    "creator_codes": 20,  # codes a creator stores (top-K)
    "verifier_codes": 64,  # codes a verifier extracts (up to K)
    "tolerance_t": 24,  # Hamming distance at or below which two codes agree
    "min_votes": 2,  # agreeing codes needed on one transform
    "prepared_size": 512,  # longer side of the prepared image, never upscaled
    "span_check": 0.05,  # spread of the agreeing verifier keypoints, see _judge
    "sift_features": 1500,  # SIFT keeps this many strongest keypoints (0: all)
    "candidates": 512,  # strongest keypoints considered before the floors
}
MIN_SIDE = 32  # a prepared image shorter than this on either side gets no codes
SIZE_FLOOR = 0.02  # keypoint diameter, as a share of the short side
DETAIL_FLOOR = 200.0  # patch detail (#064 in bakau), see _detail
PATCH_SIDE, PATCH_FACTOR = 32, 2.0
SCALE_RANGE = (0.1, 10.0)  # plausible scale between two images of one picture
CONTAINED = 0.95  # a footprint share at or above this counts as the whole image
BACKGROUND = 255  # alpha is flattened onto white

# Per recipe: its defaults where they differ from DEFAULTS, and its constants file.
RECIPES = {
    1: {"defaults": {}, "constants": "projection.f32",
        "sha256": "3e1e7c2d35d72966a2cd3b6252b69c57eaad1379f9a9f4d74911f034c0853eed"},
    2: {"defaults": {"tolerance_t": 32}, "constants": "projection_v2.f32",  # t fitted on tuning: scripts/fit_recipe_v2.py
        "sha256": "eb70f802f0ec95e1b177abc3da4438144af276a0b34c2deed0ecf09ff8f96921"},
}  # fmt: skip


class ImageError(ValueError):
    """The source cannot be decoded, or is of an unsupported kind."""


@cache
def projection(recipe: int) -> tuple[np.ndarray, np.ndarray]:
    """(P, T) of a recipe, checked against its checksum, as exact int64 (x 2^40)."""
    r = RECIPES[recipe]
    raw = files(__package__).joinpath(r["constants"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != r["sha256"]:
        raise RuntimeError(f"{r['constants']} does not match its checksum; reinstall image-simprints")
    v = np.frombuffer(raw, "<f4").astype(np.float64)
    # Every constant is a multiple of 2^-40, so this scaling is exact and the
    # projection below is exact integer arithmetic: the same bits on every platform.
    exact = (v * 2.0**40).astype(np.int64)
    if not (exact == v * 2.0**40).all():
        raise RuntimeError(f"{r['constants']} has a constant that is not a multiple of 2^-40")
    return exact[: 128 * 256].reshape(128, 256), exact[128 * 256 :]


projection(1)  # checked on import
_SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
_DCT8 = 2.0 * np.cos(np.pi * np.outer(np.arange(8), 2 * np.arange(PATCH_SIDE) + 1) / (2 * PATCH_SIDE))


def defaults_of(recipe: int) -> dict:
    if recipe not in RECIPES:
        raise ValueError(f"unknown recipe {recipe!r}; known: {sorted(RECIPES)}")
    return DEFAULTS | {"recipe": recipe} | RECIPES[recipe]["defaults"]


def settings_of(settings: dict | None) -> dict:
    unknown = set(settings or {}) - set(DEFAULTS)
    if unknown:
        raise ValueError(f"unknown settings: {sorted(unknown)}")
    return defaults_of((settings or {}).get("recipe", 1)) | (settings or {})


def version_of(s: dict) -> str:
    """The recipe version: image-simprints/<recipe>, plus every setting that differs
    from that recipe's default."""
    d = defaults_of(s["recipe"])
    return ";".join([f"image-simprints/{s['recipe']}", *(f"{k}={s[k]}" for k in DEFAULTS if s[k] != d[k])])


# --- decoding --------------------------------------------------------------------------


def decode(source) -> np.ndarray:
    """RGB uint8 (h, w, 3), sRGB, upright, alpha flattened, first frame."""
    if isinstance(source, np.ndarray):
        return _from_array(source)
    if isinstance(source, (bytes, bytearray, memoryview)):
        fp = io.BytesIO(bytes(source))
    elif isinstance(source, (str, Path)):
        fp = source
    else:
        raise TypeError(f"source must be a path, bytes or a numpy array, not {type(source).__name__}")
    try:
        with Image.open(fp) as im:
            im.load()  # the first frame; damaged data fails here
            return _to_srgb(im)
    except FileNotFoundError:
        raise
    except Exception as e:  # Pillow raises many kinds on damaged input
        raise ImageError(f"cannot decode image: {type(e).__name__}: {e}") from e


def _to_srgb(im: Image.Image) -> np.ndarray:
    icc = im.info.get("icc_profile")
    im = ImageOps.exif_transpose(im)
    if im.mode in ("I;16", "I;16L", "I;16B", "I;16N", "I"):  # 16-bit grey: keep the high byte
        im = Image.fromarray((np.clip(np.asarray(im), 0, 65535).astype(np.uint32) >> 8).astype(np.uint8))
    alpha = None
    if im.has_transparency_data:
        im = im.convert("RGBA")
        alpha = np.asarray(im.getchannel("A"), np.uint32)[..., None]
        im = im.convert("RGB")
    if im.mode not in ("RGB", "L", "CMYK"):
        im = im.convert("RGB")
    if icc:
        try:
            im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), _SRGB, outputMode="RGB")
        except (ImageCms.PyCMSError, OSError, ValueError):
            pass  # an unreadable or mismatched profile: the pixels are taken as sRGB
    rgb = np.asarray(im.convert("RGB"), np.uint8)
    return rgb if alpha is None else _flatten(rgb, alpha)


def _flatten(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Onto BACKGROUND: (c * a + bg * (255 - a) + 127) // 255, in integers."""
    out = (rgb.astype(np.uint32) * alpha + BACKGROUND * (255 - alpha) + 127) // 255
    return out.astype(np.uint8)


def _from_array(a: np.ndarray) -> np.ndarray:
    """A decoded frame: uint8, (h, w) grey, (h, w, 3) RGB or (h, w, 4) RGBA."""
    if a.dtype != np.uint8:
        raise ImageError(f"frames must be uint8, not {a.dtype}")
    if a.ndim == 2:
        return np.ascontiguousarray(np.repeat(a[..., None], 3, axis=2))
    if a.ndim == 3 and a.shape[2] == 3:
        return np.ascontiguousarray(a)
    if a.ndim == 3 and a.shape[2] == 4:
        return _flatten(a[..., :3], a[..., 3:].astype(np.uint32))
    raise ImageError(f"frames must be (h, w), (h, w, 3) or (h, w, 4), not {a.shape}")


def prepare(rgb: np.ndarray, size: int) -> np.ndarray:
    """Grey, longer side `size` by area averaging (never upscaled)."""
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    h, w = g.shape
    f = size / max(h, w)
    if f < 1:
        g = cv2.resize(g, (max(1, round(w * f)), max(1, round(h * f))), interpolation=cv2.INTER_AREA)
    return g


# --- codes -----------------------------------------------------------------------------


def generate(source, role: str, settings: dict | None = None) -> dict:
    """Codes for one image. role: "creator" (stores the top creator_codes) or
    "verifier" (extracts up to verifier_codes)."""
    if role not in ("creator", "verifier"):
        raise ValueError(f'role must be "creator" or "verifier", not {role!r}')
    s = settings_of(settings)
    g = prepare(decode(source), s["prepared_size"])
    h, w = g.shape
    out = {"recipe_version": version_of(s), "prepared_size": (w, h), "codes": [], "reason": None}
    if min(h, w) < MIN_SIDE:
        out["reason"] = f"too small: prepared image is {w}x{h}, needs {MIN_SIDE} px on each side"
        return out
    k = s["creator_codes" if role == "creator" else "verifier_codes"]
    rows, desc = select(g, k, s["sift_features"], s["candidates"], octave=s["recipe"] == 2)
    if not len(rows):
        out["reason"] = "no keypoints with enough detail"
        return out
    short = min(w, h)
    codes = codes_of(g, rows, s["recipe"], desc)
    for n, (code, (x, y, size, angle, _)) in enumerate(zip(codes, rows, strict=True)):
        out["codes"].append({"chunk_idx": n, "code": code, "x": round(float(x / w), 6), "y": round(float(y / h), 6),
                             "scale": round(float(size / short), 6), "angle": round(float(angle), 3)})  # fmt: skip
    return out


def select(g: np.ndarray, k: int, sift_features=1500, candidates=512, octave=False) -> tuple:
    """Up to k keypoints as rows (x, y, size, angle, response): the strongest, with
    enough patch detail and a diameter of at least SIZE_FLOOR of the short side.
    With octave (recipe 2), also their SIFT descriptors from the same call as the
    detection, so each is computed at the octave the detector found it in."""
    sift = cv2.SIFT_create(nfeatures=sift_features)
    kps, desc = sift.detectAndCompute(g, None) if octave else (sift.detect(g, None), None)
    rows = np.array([(p.pt[0], p.pt[1], p.size, p.angle, p.response) for p in kps], np.float64).reshape(-1, 5)
    idx = np.lexsort((rows[:, 0], rows[:, 1], -rows[:, 4]))[:candidates]
    idx = idx[_detail(g, rows[idx]) >= DETAIL_FLOOR]
    idx = idx[rows[idx, 2] >= SIZE_FLOOR * min(g.shape)][:k]
    return rows[idx], (desc[idx] if octave and len(idx) else None)


def _detail(g: np.ndarray, rows: np.ndarray) -> np.ndarray:
    """Per keypoint: an upright 32x32 patch, PATCH_FACTOR x its diameter, from the
    pyramid level nearest its scale; the 8x8 low-frequency DCT corner of it; the
    median absolute deviation of the 63 AC coefficients."""
    pyramid = [g.astype(np.float32)]
    while min(pyramid[-1].shape) > PATCH_SIDE * 2:
        pyramid.append(cv2.pyrDown(pyramid[-1]))
    side = PATCH_SIDE
    out = np.zeros(len(rows))
    for n, (x, y, size, angle, _) in enumerate(rows):
        extent = PATCH_FACTOR * size
        level = min(len(pyramid) - 1, max(0, int(np.floor(np.log2(max(extent, 1) / side)))))
        f = 2.0**level
        sc = extent / f / side
        a = np.deg2rad(angle)
        cos, sin = np.cos(a) * sc, np.sin(a) * sc
        cx, cy = x / f, y / f
        m = np.array([[cos, -sin, cx - cos * side / 2 + sin * side / 2],
                      [sin, cos, cy - sin * side / 2 - cos * side / 2]])  # fmt: skip
        p = cv2.warpAffine(pyramid[level], m, (side, side),
                           flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)  # fmt: skip
        ac = (_DCT8 @ p.astype(np.float64) @ _DCT8.T).ravel()[1:]
        out[n] = np.median(np.abs(ac - np.median(ac)))
    return out


def codes_of(g: np.ndarray, rows: np.ndarray, recipe=1, desc=None) -> list[str]:
    """RootSIFT per keypoint, projected to 256 dimensions and thresholded: 64 hex chars.
    Recipe 1 re-creates the keypoints from (x, y, size, angle), so every descriptor is
    computed at octave 0, as the research did; recipe 2 passes the detector's own."""
    if desc is None:
        kp = [cv2.KeyPoint(float(x), float(y), float(s), float(a)) for x, y, s, a, _ in rows]
        _, desc = cv2.SIFT_create().compute(g, kp)  # nfeatures only limits detection
    p, t = projection(recipe)
    bits = rootsift(desc).astype(np.int64) @ p > t
    return [b.tobytes().hex() for b in np.packbits(bits, axis=1)]


def rootsift(desc: np.ndarray) -> np.ndarray:
    desc = desc / (desc.sum(axis=1, keepdims=True) + np.float32(1e-7))  # float32 throughout
    return np.clip(np.sqrt(desc) * np.float32(255), 0, 255).astype(np.uint8)


# --- matching --------------------------------------------------------------------------


def parse(r: dict) -> tuple[np.ndarray, np.ndarray, tuple[float, float]]:
    """A generate() result -> (codes as (n, 4) uint64, geometry (x, y, size, angle) in
    short-side units, the image's (w, h) in short-side units)."""
    if r.get("recipe_version", "").split(";")[0] not in {f"image-simprints/{n}" for n in RECIPES}:
        raise ValueError(f"codes are from an unknown recipe: {r.get('recipe_version')!r}")
    w, h = r["prepared_size"]
    short = min(w, h)
    c = [x for x in r["codes"] if not x.get("stop")]  # see mark_stop_codes
    codes = np.array([np.frombuffer(bytes.fromhex(x["code"]), ">u8") for x in c], np.uint64).reshape(-1, 4)
    geo = np.array([(x["x"] * w / short, x["y"] * h / short, x["scale"], x["angle"]) for x in c]).reshape(-1, 4)
    return codes, geo, (w / short, h / short)


def mark_stop_codes(simprints: list[dict], n: int, settings: dict | None = None, against: list[dict] | None = None):
    """Copies of stored generate() results with "stop": True on each code that agrees
    (within tolerance_t) with codes of more than n other declarations in `against`
    (default: the same list). match() ignores marked codes: a guard against hub
    images, as stop words are ignored in text search. An index-side option."""
    against = simprints if against is None else against
    s = settings_of(settings)
    codes = [parse(r)[0] for r in against]
    if not codes:
        return list(simprints)
    every = np.concatenate(codes)
    owner = np.repeat(np.arange(len(codes)), [len(c) for c in codes])
    out = []
    for r in simprints:
        mine = parse(r)[0]
        own = next((i for i, x in enumerate(against) if x is r), -1)
        near = hamming(mine, every) <= s["tolerance_t"] if len(mine) else np.zeros((0, len(every)), bool)
        hub = [len(set(owner[row].tolist()) - {own}) > n for row in near]
        kept = iter(hub)
        out.append(r | {"codes": [c | {"stop": True} if not c.get("stop") and next(kept) else c for c in r["codes"]]})
    return out


def hamming(q: np.ndarray, r: np.ndarray) -> np.ndarray:
    return np.bitwise_count(q[:, None, :] ^ r[None, :, :]).sum(axis=2, dtype=np.int32)


def match(verifier_codes: dict, candidate_codes: dict, settings: dict | None = None) -> dict:
    """How the verifier's image relates to the candidate's, from their codes."""
    cq, gq, size_q = parse(verifier_codes)
    recipes = {r["recipe_version"].split(";")[0].rsplit("/", 1)[1] for r in (verifier_codes, candidate_codes)}
    recipes |= {str(settings["recipe"])} if settings and "recipe" in settings else set()
    if len(recipes) > 1:
        raise ValueError(f"cannot match codes of different recipes: {sorted(recipes)}")
    s = settings_of({"recipe": int(recipes.pop())} | (settings or {}))
    cr, gr, size_r = parse(candidate_codes)
    qi, rj = np.nonzero(hamming(cq, cr) <= s["tolerance_t"])
    best, members = votes(qi, rj, np.zeros(len(cr), int), gq, gr, 1)
    return judge(int(best[0]), members[0], gq, gr, size_q, size_r, s)


def transform_of(gq, gr) -> tuple:
    """Per code pair: (scale, rotation in radians, tx, ty), candidate -> verifier."""
    s = gq[:, 2] / np.maximum(gr[:, 2], 1e-9)
    da = np.deg2rad((gq[:, 3] - gr[:, 3] + 180) % 360 - 180)
    c, sn = np.cos(da), np.sin(da)
    tx = gq[:, 0] - s * (c * gr[:, 0] - sn * gr[:, 1])
    ty = gq[:, 1] - s * (sn * gr[:, 0] + c * gr[:, 1])
    return s, da, tx, ty


def bins(s, da, tx, ty) -> np.ndarray:
    """log2 scale in half steps, rotation in 30-degree steps, shift in 0.15 steps."""
    ls = np.round(np.log2(np.maximum(s, 1e-9)) / 0.5).astype(np.int64)
    ab = np.round(np.rad2deg(da) / 30).astype(np.int64) % 12
    bx = np.round(tx / 0.15).astype(np.int64)
    by = np.round(ty / 0.15).astype(np.int64)
    return (((ls + 32) * 16 + ab) * 2000 + bx + 1000) * 2000 + by + 1000


def votes(qi, rj, owner, gq, gr, nrefs) -> tuple[np.ndarray, list]:
    """For each candidate image (owner[rj]): the most code pairs agreeing on one
    transform bin, counted as the smaller of distinct verifier and distinct
    candidate codes, and that bin's (verifier index, candidate index) pairs."""
    best = np.zeros(nrefs, dtype=np.int32)
    members = [None] * nrefs
    if not len(qi):
        return best, members
    s, da, tx, ty = transform_of(gq[qi], gr[rj])
    ok = (s >= SCALE_RANGE[0]) & (s <= SCALE_RANGE[1])
    qi, rj, key = qi[ok], rj[ok], bins(s[ok], da[ok], tx[ok], ty[ok])
    if not len(qi):
        return best, members
    own = owner[rj]
    order = np.lexsort((qi, key, own))
    qi, rj, key, own = qi[order], rj[order], key[order], own[order]
    first_q = np.ones(len(qi), bool)
    first_q[1:] = (own[1:] != own[:-1]) | (key[1:] != key[:-1]) | (qi[1:] != qi[:-1])
    starts = np.flatnonzero(np.concatenate(([True], (own[1:] != own[:-1]) | (key[1:] != key[:-1]))))
    counts = np.add.reduceat(first_q.astype(np.int32), starts)
    o2 = np.lexsort((rj, key, own))  # the same groups in the same order, by candidate code within each
    r2, k2, w2 = rj[o2], key[o2], own[o2]
    first_r = np.ones(len(r2), bool)
    first_r[1:] = (w2[1:] != w2[:-1]) | (k2[1:] != k2[:-1]) | (r2[1:] != r2[:-1])
    counts = np.minimum(counts, np.add.reduceat(first_r.astype(np.int32), starts))
    g_own = own[starts]
    ends = np.append(starts[1:], len(qi))
    for g in np.argsort(-counts, kind="stable"):
        o = g_own[g]
        if counts[g] > best[o]:
            best[o] = counts[g]
            members[o] = (qi[starts[g] : ends[g]], rj[starts[g] : ends[g]])
    return best, members


def estimate(gq, gr) -> np.ndarray:
    """3x3 similarity, candidate -> verifier: one pair from its scale and angle,
    several by least median of squares."""
    if len(gq) == 1:
        s, da, tx, ty = (v[0] for v in transform_of(gq, gr))
        c, sn = s * np.cos(da), s * np.sin(da)
        return np.array([[c, -sn, tx], [sn, c, ty], [0, 0, 1]])
    m, _ = cv2.estimateAffinePartial2D(gr[:, :2].astype(np.float32), gq[:, :2].astype(np.float32), method=cv2.LMEDS)
    if m is None:
        return estimate(gq[:1], gr[:1])
    return np.vstack([m, [0, 0, 1]])


def clipped_area(poly: np.ndarray, w: float, h: float) -> float:
    """Area of a convex polygon inside [0, w] x [0, h]: Sutherland-Hodgman clipping,
    then the shoelace formula. (OpenCV's intersectConvexConvex returns 0 when the
    two outlines nearly coincide, as they do for an identical image.)"""
    pts = [np.asarray(p, np.float64) for p in poly]
    for axis, bound, sign in ((0, 0.0, 1), (0, w, -1), (1, 0.0, 1), (1, h, -1)):
        inside = [sign * (p[axis] - bound) >= 0 for p in pts]
        out = []
        for i, q in enumerate(pts):
            p, p_in = pts[i - 1], inside[i - 1]
            if inside[i] != p_in:  # the edge p -> q crosses the boundary
                out.append(p + (bound - p[axis]) / (q[axis] - p[axis]) * (q - p))
            if inside[i]:
                out.append(q)
        pts = out
        if not pts:
            return 0.0
    x, y = np.array(pts).T
    return float(abs(x @ np.roll(y, -1) - y @ np.roll(x, -1)) / 2)


def footprint(t: np.ndarray, size_r, size_q) -> tuple[float, float]:
    """(share of the candidate covered by the verifier, share of the verifier
    covered by the candidate) under the candidate -> verifier transform."""

    w, h = size_r
    poly = (np.array([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]], np.float64) @ t.T)[:, :2]
    area = clipped_area(poly, *size_q)
    det = abs(np.linalg.det(t[:2, :2]))
    if area <= 0 or det <= 0:
        return 0.0, 0.0
    return min(1.0, area / det / (size_r[0] * size_r[1])), min(1.0, area / (size_q[0] * size_q[1]))


def judge(count, mem, gq, gr, size_q, size_r, s) -> dict:
    """The relationship from the winning bin: enough votes, a span check, then
    the footprint of each image in the other."""
    out = {"relationship": "none", "overlap_fraction": {"verifier": 0.0, "candidate": 0.0}, "agreeing_codes": count}
    if count < s["min_votes"] or mem is None:
        return out
    gq, gr = gq[mem[0]], gr[mem[1]]
    t = estimate(gq, gr)
    if not np.isfinite(t).all():  # all pairs at one point (SIFT emits a keypoint twice, two angles)
        t = estimate(gq[:1], gr[:1])
    share_r, share_q = footprint(t, size_r, size_q)
    region = max(share_q * size_q[0] * size_q[1], 1e-9)  # the claimed overlap, in the verifier
    span = float(np.hypot(*(gq[:, None, :2] - gq[None, :, :2]).transpose(2, 0, 1)).max())
    if not span / math.sqrt(region) >= s["span_check"]:  # NaN fails too
        return out
    if share_r >= CONTAINED and share_q >= CONTAINED:
        rel = "identical"
    elif share_r >= CONTAINED:
        rel = "contains"  # the whole candidate is in the verifier's image
    elif share_q >= CONTAINED:
        rel = "contained_in"  # the whole verifier image is in the candidate's
    else:
        rel = "overlapping" if share_r > 0.01 and share_q > 0.01 else "none"
    if rel != "none":
        out["overlap_fraction"] = {"verifier": round(float(share_q), 4), "candidate": round(float(share_r), 4)}
    out["relationship"] = rel
    return out
