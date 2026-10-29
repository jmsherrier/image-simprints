"""Fit recipe 2's constants and the hub guards on the research TUNING split only
(tests/corpus/manifest.csv; fetch it with `image-simprints fetch-corpus`).

    python scripts/fit_recipe_v2.py thresholds         # writes src/image_simprints/projection_v2.f32
    python scripts/fit_recipe_v2.py tolerance 2 [log]  # t, and guard (a), per t and N
    python scripts/fit_recipe_v2.py hubs [log]         # guard (b): hub lists, per t and N

thresholds: the projection P is recipe 1's (seed 20261013); T is the per-dimension median
of P applied to the RootSIFT of every "tuning" original and unrelated photo's top 64
keypoints at 512 px, descriptors at each keypoint's octave. As the research fitted recipe
1's T (granular_constraints/grid.py, fit_rootsift).

Every table scores creator 20 and verifier 64 at 512 px (min_votes 2, span_check 0.05):
positives are the test-mode manipulations of the 60 tuning originals; negatives are the
unrelated photos against each other, and every derived image with no edit against every
unrelated photo, both ways (the research's negatives). The research's rule picks: the most
positives found with no genuine false match; ties to the smaller t, then the larger N.
Pairs that are the same picture are set aside (SAME) after an eye check.

tolerance: negatives include the 1,000 "tuning-extra" photos (about 3.5 million pairs).
Guard (a): stored codes that agree with codes of more than N other photos in the corpus
are ignored (recipe.mark_stop_codes).

hubs: guard (b). The hub list is the "tuning-extra" photos' stored codes that agree with
codes of more than N other "tuning-extra" photos; a creator skips keypoints whose code is
within t of a hub code. Scored on the "tuning" split alone, so the list never sees the
photos it is scored on.
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
STOP_N = (1, 2, 3, 5, 10)
TMAX = max(GRID)

# Tuning photos that are the same picture (re-uploads, crops, a PNG and an SVG of one
# symbol): the research's KNOWN_DUPLICATES, and the rest by eye. Set aside, as the research did.
SAME = {frozenset(p) for p in [(f"unrelated/{a}", f"unrelated/{b}") for a, b in [
    ("u057", "u058"), ("u064", "u068"), ("u072", "u073"), ("u094", "u095"), ("u111", "u112"), ("u131", "u132"),
    ("u131", "u133"), ("u132", "u133"), ("u138", "u139"), ("u140", "u141"), ("u193", "u194")]]}  # fmt: skip


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
    import hashlib

    with ProcessPoolExecutor() as ex:
        rs = np.concatenate(list(ex.map(rootsift_of, tuning("original") + tuning("unrelated"))))
    raw = np.fromfile(ROOT / "src" / "image_simprints" / "projection.f32", "<f4")
    p = raw[: 128 * 256].reshape(128, 256).astype(np.float64)
    t = np.median(rs.astype(np.float64) @ p, axis=0).astype("<f4")  # float32, so a multiple of 2^-40
    OUT.write_bytes(raw[: 128 * 256].astype("<f4").tobytes() + t.tobytes())
    print(f"{len(rs)} descriptors; wrote {OUT}; sha256 {hashlib.sha256(OUT.read_bytes()).hexdigest()}")


def codes(recipe: int):
    """Codes of the tuning originals (with their manipulations), the tuning unrelated
    photos, and the tuning-extra photos; and each original's collage background."""
    originals, unrelated = tuning("original"), tuning("unrelated")
    extra = tuning("unrelated", ("tuning-extra",))
    common = {"recipe": recipe}
    bgs = [unrelated[i % len(unrelated)] for i in range(len(originals))]
    with ProcessPoolExecutor() as ex:
        results = list(ex.map(T.work_original, [(i, p, bgs[i], {}, common) for i, p in enumerate(originals)]))
        plain = list(ex.map(T.work_plain, [(p, {}, common) for p in unrelated]))
        xs = list(ex.map(T.work_plain, [(p, {}, common) for p in extra]))
    return results, plain, xs, bgs


