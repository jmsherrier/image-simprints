"""Fit recipe 2's constants on the research TUNING split only (tests/corpus/manifest.csv,
split "tuning"; fetch it with `image-simprints fetch-corpus`).

    python scripts/fit_recipe_v2.py thresholds   # writes src/image_simprints/projection_v2.f32
    python scripts/fit_recipe_v2.py tolerance    # tuning positives and false matches per t

thresholds: the projection P is recipe 1's (seed 20261013); T is the per-dimension median
of P applied to the RootSIFT of every tuning original and unrelated photo's top 64
keypoints at 512 px, with descriptors at each keypoint's octave. As the research fitted
recipe 1's T on its tuning descriptors (granular_constraints/grid.py, fit_rootsift).

tolerance: for each t, at min_votes 2 and span_check 0.05, creator 20 and verifier 64 at
512 px: the tuning positives found (the test-mode manipulations of the 60 tuning originals)
and the false matches among the 260 tuning photos, both directions. The research's rule
picks t: the most positives found with no false match; ties to the smaller t. Pairs that
are the same photograph (known duplicates) are listed so they can be set aside.
"""

import csv
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from image_simprints import recipe as R
from image_simprints import testmode as T

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "corpus"
OUT = ROOT / "src" / "image_simprints" / "projection_v2.f32"
GRID = (12, 16, 20, 24, 28, 32, 36, 40, 48)
STOP_N = (1, 2, 3, 5, 10)  # the hub guard: ignore stored codes agreeing with more than N other photos


def tuning(role: str, splits=("tuning",)) -> list[Path]:
    with (ROOT / "tests" / "corpus" / "manifest.csv").open(encoding="utf-8") as f:
        return [CACHE / r["path"] for r in csv.DictReader(f) if r["split"] in splits and r["role"] == role]


def key(name: str) -> str:
    """"unrelated/u057.jpg:crop50" -> "unrelated/u057": one photo, whatever was made of it."""
    return name.split(":")[0].rsplit(".", 1)[0]


def rootsift_of(path: Path) -> np.ndarray:
    g = R.prepare(R.decode(path), 512)
    _, desc = R.select(g, 64, octave=True)
    return R.rootsift(desc) if desc is not None else np.zeros((0, 128), np.uint8)


def thresholds() -> None:
    with ProcessPoolExecutor() as ex:
        rs = np.concatenate(list(ex.map(rootsift_of, tuning("original") + tuning("unrelated"))))
    raw = np.fromfile(ROOT / "src" / "image_simprints" / "projection.f32", "<f4")
    p = raw[: 128 * 256].reshape(128, 256).astype(np.float64)
    t = np.median(rs.astype(np.float64) @ p, axis=0).astype("<f4")  # float32, so a multiple of 2^-40
    OUT.write_bytes(raw[: 128 * 256].astype("<f4").tobytes() + t.tobytes())
    import hashlib

    print(f"{len(rs)} descriptors; wrote {OUT}; sha256 {hashlib.sha256(OUT.read_bytes()).hexdigest()}")


