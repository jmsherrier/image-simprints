"""Makes the figures of DEMO.md from test-split photos and test mode's copies of them
(run `image-simprints fetch-corpus` first): python docs/demo/make.py"""

import json
import random
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from image_simprints import generate, match
from image_simprints import recipe as R
from image_simprints import testmode as T

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent
ORIGINALS, UNRELATED = T.images_in(ROOT / ".cache/corpus/originals"), T.images_in(ROOT / ".cache/corpus/unrelated")
PHOTO, CROWDED, SMALL, FLAT, PATTERN = "s015.jpg", "s131.jpg", "s002.jpg", ("s042.jpg", "s126.jpg"), ("s067.jpg", "u0330.jpg")
GREEN, GREY, ORANGE, BLUE, WHITE = (80, 200, 80), (170, 170, 170), (40, 150, 255), (230, 140, 40), (255, 255, 255)


def path_of(name):
    return next(p for p in ORIGINALS + UNRELATED if p.name == name)


def copies(name):
    """Test mode's copies of an original: the same background and seed as `image-simprints test`."""
    i = [p.name for p in ORIGINALS].index(name)
    src, bg = Image.fromarray(R.decode(ORIGINALS[i])), Image.fromarray(R.decode(UNRELATED[i % len(UNRELATED)]))
    imgs, pairs = T.derive(src, bg, random.Random(i))
    imgs["original"] = ORIGINALS[i].read_bytes()
    return imgs, pairs


def bgr(source):
    return np.ascontiguousarray(R.decode(source)[:, :, ::-1])


def fit(img, h):
    return cv2.resize(img, (round(img.shape[1] * h / img.shape[0]), h), interpolation=cv2.INTER_AREA)


def label(img, text, y=28, size=0.7):
    (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, size, 1)
    cv2.rectangle(img, (4, y - h - 8), (16 + w, y + 8), (0, 0, 0), -1)
    cv2.putText(img, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, size, WHITE, 1, cv2.LINE_AA)
    return img


def xy(code, w, h, ox=0):
    return int(ox + code["x"] * w), int(code["y"] * h)


def draw_codes(img, codes, colour, w=None, h=None, ox=0, numbers=False, first=0):
    w, h = w or img.shape[1], h or img.shape[0]
    for i, c in enumerate(codes):
        p, r = xy(c, w, h, ox), max(4, int(c["scale"] * min(w, h) / 2))
        cv2.circle(img, p, r, colour, 2, cv2.LINE_AA)
        a = np.radians(c["angle"])
        cv2.line(img, p, (int(p[0] + r * np.cos(a)), int(p[1] - r * np.sin(a))), colour, 2, cv2.LINE_AA)
        if numbers:
            cv2.putText(img, str(first + i + 1), (p[0] + r, p[1] - r), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colour, 2, cv2.LINE_AA)


def side_by_side(left, right, h=420):
    l, r = fit(left, h), fit(right, h)
    return np.hstack([l, np.full((h, 24, 3), 255, np.uint8), r]), l.shape[1] + 24


def code_pairs(q, c, settings=None):
    """Code pairs within tolerance_t, and the pairs of the winning transform bin, as in match()."""
    s = R.settings_of(settings)
    cq, gq, _ = R.parse(q)
    cr, gr, _ = R.parse(c)
    qi, rj = np.nonzero(R.hamming(cq, cr) <= s["tolerance_t"])
    _, members = R.votes(qi, rj, np.zeros(len(cr), int), gq, gr, 1)
    won = set(zip(*members[0])) if members[0] is not None else set()
    return list(zip(qi, rj)), won