def evaluate(results, plain, bgs, t, recipe) -> dict:
    """The reference definition of a tuning row (slow: every distance, every time); Negatives is the fast one."""
    over = {"tolerance_t": t}
    pool = [r for r in results + plain if r["codes"]["original"]["creator"]["codes"]]
    derived = [(f"{r['name']}:{k}", r["codes"][k], f"unrelated/{bgs[i].stem}" if k.startswith("collage") else None)
               for i, r in enumerate(results)
               for k in r["codes"] if k == "identical" or k.startswith(("crop", "collage"))
               or (k.startswith("overlap") and not k.endswith("first"))]  # fmt: skip
    unrel = [(r["name"], r["codes"]["original"], None) for r in plain]
    rates, _ = T.positives(results, 20, 64, 512, over)
    _, n_pool, hits = T.false_matches(pool, 20, 64, 512, over)
    cross = across(derived, unrel, t, recipe) + across(unrel, derived, t, recipe)
    pairs = sorted({tuple(sorted(h)) for h in hits} | {tuple(sorted(h)) for h in cross})
    return {"found": sum(v[0] for v in rates.values()), "positives": sum(v[2] for v in rates.values()),
            "negative_pairs": n_pool + 2 * len(derived) * len(unrel), "pairs": pairs,
            "genuine": [p for p in pairs if frozenset(key(x) for x in p) not in SAME]}  # fmt: skip


def table(rows, log) -> None:
    print("| t | N | positives found | negative pairs | false-match pairs | genuine | genuine pairs |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        print(f"| {r['t']} | {r['n'] or '-'} | {r['found']} of {r['positives']} | {r['negative_pairs']:,} | {len(r['pairs'])} | "
              f"{len(r['genuine'])} | {'; '.join(f'{a} ~ {b}' for a, b in r['genuine'])} |", flush=True)  # fmt: skip
    if log:
        Path(log).write_text(json.dumps(rows, indent=1), encoding="utf-8")


class Negatives:
    """The negatives of evaluate(), scored fast: every code pair within TMAX between a
    query's verifier codes and a reference's whole 64-code creator run is found once;
    a setting then only says which of those 64 codes are stored (the first 20, less any
    a guard drops) and filters by t. Same vote and judgement as evaluate()."""

    def __init__(self, results, plain, bgs, recipe):
        self.recipe = recipe
        base = {r["name"]: r for r in results + plain}
        pool = [r["name"] for r in results + plain if r["codes"]["original"]["creator"]["codes"]]
        derived = [(f"{r['name']}:{k}", f"unrelated/{bgs[i].stem}" if k.startswith("collage") else None)
                   for i, r in enumerate(results)
                   for k in r["codes"] if k == "identical" or k.startswith(("crop", "collage"))
                   or (k.startswith("overlap") and not k.endswith("first"))]  # fmt: skip
        unrel = [(r["name"], None) for r in plain]

        def run(name, size):
            img, _, k = name.partition(":")
            c = base[img]["codes"][k or "original"]
            return c["creator"] if size == "creator" else c[512]

        self.run = run
        self.n_pairs = len(pool) * (len(pool) - 1) + 2 * len(derived) * len(unrel)
        self.blocks = [self._block([(n, None) for n in pool], [(n, None) for n in pool], True),
                       self._block(derived, unrel, False), self._block(unrel, derived, False)]

    def _block(self, queries, refs, pool):
        parsed = [R.parse(self.run(n, "creator")) for n, _ in refs]
        b = {"queries": queries, "refs": refs, "pool": pool, "sizes": [p[2] for p in parsed],
             "codes": np.concatenate([p[0] for p in parsed]), "geo": np.concatenate([p[1] for p in parsed]),
             "owner": np.repeat(np.arange(len(refs)), [len(p[0]) for p in parsed]),
             "rank": np.concatenate([[c["chunk_idx"] for c in self.run(n, "creator")["codes"]] for n, _ in refs])}  # fmt: skip
        b["hits"] = []
        for n, _ in queries:
            cq, gq, size_q = R.parse(T.first(self.run(n, 512), 64))
            found = [np.nonzero(R.hamming(cq, b["codes"][k : k + T.CHUNK]) <= TMAX) for k in range(0, len(b["codes"]), T.CHUNK)]
            qi = np.concatenate([f[0] for f in found]).astype(int) if len(cq) else np.zeros(0, int)
            rj = np.concatenate([f[1] + k * T.CHUNK for k, f in enumerate(found)]).astype(int) if len(cq) else np.zeros(0, int)
            d = np.bitwise_count(cq[qi] ^ b["codes"][rj]).sum(axis=1) if len(qi) else np.zeros(0, int)
            b["hits"].append((qi, rj, d, gq, size_q))
        return b

    def score(self, creators: dict, t: int) -> list:
        """False-match pairs when each reference stores creators[name]'s first 20 codes."""
        s = R.settings_of({"recipe": self.recipe, "tolerance_t": t})
        out = []
        for b in self.blocks:
            stored = np.zeros(len(b["codes"]), bool)
            for j, (n, _) in enumerate(b["refs"]):
                keep = {c["chunk_idx"] for c in T.first(creators[n], 20)["codes"] if not c.get("stop")}
                mine = b["owner"] == j
                stored[mine] = np.isin(b["rank"][mine], list(keep))
            for q, ((qname, qbg), (qi, rj, d, gq, size_q)) in enumerate(zip(b["queries"], b["hits"], strict=True)):
                keep = (d <= t) & stored[rj]
                if b["pool"]:
                    keep &= b["owner"][rj] != q
                if not keep.any():
                    continue
                best, mem = R.votes(qi[keep], rj[keep], b["owner"], gq, b["geo"], len(b["refs"]))
                for j in np.flatnonzero(best >= s["min_votes"]):
                    rname, rbg = b["refs"][j]
                    if related(qbg, rname) or related(rbg, qname):
                        continue
                    if R.judge(int(best[j]), mem[j], gq, b["geo"], size_q, b["sizes"][j], s)["relationship"] != "none":
                        out.append(tuple(sorted((qname, rname))))
        return sorted(set(out))


