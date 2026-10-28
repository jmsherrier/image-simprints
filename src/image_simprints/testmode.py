"""`image-simprints test`: match rates per manipulation, false matches, timing, sweeps.

    image-simprints test ORIGINALS [--unrelated DIR] [--modified DIR] [--out DIR]

Without --modified, each original is manipulated in memory as the bakau research
benchmark does (research/granular_bench/pairs.py: crops, collages, overlaps,
JPEG q60, resize, brightness and contrast, rotation 15 and 90), plus WebP, AVIF,
greyscale and a second resize. With --modified, files named
<original stem>__<label>.<ext> are matched against their original.

False matches: every image in ORIGINALS and --unrelated is taken as unrelated to
every other; each one's verifier codes are matched against every other's creator
codes, offline, in both directions.
"""

import argparse
import collections
import io
import itertools
import json
import math
import os
import platform
import random
import statistics
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, features

from . import recipe as R

CREATOR_CODES = (10, 20, 50)
VERIFIER_CODES = (32, 64)
VERIFIER_SIZES = (512, 1024)
CREATOR_SIZE = 512
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".tif", ".tiff", ".bmp", ".gif"}
CHUNK = 4096  # candidate codes per distance block (memory)

# manipulation -> the relationship the verifier (first) should have to the candidate
EXPECTED = {
    "identical": "identical", "resize50": "identical", "resize25": "identical",
    "jpeg60": "identical", "webp60": "identical", "avif50": "identical",
    "bright_contrast": "identical", "greyscale": "identical", "rotate90": "identical",
    "rotate15": "contained_in",
    **{f"crop{a}": "contained_in" for a in (90, 70, 50, 30, 20, 10)},
    **{f"collage{a}": "contains" for a in (50, 30, 15)},
    **{f"collage{a} reversed": "contained_in" for a in (50, 30, 15)},
    **{f"overlap{a}": "overlapping" for a in (50, 30, 15)},
}  # fmt: skip


# --- manipulations (ported from research/granular_bench/pairs.py) -----------------------


def encode(img: Image.Image, fmt="JPEG", **kw) -> bytes:
    buf = io.BytesIO()
    img.save(buf, fmt, **({"quality": 90} | kw))
    return buf.getvalue()


def crop(img, area, rng):
    w, h = img.size
    f = math.sqrt(area)
    cw, ch = w * f, h * f
    x, y = rng.uniform(0, w - cw), rng.uniform(0, h - ch)
    return img.crop(tuple(int(round(v)) for v in (x, y, x + cw, y + ch)))


def resize(img, f):
    return img.resize((max(1, round(img.width * f)), max(1, round(img.height * f))), Image.Resampling.LANCZOS)


def inscribed(w, h, angle_deg):
    """Width and height of the largest upright rectangle inside a w x h rectangle
    rotated by the angle."""
    a = math.radians(angle_deg) % math.pi
    if a > math.pi / 2:
        a = math.pi - a
    sin, cos = abs(math.sin(a)), abs(math.cos(a))
    side_long, side_short = (w, h) if w >= h else (h, w)
    if side_short <= 2 * sin * cos * side_long or abs(sin - cos) < 1e-10:
        x = 0.5 * side_short
        return (x / sin, x / cos) if w >= h else (x / cos, x / sin)
    cos2 = cos * cos - sin * sin
    return (w * cos - h * sin) / cos2, (h * cos - w * sin) / cos2


def rotate(img, angle):
    """Counter-clockwise about the centre (bicubic), cropped to the largest upright
    rectangle inside, so no padding is added."""
    w, h = img.size
    t = math.radians(angle)
    c, s = math.cos(t), math.sin(t)
    W, H = math.ceil(w * c + h * s), math.ceil(w * s + h * c)
    m = np.array([[c, s, W / 2 - c * w / 2 - s * h / 2], [-s, c, H / 2 + s * w / 2 - c * h / 2]])
    out = Image.fromarray(cv2.warpAffine(np.asarray(img), m, (W, H), flags=cv2.INTER_CUBIC))
    wr, hr = inscribed(w, h, angle)
    box = ((W - wr) / 2 + 1, (H - hr) / 2 + 1, (W + wr) / 2 - 1, (H + hr) / 2 - 1)
    return out.crop(tuple(int(round(v)) for v in box))