def pairs_figure(q_img, c_img, q, c, text, settings=None, marked=None):
    """The verifier's image (left, its codes as dots) and the candidate's (right, its codes
    as circles); lines join code pairs within tolerance_t: green in the winning bin,
    orange otherwise, or orange for codes marked as stop codes when `marked` is given."""
    pic, ox = side_by_side(q_img, c_img)
    wq, hq = pic.shape[0] * q_img.shape[1] / q_img.shape[0], pic.shape[0]
    wc, hc = pic.shape[0] * c_img.shape[1] / c_img.shape[0], pic.shape[0]
    for x in q["codes"]:
        cv2.circle(pic, xy(x, wq, hq), 3, GREY, -1, cv2.LINE_AA)
    draw_codes(pic, c["codes"], GREY, wc, hc, ox)
    all_pairs, won = code_pairs(q, c, settings)
    for a, b in all_pairs:
        good = not marked["codes"][b].get("stop") if marked else (a, b) in won
        colour = GREEN if good else ORANGE
        cv2.circle(pic, xy(q["codes"][a], wq, hq), 6, colour, -1, cv2.LINE_AA)
        cv2.line(pic, xy(q["codes"][a], wq, hq), xy(c["codes"][b], wc, hc, ox), colour, 2, cv2.LINE_AA)
    return label(pic, text)


def transform(q, c):
    """The candidate -> verifier similarity of the winning bin, in short-side units, as judge() estimates it."""
    _, gq, _ = R.parse(q)
    _, gr, _ = R.parse(c)
    _, won = code_pairs(q, c)
    qi, rj = map(list, zip(*sorted(won)))
    return R.estimate(gq[qi], gr[rj])


def outline(t, w, h):
    return (np.array([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]], float) @ t.T)[:, :2]


def creator_codes(path):
    return generate(path, "creator")