def creators_of(results, plain) -> dict:
    out = {r["name"]: r["codes"]["original"]["creator"] for r in results + plain}
    out |= {f"{r['name']}:{k}": c["creator"] for r in results for k, c in r["codes"].items()}
    return out


def row(t, n, res, pl, neg: Negatives) -> dict:
    rates, _ = T.positives(res, 20, 64, 512, {"tolerance_t": t})
    pairs = [list(p) for p in neg.score(creators_of(res, pl), t)]
    return {"t": t, "n": n, "found": sum(v[0] for v in rates.values()), "positives": sum(v[2] for v in rates.values()),
            "negative_pairs": neg.n_pairs, "pairs": pairs,
            "genuine": [p for p in pairs if frozenset(key(x) for x in p) not in SAME]}  # fmt: skip


def tolerance(recipe: int, log=None) -> None:
    results, plain, xs, bgs = codes(recipe)
    plain = plain + xs
    neg = Negatives(results, plain, bgs, recipe)
    rows = []
    for t, n in [(t, None) for t in GRID] + ([(t, n) for t in GRID if t >= 24 for n in STOP_N] if recipe == 2 else []):
        res, pl = (results, plain) if n is None else T.guarded(results, plain, [], 20, n, {"recipe": recipe, "tolerance_t": t})[:2]
        rows.append(row(t, n, res, pl, neg))
        print(f"t {t}, N {n}: {rows[-1]['found']} found, {len(rows[-1]['genuine'])} genuine", flush=True)
    table(rows, log)


def hub_list(xs, t, n) -> list[str]:
    """Stored codes (top 20) of the tuning-extra photos that agree with codes of more
    than n other tuning-extra photos."""
    stored = [T.first(r["codes"]["original"]["creator"], 20) for r in xs]
    marked = R.mark_stop_codes(stored, n, {"recipe": 2, "tolerance_t": t})
    return sorted({c["code"] for r in marked for c in r["codes"] if c.get("stop")})


def hubs(log=None) -> None:
    results, plain, xs, bgs = codes(2)
    neg = Negatives(results, plain, bgs, 2)
    rows = []
    for t in (24, 28, 32, 36, 40):
        for n in STOP_N:
            hub = hub_list(xs, t, n)
            arr = np.array([np.frombuffer(bytes.fromhex(h), ">u8") for h in hub], np.uint64).reshape(-1, 4)
            res, pl, _ = T.skip_hubs(results, plain, [], arr, t)
            rows.append(row(t, n, res, pl, neg) | {"hubs": len(hub), "hub_codes": hub})
            print(f"t {t}, N {n}: {len(hub)} hub codes, {rows[-1]['found']} found, {len(rows[-1]['genuine'])} genuine", flush=True)
    table(rows, log)


def related(bg, other) -> bool:
    """A collage and its own background, or a known duplicate of it."""
    return bg is not None and (bg == key(other) or frozenset((bg, key(other))) in SAME)


def across(queries, refs, t, recipe) -> list:
    """False matches of each query's verifier codes (64 at 512 px) against every
    reference's creator codes (20). A collage is never scored against its own background
    or a known duplicate of it."""

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
    elif sys.argv[1] == "hubs":
        hubs(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        tolerance(int(sys.argv[2]) if len(sys.argv) > 2 else 2, sys.argv[3] if len(sys.argv) > 3 else None)