def collage(src, bg, area, rng):
    w, h = src.size
    bw, bh = bg.size
    f = min(math.sqrt(area * bw * bh / (w * h)), 0.98 * bw / w, 0.98 * bh / h)
    small = resize(src, f)
    canvas = bg.copy()
    canvas.paste(small, (rng.randint(0, bw - small.width), rng.randint(0, bh - small.height)))
    return canvas


def overlap(src, share, rng):
    """Two crops of 25% of the source each, sharing `share` of their area."""
    w, h = src.size
    cw, ch = w * 0.5, h * 0.5
    horizontal = rng.random() < 0.5
    step = (1 - share) * (cw if horizontal else ch)
    span_w, span_h = (cw + step, ch) if horizontal else (cw, ch + step)
    x, y = rng.uniform(0, w - span_w), rng.uniform(0, h - span_h)
    x2, y2 = (x + step, y) if horizontal else (x, y + step)
    box = lambda x, y: tuple(int(round(v)) for v in (x, y, x + cw, y + ch))  # noqa: E731
    return src.crop(box(x, y)), src.crop(box(x2, y2))


def derive(src: Image.Image, bg: Image.Image | None, rng: random.Random):
    """({name: encoded bytes}, [(manipulation, verifier name, candidate name)])."""
    imgs, pairs = {}, []

    def add(name, data, candidate="original", verifier=None):
        imgs[name] = data
        pairs.append((name, verifier or name, candidate))

    add("identical", encode(src))
    for a in (90, 70, 50, 30, 20, 10):
        add(f"crop{a}", encode(crop(src, a / 100, rng)))
    add("resize50", encode(resize(src, 0.5)))
    add("resize25", encode(resize(src, 0.25)))
    add("jpeg60", encode(src, quality=60))
    add("webp60", encode(src, "WEBP", quality=60))
    if features.check("avif"):
        add("avif50", encode(src, "AVIF", quality=50))
    edited = ImageEnhance.Brightness(src).enhance(1 + rng.choice((-0.2, 0.2)))
    add("bright_contrast", encode(ImageEnhance.Contrast(edited).enhance(1 + rng.choice((-0.2, 0.2)))))
    add("greyscale", encode(ImageOps.grayscale(src)))
    add("rotate15", encode(rotate(src, 15)))
    add("rotate90", encode(src.transpose(Image.Transpose.ROTATE_90)))
    for a in (50, 30, 15) if bg is not None else ():
        add(f"collage{a}", encode(collage(src, bg, a / 100, rng)))
        pairs.append((f"collage{a} reversed", "original", f"collage{a}"))
    for a in (50, 30, 15):
        first, second = overlap(src, a / 100, rng)
        imgs[f"overlap{a} first"] = encode(first)
        add(f"overlap{a}", encode(second), candidate=f"overlap{a} first")
    return imgs, pairs


# --- codes, in worker processes --------------------------------------------------------


def codes_for(source, as_verifier=True) -> tuple[dict, dict]:
    """({prepared size: generate() at verifier_codes 64}, {size: ms}). Creator codes
    are the first creator_codes of these: the ranking does not depend on N."""
    out, ms = {}, {}
    for size in VERIFIER_SIZES if as_verifier else (CREATOR_SIZE,):
        t0 = time.perf_counter()
        out[size] = R.generate(source, "verifier", {"prepared_size": size, "verifier_codes": 64})
        ms[size] = (time.perf_counter() - t0) * 1000
    return out, ms


def work_original(job) -> dict:
    index, path, bg_path = job
    src = Image.fromarray(R.decode(path))
    bg = Image.fromarray(R.decode(bg_path)) if bg_path else None
    imgs, pairs = derive(src, bg, random.Random(index))
    imgs["original"] = Path(path).read_bytes()
    verifiers = {v for _, v, _ in pairs} | {"original"}
    codes, ms = {}, []
    for name, data in imgs.items():
        codes[name], t = codes_for(data, name in verifiers)
        ms.append(t)
    return {"name": Path(path).name, "codes": codes, "pairs": pairs, "ms": ms}


def work_modified(job) -> dict:
    path, modified = job
    codes, ms = {}, []
    codes["original"], t = codes_for(path)
    ms.append(t)
    pairs = []
    for m in modified:
        label = m.stem.split("__", 1)[1]
        codes[m.name], t = codes_for(m)
        ms.append(t)
        pairs.append((label, m.name, "original"))
    return {"name": Path(path).name, "codes": codes, "pairs": pairs, "ms": ms}