def main():
    imgs, pairs = copies(PHOTO)
    original = bgr(imgs["original"])

    # 1. preparation: grey, longer side 512
    g = R.prepare(R.decode(imgs["original"]), 512)
    pic, _ = side_by_side(original, cv2.cvtColor(g, cv2.COLOR_GRAY2BGR), 300)
    label(pic, f"original {original.shape[1]}x{original.shape[0]}  ->  prepared {g.shape[1]}x{g.shape[0]}, grey")
    cv2.imwrite(str(OUT / "1-prepare.jpg"), pic)

    # 2. keypoints: SIFT, size floor, the strongest 512, detail floor, the first 20
    kps = cv2.SIFT_create(nfeatures=1500).detect(g, None)
    rows = np.array([(p.pt[0], p.pt[1], p.size, p.angle, p.response) for p in kps])
    big = rows[:, 2] >= R.SIZE_FLOOR * min(g.shape)
    order = np.lexsort((rows[:, 0], rows[:, 1], -rows[:, 4]))
    cand = order[big[order]][:512]
    detail = R._detail(g, rows[cand]) >= R.DETAIL_FLOOR
    creator = generate(imgs["original"], "creator")
    f = 1.5
    pic = fit(cv2.cvtColor(g, cv2.COLOR_GRAY2BGR), round(g.shape[0] * f))
    for x, y, *_ in rows[~big]:
        cv2.circle(pic, (int(x * f), int(y * f)), 2, GREY, -1, cv2.LINE_AA)
    for x, y, size, *_ in rows[cand[~detail]]:
        cv2.circle(pic, (int(x * f), int(y * f)), max(3, int(size * f / 2)), ORANGE, 1, cv2.LINE_AA)
    draw_codes(pic, creator["codes"], GREEN, numbers=True)
    counts = f"{len(rows)} SIFT keypoints, {big.sum()} large enough, {detail.sum()} with enough detail, the strongest 20 kept"
    cv2.imwrite(str(OUT / "2-keypoints.jpg"), label(pic, counts, size=0.6))
    print(counts)

    # 3. one code: its patch (upright, twice the keypoint's diameter) and its 256 bits
    x, y, size, angle, _ = R.select(g, 1, octave=True)[0][0]
    a, sc, side = np.deg2rad(angle), 2 * size / 256, 256
    m = np.array([[np.cos(a) * sc, -np.sin(a) * sc, x - np.cos(a) * sc * side / 2 + np.sin(a) * sc * side / 2],
                  [np.sin(a) * sc, np.cos(a) * sc, y - np.sin(a) * sc * side / 2 - np.cos(a) * sc * side / 2]])  # fmt: skip
    patch = cv2.warpAffine(g, m, (side, side), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
    bits = np.unpackbits(np.frombuffer(bytes.fromhex(creator["codes"][0]["code"]), np.uint8)).reshape(16, 16)
    grid = cv2.resize((255 - bits * 255).astype(np.uint8), (side, side), interpolation=cv2.INTER_NEAREST)
    for k in range(0, side + 1, 16):
        cv2.line(grid, (k, 0), (k, side), 200, 1)
        cv2.line(grid, (0, k), (side, k), 200, 1)
    pic = np.hstack([patch, np.full((side, 24), 255, np.uint8), grid])
    cv2.imwrite(str(OUT / "3-code.jpg"), label(cv2.cvtColor(pic, cv2.COLOR_GRAY2BGR), "code 1: its patch, and its 256 bits", 24, 0.55))
    print(json.dumps(creator["codes"][0]))

    # 4. a copy against the original: code pairs within distance 24, and those agreeing on one transform
    copy = imgs["rotate15"]
    q = generate(copy, "verifier")
    result = match(q, creator)
    all_pairs, won = code_pairs(q, creator)
    text = f"rotate15 -> original: {len(all_pairs)} code pairs within 24, {result['agreeing_codes']} agree on one transform"
    cv2.imwrite(str(OUT / "4-pairs.jpg"), pairs_figure(bgr(copy), original, q, creator, text))

    # 5. footprint: the original's outline carried into the copy by that transform
    t = transform(q, creator)
    _, _, (wq, hq) = R.parse(q)
    _, _, (wr, hr) = R.parse(creator)
    img = fit(bgr(copy), 300)
    px = min(img.shape[:2])  # pixels per short-side unit of the copy
    poly = outline(t, wr, hr) * px
    pad = int(max(0, -poly.min(), (poly[:, 0] - img.shape[1]).max(), (poly[:, 1] - img.shape[0]).max())) + 20
    canvas = np.full((img.shape[0] + 2 * pad, img.shape[1] + 2 * pad, 3), 255, np.uint8)
    canvas[pad : pad + img.shape[0], pad : pad + img.shape[1]] = img
    cv2.polylines(canvas, [np.int32(poly + pad)], True, GREEN, 3, cv2.LINE_AA)
    o = result["overlap_fraction"]
    text = f"{result['relationship']}: the copy lies {o['verifier']:.0%} inside the original and covers {o['candidate']:.0%} of it"
    cv2.imwrite(str(OUT / "5-footprint.jpg"), label(canvas, text, size=0.6))

    # 6. the results for a few of the copies
    print(json.dumps(result))
    for m_, v, c in pairs:
        if m_ in ("jpeg60", "crop50", "collage50", "collage50 reversed", "overlap50", "rotate15"):
            r = match(generate(imgs[v], "verifier"), generate(imgs[c], "creator"))
            print(m_, r["relationship"], r["agreeing_codes"], r["overlap_fraction"])

    # 7. fine detail: version 2.1 capped before the size floor; 2.2 applies the floor first
    crowded = path_of(CROWDED)
    g = R.prepare(R.decode(crowded), 512)
    kps = cv2.SIFT_create(nfeatures=1500).detect(g, None)
    strongest = sorted(kps, key=lambda p: -p.response)[:512]
    panels = []
    for floor_first, name in ((False, "2.1"), (True, "2.2")):
        sel, _ = R.select(g, 20, octave=True, floor_first=floor_first)
        pic = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
        for p in strongest:
            cv2.circle(pic, (int(p.pt[0]), int(p.pt[1])), 2, GREY, -1, cv2.LINE_AA)
        draw_codes(pic, [{"x": x / g.shape[1], "y": y / g.shape[0], "scale": s / min(g.shape), "angle": a} for x, y, s, a, _ in sel], GREEN)
        panels.append(label(pic, f"version {name}: {len(sel)} codes", 24, 0.6))
    cv2.imwrite(str(OUT / "7-detail.jpg"), side_by_side(*panels, 340)[0])
    imgs7, pairs7 = copies(CROWDED)
    select = R.select
    for name, floor_first in (("2.1", False), ("2.2", True)):
        R.select = lambda *a, ff=floor_first, **k: select(*a, **k | {"floor_first": ff})  # ponytail: 2.1's selection, for this comparison only
        found = sum(match(generate(imgs7[v], "verifier"), generate(imgs7[c], "creator"))["relationship"] != "none" for _, v, c in pairs7)
        print(f"{CROWDED} under {name}: {found} of {len(pairs7)} copies found")
    R.select = select

    # 8. small pieces: a 20% crop holds few of the 20 stored codes; 50 stored codes put more inside
    imgs8, _ = copies(SMALL)
    q = generate(imgs8["crop20"], "verifier")
    c50 = generate(imgs8["original"], "creator", {"creator_codes": 50})
    r20, r50 = match(q, T.first(c50, 20)), match(q, c50)
    pic = fit(bgr(imgs8["original"]), 420)
    draw_codes(pic, c50["codes"][20:], BLUE)
    draw_codes(pic, c50["codes"][:20], GREEN)
    if r50["relationship"] != "none":  # the crop's outline carried into the original
        _, _, (wq, hq) = R.parse(q)
        inside = outline(np.linalg.inv(transform(q, c50)), wq, hq) * min(pic.shape[:2])
        cv2.polylines(pic, [np.int32(inside)], True, WHITE, 3, cv2.LINE_AA)
        n = [cv2.pointPolygonTest(np.float32(inside), xy(x, pic.shape[1], pic.shape[0]), False) >= 0 for x in c50["codes"]]
        print(f"stored codes inside the crop: {sum(n[:20])} of the first 20, {sum(n)} of 50")
    cv2.imwrite(str(OUT / "8-small.jpg"), label(pic, f"crop20: {r20['relationship']} with 20 stored codes, {r50['relationship']} with 50", size=0.6))
    print("crop20", r20, r50)

    # 9. flat images: too few codes to match
    panels = []
    for name in FLAT:
        r = generate(path_of(name), "creator")
        pic = fit(bgr(path_of(name)), 300)
        draw_codes(pic, r["codes"], GREEN)
        panels.append(label(pic, f"{len(r['codes'])} code" + "s" * (len(r["codes"]) != 1), 24, 0.55))
        print(name, len(r["codes"]), r["reason"])
    cv2.imwrite(str(OUT / "9-flat.jpg"), side_by_side(*panels, 300)[0])

    # 10. a repeated pattern: a stone wall and a frieze, and the stop codes that end it
    q_path, c_path = map(path_of, PATTERN)
    q, c = generate(q_path, "verifier"), generate(c_path, "creator")
    guard = {"tolerance_t": 28}
    with ProcessPoolExecutor() as ex:
        corpus = list(ex.map(creator_codes, ORIGINALS + UNRELATED, chunksize=8))
    marked = R.mark_stop_codes(corpus, 1, guard)[(ORIGINALS + UNRELATED).index(c_path)]
    plain, guarded = match(q, c), match(q, marked, guard)
    stops = sum(x.get("stop", False) for x in marked["codes"])
    text = f"stone wall -> frieze: {plain['relationship']}, {plain['agreeing_codes']} agreeing; with stop codes ({stops} marked): {guarded['relationship']}"
    cv2.imwrite(str(OUT / "10-pattern.jpg"), pairs_figure(bgr(q_path), bgr(c_path), q, c, text, guard, marked))
    print(text)


if __name__ == "__main__":
    main()