def tolerance(recipe: int) -> None:
    # The negatives include the 1,000 extra Pixabay photos ("tuning-extra"), so that a
    # false-match rate near one in a million pairs shows; T stays as fitted on "tuning".
    originals, unrelated = tuning("original"), tuning("unrelated", ("tuning", "tuning-extra"))
    common = {"recipe": recipe} if recipe != 1 else {}
    bgs = [unrelated[i % len(unrelated)] for i in range(len(originals))]
    with ProcessPoolExecutor() as ex:
        results = list(ex.map(T.work_original, [(i, p, bgs[i], {}, common) for i, p in enumerate(originals)]))
        plain = list(ex.map(T.work_plain, [(p, {}, common) for p in unrelated]))
    combos = [(t, None) for t in GRID] + ([(t, n) for t in GRID if t >= 24 for n in STOP_N] if recipe == 2 else [])
    log = []
    print(f"recipe {recipe}: {sum(len(r['pairs']) for r in results)} positives; {len(plain)} unrelated photos")
    print("| t | stop codes N | positives found | false matches, pool | false matches, derived/unrelated | genuine (same picture set aside) | genuine pairs |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for t, n in combos:
        over = {"tolerance_t": t}
        res, pl = (results, plain) if n is None else T.guarded(results, plain, [], 20, n, {"recipe": recipe} | over)[:2]
        pool = [r for r in res + pl if r["codes"]["original"]["creator"]["codes"]]
        # The research's negatives too: every derived image with no photometric edit or rotation
        # (identical, crops, collages, second overlap crops) against every unrelated photo, both
        # ways, a collage never against its own background (granular_bench/bench.py).
        derived = [(f"{r['name']}:{k}", r["codes"][k], f"unrelated/{bgs[i].stem}" if k.startswith("collage") else None)
                   for i, r in enumerate(res)
                   for k in r["codes"] if k == "identical" or k.startswith(("crop", "collage"))
                   or (k.startswith("overlap") and not k.endswith("first"))]  # fmt: skip
        unrel = [(r["name"], r["codes"]["original"], None) for r in pl]
        rates, _ = T.positives(res, 20, 64, 512, over)
        found = sum(v[0] for v in rates.values())
        fm, _, hits = T.false_matches(pool, 20, 64, 512, over)
        cross = across(derived, unrel, t, recipe) + across(unrel, derived, t, recipe)
        pairs = sorted({tuple(sorted(h)) for h in hits} | {tuple(sorted(h)) for h in cross})
        genuine = [p for p in pairs if frozenset(key(x) for x in p) not in SAME]
        log.append({"t": t, "stop_codes": n, "found": found, "positives": sum(v[2] for v in rates.values()),
                    "pairs": pairs, "genuine": genuine})  # fmt: skip
        print(f"| {t} | {n or '-'} | {found} | {fm} | {len(cross)} | {len(genuine)} | {'; '.join(f'{a} ~ {b}' for a, b in genuine)} |",
              flush=True)  # fmt: skip
    if len(sys.argv) > 3:
        Path(sys.argv[3]).write_text(json.dumps(log, indent=1), encoding="utf-8")

# Tuning photos that are the same picture (re-uploads, crops, a PNG and an SVG of one symbol):
# the research's KNOWN_DUPLICATES, and u094 ~ u095 by eye. Set aside, as the research did.
SAME = {frozenset(f"unrelated/{x}" for x in p) for p in [
    ("u057", "u058"), ("u064", "u068"), ("u072", "u073"), ("u094", "u095"), ("u111", "u112"), ("u131", "u132"),
    ("u131", "u133"), ("u132", "u133"), ("u138", "u139"), ("u140", "u141"), ("u193", "u194")]}  # fmt: skip


def across(queries, refs, t, recipe) -> list:
    """False matches of each query's verifier codes (64 at 512 px) against every
    reference's creator codes (20). A collage is never scored against its own background
    or a known duplicate of it."""

    def related(bg, other):
        return bg is not None and (bg == key(other) or frozenset((bg, key(other))) in SAME)

    s = R.settings_of({"recipe": recipe, "tolerance_t": t})
    parsed = [R.parse(T.first(c["creator"], 20)) for _, c, _ in refs]
    rc = np.concatenate([p[0] for p in parsed])
    rg = np.concatenate([p[1] for p in parsed])
    owner = np.repeat(np.arange(len(refs)), [len(p[0]) for p in parsed])
    hits = []
    for name, c, bg in queries:
        cq, gq, size_q = R.parse(T.first(c[512], 64))
        if not len(cq):
            continue
        qi, rj = np.nonzero(R.hamming(cq, rc) <= t)
        best, mem = R.votes(qi, rj, owner, gq, rg, len(refs))
        for j in np.flatnonzero(best >= s["min_votes"]):
            if related(bg, refs[j][0]) or related(refs[j][2], name):
                continue
            if R.judge(int(best[j]), mem[j], gq, rg, size_q, parsed[j][2], s)["relationship"] != "none":
                hits.append([name, refs[j][0]])
    return hits


if __name__ == "__main__":
    random.seed(0)
    if sys.argv[1] == "thresholds":
        thresholds()
    else:
        tolerance(int(sys.argv[2]) if len(sys.argv) > 2 else 2)