def work_plain(path) -> dict:
    codes, t = codes_for(path)
    return {"name": Path(path).name, "codes": {"original": codes}, "pairs": [], "ms": [t]}


# --- scoring -----------------------------------------------------------------------------


def first(r: dict, n: int) -> dict:
    return r | {"codes": r["codes"][:n]}


def positives(results, cc, vc, vs) -> tuple[dict, float]:
    """{manipulation: [found, label right, pairs]}, and ms per match."""
    rates = collections.defaultdict(lambda: [0, 0, 0])
    n, t0 = 0, time.perf_counter()
    for res in results:
        for manip, v, c in res["pairs"]:
            m = R.match(first(res["codes"][v][vs], vc), first(res["codes"][c][CREATOR_SIZE], cc))
            found = m["relationship"] != "none"
            rates[manip][0] += found
            rates[manip][1] += found and m["relationship"] == EXPECTED.get(manip)
            rates[manip][2] += 1
            n += 1
    return rates, (time.perf_counter() - t0) * 1000 / max(n, 1)


def false_matches(pool, cc, vc, vs) -> tuple[int, int, list]:
    """Every image's verifier codes against every other's creator codes, at once."""
    s = R.DEFAULTS
    refs = [R.parse(first(p["codes"]["original"][CREATOR_SIZE], cc)) for p in pool]
    rc = np.concatenate([r[0] for r in refs])
    rg = np.concatenate([r[1] for r in refs])
    owner = np.repeat(np.arange(len(pool)), [len(r[0]) for r in refs])
    hits = []
    for i, p in enumerate(pool):
        cq, gq, size_q = R.parse(first(p["codes"]["original"][vs], vc))
        found = [np.nonzero(R.hamming(cq, rc[k : k + CHUNK]) <= s["tolerance_t"]) for k in range(0, len(rc), CHUNK)]
        qi = np.concatenate([f[0] for f in found]).astype(int) if found else np.zeros(0, int)
        rj = np.concatenate([f[1] + k * CHUNK for k, f in enumerate(found)]).astype(int) if found else np.zeros(0, int)
        keep = owner[rj] != i
        best, mem = R.votes(qi[keep], rj[keep], owner, gq, rg, len(pool))
        for j in np.flatnonzero(best >= s["min_votes"]):
            if R.judge(int(best[j]), mem[j], gq, rg, size_q, refs[j][2], s)["relationship"] != "none":
                hits.append([p["name"], pool[j]["name"]])
    return len(hits), len(pool) * (len(pool) - 1), hits


def summarise(ms: list[float]) -> dict:
    if not ms:
        return {}
    q = sorted(ms)
    return {"mean": round(statistics.fmean(q), 1), "median": round(statistics.median(q), 1),
            "p95": round(q[min(len(q) - 1, int(0.95 * len(q)))], 1), "images": len(q)}  # fmt: skip


def images_in(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in EXTENSIONS)


