import importlib
from os import listdir
from os.path import isfile, join
from typing import Tuple, Dict

def get_available_maps() -> list[str]:
    path = "stations"
    return sorted([f.replace(".py", "") for f in listdir(path) if isfile(join(path, f))])

class Maps:
    def __init__(self, map: str):
        self.map_objects = {}
        self.map = map
        self.schema, self.dependencies = self.load_schema(map)

    def load_schema(self, map: str) -> Tuple[Dict, Dict]:
        schema_module = importlib.import_module(f"stations.{map}")
        return getattr(schema_module, "SCHEMA"), getattr(schema_module, "DEPENDENCIES")