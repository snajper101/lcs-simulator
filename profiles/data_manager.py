from typing import Dict, Any
from constants import Constants
import json
import os

class DataStore:
    def __init__(self) -> None:
        os.makedirs('/'.join(Constants.DATA_SAVE_FILENAME.split("/")[:-1]), exist_ok=True)

        self.data = self.load()
        self.save()
        
    def load(self) -> Dict[str, Dict[str, Any]]:
        try:
            with open(Constants.DATA_SAVE_FILENAME, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return Constants.DEFAULT_DATA.copy()
                
    def save(self) -> None:
        with open(Constants.DATA_SAVE_FILENAME, "w") as file:
            json.dump(self.data, file)