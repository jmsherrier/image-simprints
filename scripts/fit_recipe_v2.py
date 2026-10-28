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


def tuning(role: str) -> list[Path]:
    with (ROOT / "tests" / "corpus" / "manifest.csv").open(encoding="utf-8") as f:
        return [CACHE / r["path"] for r in csv.DictReader(f) if r["split"] == "tuning" and r["role"] == role]


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
    originals, unrelated = tuning("original"), tuning("unrelated")
    common = {"recipe": recipe} if recipe != 1 else {}
    bgs = [unrelated[i % len(unrelated)] for i in range(len(originals))]
    with ProcessPoolExecutor() as ex:
        results = list(ex.map(T.work_original, [(i, p, bgs[i], {}, common) for i, p in enumerate(originals)]))
        plain = list(ex.map(T.work_plain, [(p, {}, common) for p in unrelated]))
    pool = [r for r in results + plain if r["codes"]["original"]["creator"]["codes"]]
    # The research's negatives too: every derived image with no photometric edit or rotation
    # (identical, crops, collages, second overlap crops) against every unrelated photo, both
    # ways, a collage never against its own background (granular_bench/bench.py).
    derived = [(f"{res['name']}:{n}", res["codes"][n], bgs[i].stem if n.startswith("collage") else None)
               for i, res in enumerate(results)
               for n in res["codes"] if n == "identical" or n.startswith(("crop", "collage"))
               or (n.startswith("overlap") and not n.endswith("first"))]  # fmt: skip
    unrel = [(f"unrelated/{r['name'].split('/')[-1]}", r["codes"]["original"], None) for r in plain]
    print(f"recipe {recipe}: {sum(len(r['pairs']) for r in results)} positives; {len(pool)} photos in the pool "
          f"({len(pool) * (len(pool) - 1)} ordered pairs); {2 * len(derived) * len(unrel)} derived/unrelated pairs")
    print("| t | positives found | false matches, pool | false matches, derived/unrelated | genuine (same picture set aside) | genuine pairs |")
    print("| --- | --- | --- | --- | --- | --- |")
    for t in GRID:
        rates, _ = T.positives(results, 20, 64, 512, {"tolerance_t": t})
        found = sum(v[0] for v in rates.values())
        fm, _, hits = T.false_matches(pool, 20, 64, 512, {"tolerance_t": t})
        cross = across(derived, unrel, t, recipe) + across(unrel, derived, t, recipe)
        pairs = {tuple(sorted(h)) for h in hits} | {tuple(sorted(h)) for h in cross}
        genuine = sorted(p for p in pairs if frozenset(x.split("/")[-1].split(":")[0][:4] for x in p) not in SAME)
        print(f"| {t} | {found} | {fm} | {len(cross)} | {len(genuine)} | {'; '.join(f'{a} ~ {b}' for a, b in genuine)} |",
              flush=True)  # fmt: skip


# Tuning photos that are the same picture (re-uploads, crops, a PNG and an SVG of one symbol):
# the research's KNOWN_DUPLICATES, and u094 ~ u095 by eye. Set aside, as the research did.
SAME = {frozenset(p) for p in [("u057", "u058"), ("u064", "u068"), ("u072", "u073"), ("u094", "u095"),
                               ("u111", "u112"), ("u131", "u132"), ("u131", "u133"), ("u132", "u133"),
                               ("u138", "u139"), ("u140", "u141"), ("u193", "u194")]}  # fmt: skip


def across(queries, refs, t, recipe) -> list:
    """False matches of each query's verifier codes (64 at 512 px) against every
    reference's creator codes (20). A collage is never scored against its own background
    or a known duplicate of it."""

    def key(name):
        return name.split("/")[-1].split(":")[0][:4]

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
