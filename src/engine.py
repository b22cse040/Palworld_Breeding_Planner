import pandas as pd
from typing import List, Dict, Tuple
from pathlib import Path

from src.pals import Pal, row_to_pal
from src.breeding_graph import BreedingGraph

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def is_better_graph(a: BreedingGraph, b: BreedingGraph) -> bool:
    if a.depth() != b.depth():
        return a.depth() < b.depth()
    return a.unique_pal_count() < b.unique_pal_count()


def get_breeding_combinations(
    pals: List[Pal],
    depth: int = 3,
) -> Dict[Pal, BreedingGraph]:

    breed_df = pd.read_parquet(DATA_DIR / "breeding.parquet")
    BREED_LOOKUP = {
        tuple(sorted((r.p1, r.p2))): r.child_id
        for r in breed_df.itertuples()
    }

    df = pd.read_parquet(DATA_DIR / "pals.parquet")
    pal_by_key = {
        row["key"]: row_to_pal(row)
        for _, row in df.iterrows()
    }

    known = {p.key: p for p in pals}
    reachable = set(known.keys())
    best_graphs: Dict[str, BreedingGraph] = {}

    for _ in range(depth):
        next_gen = set()
        all_pals = list(known.values())

        for i in range(len(all_pals)):
            for j in range(i + 1, len(all_pals)):
                p1, p2 = all_pals[i], all_pals[j]
                if p1.key not in reachable or p2.key not in reachable:
                    continue

                child_key = BREED_LOOKUP.get(tuple(sorted((p1.key, p2.key))))
                if not child_key:
                    continue

                child = pal_by_key.get(child_key)
                if not child:
                    continue

                candidate = BreedingGraph(child)
                candidate.add_breeding(p1, p2, child)

                if p1.key in best_graphs:
                    candidate.merge(best_graphs[p1.key])
                if p2.key in best_graphs:
                    candidate.merge(best_graphs[p2.key])

                if (
                    child.key not in best_graphs
                    or is_better_graph(candidate, best_graphs[child.key])
                ):
                    best_graphs[child.key] = candidate

                if child.key not in known:
                    known[child.key] = child
                    reachable.add(child.key)
                    next_gen.add(child.key)

        if not next_gen:
            break

    return {pal_by_key[k]: g for k, g in best_graphs.items()}


def sort_breeding_results(results, by, descending=True):
    return sorted(
        results.items(),
        key=lambda x: getattr(x[0], by),
        reverse=descending
    )