def run(args) -> dict:
    originals = images_in(args.originals)[: args.limit]
    unrelated = images_in(args.unrelated) if args.unrelated else []
    with ProcessPoolExecutor(args.workers) as ex:
        if args.modified:
            by_stem = collections.defaultdict(list)
            for m in images_in(args.modified):
                if "__" in m.stem:
                    by_stem[m.stem.split("__", 1)[0]].append(m)
            results = list(ex.map(work_modified, [(p, by_stem[p.stem]) for p in originals]))
        else:
            n = len(originals)
            bgs = [unrelated[i % len(unrelated)] if unrelated else (originals[(i + 1) % n] if n > 1 else None)
                   for i in range(n)]  # fmt: skip
            results = list(ex.map(work_original, [(i, p, bgs[i]) for i, p in enumerate(originals)]))
        plain = list(ex.map(work_plain, unrelated))
    pool = [r for r in results + plain if r["codes"]["original"][CREATOR_SIZE]["codes"]]
    report = {
        "recipe": R.RECIPE, "date": date.today().isoformat(),
        "environment": {"platform": platform.platform(), "python": platform.python_version(),
                        "opencv": cv2.__version__, "numpy": np.__version__, "pillow": Image.__version__},
        "inputs": {"originals": len(originals), "unrelated": len(unrelated), "modified": bool(args.modified),
                   "positive_pairs": sum(len(r["pairs"]) for r in results), "workers": args.workers,
                   "without_codes": [r["name"] for r in results + plain if not r["codes"]["original"][CREATOR_SIZE]["codes"]]},
        "timing_ms": {f"generate at {s}": summarise([t[s] for r in results + plain for t in r["ms"] if s in t])
                      for s in VERIFIER_SIZES},
        "configs": [],
    }  # fmt: skip
    for cc, vc, vs in itertools.product(CREATOR_CODES, VERIFIER_CODES, VERIFIER_SIZES):
        rates, ms_match = positives(results, cc, vc, vs)
        fm, pairs, hits = false_matches(pool, cc, vc, vs)
        total = [sum(v[i] for v in rates.values()) for i in range(3)]
        report["configs"].append({
            "creator_codes": cc, "verifier_codes": vc, "verifier_prepared_size": vs,
            "default": (cc, vc, vs) == (R.DEFAULTS["creator_codes"], R.DEFAULTS["verifier_codes"], R.DEFAULTS["prepared_size"]),
            "found": round(total[0] / max(total[2], 1), 4), "label_correct": round(total[1] / max(total[2], 1), 4),
            "per_manipulation": {k: {"found": round(v[0] / v[2], 4), "label_correct": round(v[1] / v[2], 4), "pairs": v[2],
                                     "expected": EXPECTED.get(k)} for k, v in sorted(rates.items())},
            "false_matches": fm, "unrelated_pairs": pairs, "false_match_pairs": hits, "ms_per_match": round(ms_match, 3),
        })  # fmt: skip
        print(f"creator {cc}, verifier {vc} at {vs}: found {total[0]}/{total[2]}, false {fm}/{pairs}", flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (args.out / "summary.md").write_text(markdown(report), encoding="utf-8")
    print(f"wrote {args.out / 'report.json'} and {args.out / 'summary.md'}")
    return report


def markdown(rep: dict) -> str:
    inp, env = rep["inputs"], rep["environment"]
    lines = [
        f"# image-simprints test, {rep['date']}",
        "",
        f"Recipe `{rep['recipe']}`; {inp['originals']} originals, {inp['unrelated']} unrelated images, "
        f"{inp['positive_pairs']} positive pairs; {env['platform']}, Python {env['python']}, OpenCV {env['opencv']}.",
        "",
        "## Sweep",
        "",
        "| creator codes | verifier codes | verifier size | found | label correct | false matches | ms per match |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for c in rep["configs"]:
        star = " (default)" if c["default"] else ""
        lines.append(f"| {c['creator_codes']}{star} | {c['verifier_codes']} | {c['verifier_prepared_size']} | "
                     f"{c['found']:.1%} | {c['label_correct']:.1%} | {c['false_matches']} of {c['unrelated_pairs']:,} | "
                     f"{c['ms_per_match']} |")  # fmt: skip
    default = next(c for c in rep["configs"] if c["default"])
    lines += ["", "## Per manipulation, default settings", "",
              "| manipulation | expected | found | label correct | pairs |", "| --- | --- | --- | --- | --- |"]  # fmt: skip
    for k, v in default["per_manipulation"].items():
        lines.append(f"| {k} | {v['expected'] or '-'} | {v['found']:.0%} | {v['label_correct']:.0%} | {v['pairs']} |")
    lines += ["", f"## Time per image (generate, {inp['workers']} worker processes in parallel)", ""]
    lines += [f"- {k}: mean {v['mean']} ms, median {v['median']} ms, p95 {v['p95']} ms ({v['images']} images)"
              for k, v in rep["timing_ms"].items() if v]  # fmt: skip
    if default["false_match_pairs"]:
        lines += ["", "## False matches, default settings (verifier, candidate)", ""]
        lines += [f"- {a} -> {b}" for a, b in default["false_match_pairs"][:50]]
    return "\n".join(lines) + "\n"


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="image-simprints")
    sub = ap.add_subparsers(dest="command", required=True)
    t = sub.add_parser("test", help="match rates, false matches and timing on a folder of images")
    t.add_argument("originals", type=Path, help="folder of original images")
    t.add_argument("--unrelated", type=Path, help="folder of images unrelated to the originals and each other")
    t.add_argument("--modified", type=Path, help="folder of modified copies named <original stem>__<label>.<ext>")
    t.add_argument("--out", type=Path, default=Path("report"), help="where report.json and summary.md go")
    t.add_argument("--workers", type=int, default=os.cpu_count())
    t.add_argument("--limit", type=int, help="use only the first N originals")
    run(ap.parse_args(argv))


if __name__ == "__main__":
    main()
