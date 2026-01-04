from typing import Dict, Any
from constants import Constants
import json
import os

class DataStore:
    def __init__(self) -> None:
        os.makedirs('/'.join(Constants.DATA_SAVE_FILENAME.split("/")[:-1]), exist_ok=True)

        self.data = self.load()
        self.save()
        
    def load(self) -> Dict:
        try:
            with open(Constants.DATA_SAVE_FILENAME, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return Constants.DEFAULT_DATA.copy()
                
    def save(self) -> None:
        with open(Constants.DATA_SAVE_FILENAME, "w") as file:
            json.dump(self.data, file)
            
    def add_result(self, map_name: str, result: int):
        if result < 0:
            return
        if not map_name in self.data['stats']:
            self.data['stats'][map_name] = result
        else:
            self.data['stats'][map_name] = max(self.data['stats'][map_name], result)
        self.save()
        
    def get_results(self) -> Dict[str, int]:
        return self.data['stats']