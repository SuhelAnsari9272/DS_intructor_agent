import json
from typing import List, Set, Dict, Callable

def load_dataset(path: str) -> List[dict]:

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


