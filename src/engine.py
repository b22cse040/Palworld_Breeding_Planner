import pandas as pd
from typing import List, Dict, Tuple

from pals import Pal, row_to_pal
from breeding_graph import BreedingGraph


# --------------------------------------------------
# Graph comparison logic
# --------------------------------------------------

def is_better_graph(a: BreedingGraph, b: BreedingGraph) -> bool:
    """
    Return True if graph a is better than graph b
    Priority:
      1. Smaller depth
      2. Fewer unique pals (tie-breaker)
    """
    if a.depth() != b.depth():
        return a.depth() < b.depth()

    return a.unique_pal_count() < b.unique_pal_count()


# --------------------------------------------------
# Breeding engine
# --------------------------------------------------

def get_breeding_combinations(
    pals: List[Pal],
    depth: int = 3,
    BREED_LOOKUP: Dict[Tuple[str, str], str] | None = None,
    breeding_file_path: str = "../data/breeding.parquet",
    pals_file_path: str = "../data/pals.parquet",
) -> Dict[Pal, BreedingGraph]:

    if BREED_LOOKUP is None:
        breed_df = pd.read_parquet(breeding_file_path)

        BREED_LOOKUP = {
            (r.p1, r.p2): r.child_id
            for r in breed_df.itertuples()
        }

    df = pd.read_parquet(pals_file_path)

    pal_by_key: Dict[str, Pal] = {
        row["key"]: row_to_pal(row)
        for _, row in df.iterrows()
    }

    known_pals: Dict[str, Pal] = {p.key: p for p in pals}
    best_graphs: Dict[str, BreedingGraph] = {}
    reachable: set[str] = {p.key for p in pals}  # generation 0

    for _ in range(depth):
        next_generation = set()
        all_pals = list(known_pals.values())

        for i in range(len(all_pals)):
            for j in range(i + 1, len(all_pals)):
                p1, p2 = all_pals[i], all_pals[j]

                if p1.key not in reachable or p2.key not in reachable:
                  continue

                parent_pair = tuple(sorted((p1.key, p2.key)))
                child_key = BREED_LOOKUP.get(parent_pair)

                if not child_key:
                    continue

                child = pal_by_key.get(child_key)
                if child is None:
                    continue

                if child.key == p1.key or child.key == p2.key:
                  if p1.key not in reachable or p2.key not in reachable:
                    continue

                candidate = BreedingGraph(child)
                candidate.add_breeding(p1, p2, child)

                if p1.key in best_graphs:
                  if not best_graphs[p1.key].contains(child):
                    candidate.merge(best_graphs[p1.key])

                if p2.key in best_graphs:
                  if not best_graphs[p2.key].contains(child):
                    candidate.merge(best_graphs[p2.key])

                if (
                    child.key not in best_graphs
                    or is_better_graph(candidate, best_graphs[child.key])
                ):
                    best_graphs[child.key] = candidate

                if child.key not in known_pals:
                    known_pals[child.key] = child
                    next_generation.add(child)
                    reachable.add(child.key)

        if not next_generation:
            break

    return {
        pal_by_key[k]: graph
        for k, graph in best_graphs.items()
    }


def sort_breeding_results(
    results: Dict[Pal, BreedingGraph],
    by: str,
    descending: bool = True
) -> List[Tuple[Pal, BreedingGraph]]:
  """
  Sort breeding results by a Pal ability.

  Returns a list of (Pal, BreedingGraph) tuples.
  """
  if not results:
    return []

  if not hasattr(next(iter(results.keys())), by):
    raise ValueError(f"Invalid ability for sorting: {by}")

  return sorted(
    results.items(),
    key=lambda item: getattr(item[0], by),
    reverse=descending
  )

if __name__ == "__main__":
    df = pd.read_parquet("../data/pals.parquet")

    pal_by_name = {
        row["name"].lower(): row_to_pal(row)
        for _, row in df.iterrows()
    }

    pals_name = ["Gorirat", "Chikipi"]

    pals = [pal_by_name[name.lower()] for name in pals_name]

    results = get_breeding_combinations(
      pals=pals,
      depth=6
    )

    sorted_results = sort_breeding_results(
      results,
      by="mining",
      descending=True
    )

    for pal, graph in sorted_results[:5]:
      print(
        f"{pal.name:15} | "
        f"mining={pal.mining} | "
        f"depth={graph.depth()} | "
        f"unique_pals={graph.unique_pal_count()}"
      )

    if sorted_results:
      best_pal, best_graph = sorted_results[3]
      best_graph.visualize()