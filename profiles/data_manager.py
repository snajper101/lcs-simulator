from typing import Dict, Any
import constants
import json

Data = Dict[str, Dict[str, Any]]

default_data: Data = {
    "stats": {}
}

class DataStore:
    def __init__(self) -> None:
        self.data : Data = self.load()
        self.save()
        
    def load(self) -> Data:
        try:
            with open(constants.DATA_SAVE_FILENAME, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return default_data.copy()
                
    def save(self) -> None:
        with open(constants.DATA_SAVE_FILENAME, "w") as file:
            json.dump(self.data, file)