import importlib
from os import listdir
from os.path import isfile, join

def get_available_maps() -> list[str]:
    path = "stations"
    return [f.replace(".py", "") for f in listdir(path) if isfile(join(path, f))]

class Maps:
    def __init__(self, map: str):
        self.map_objects = {}
        self.map = map
        self.schema = self.load_schema(map)

    def load_schema(self, map: str) -> dict:
        schema_module = importlib.import_module(f"stations/{map}.py")
        return schema_module

    def load_map_data():
        pass