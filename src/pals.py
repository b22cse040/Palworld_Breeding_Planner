from dataclasses import dataclass
import pandas as pd
from typing import Dict, Tuple 
from pydantic import BaseModel, conint

Ability = conint(ge=0, le=4)

ABILITY_COLS = [
    "gathering",
    "generating_electricity",
    "handiwork",
    "kindling",
    "lumbering",
    "medicine_production",
    "mining",
    "planting",
    "transporting",
    "watering",
]

class Pal(BaseModel, frozen=True):
    id: int
    key: str 
    name: str 
    rarity: int 
    types: Tuple[str, ...]

    ## Work abilities
    gathering: Ability 
    generating_electricity: Ability
    handiwork: Ability
    kindling: Ability
    lumbering: Ability
    medicine_production: Ability
    mining: Ability
    planting: Ability
    transporting: Ability
    watering: Ability

    def ability_map(self) -> Dict[str, int]:
        return {
            "gathering": self.gathering,
            "generating_electricity": self.generating_electricity,
            "handiwork": self.handiwork,
            "kindling": self.kindling,
            "lumbering": self.lumbering,
            "medicine_production": self.medicine_production,
            "mining": self.mining,
            "planting": self.planting,
            "transporting": self.transporting,
            "watering": self.watering,
        }
    
    def score(self, ability: str) -> int:
        return self.ability_map().get(ability, 0)
    
    def __str__(self):
        return f"{self.name}({self.key})"
    
def row_to_pal(row: pd.Series) -> Pal:
    return Pal(
        id=int(row["id"]),
        key=row["key"],
        name=row['name'],
        rarity=int(row["rarity"]),
        types=tuple(t["name"] for t in row["types"]),
        **{a: int(row[a]) for a in ABILITY_COLS}
    )

def get_pal_data(pal_name: str, pal_by_name: Dict[str, Pal]) -> Pal:
    pal = pal_by_name.get(pal_name.lower())
    if pal is None:
        raise ValueError(f"Unknown pal: {pal_name}")
    return pal

if __name__ == "__main__":
    path = "../data/pals.parquet"
    df = pd.read_parquet(path)

    pal_by_key: Dict[str, Pal] = {
        row["key"]: row_to_pal(row)
        for _, row in df.iterrows()
    }

    pal_by_name: Dict[str, Pal] = {
        row["name"].lower(): row_to_pal(row)
        for _, row in df.iterrows()
    }

    print(pal_by_key["080"])
    print(pal_by_name["jormuntide"])