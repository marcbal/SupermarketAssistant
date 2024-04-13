from pathlib import Path
from time import sleep
from typing import Union

from es3json import load_es3_json_file
from gamedata import GameData
from savefile import SaveData




class FileWatcher:

    def __init__(self):
        self.gameDataLastUpdate = 0
        self.gameDataRaw = None
        self.gameData: GameData = None

        self.saveDataLastUpdate = 0
        self.saveDataRaw = None
        self.saveData: SaveData = None

    def has_game_data_updated(self) -> bool:
        return FileWatcher.has_file_updated(GameData.get_path(), self.gameDataLastUpdate)
    
    def load_game_data(self):
        oldUpdateTime = self.gameDataLastUpdate
        oldDataRaw = self.gameDataRaw
        oldData = self.gameData
        try:
            path = GameData.get_path()
            time = FileWatcher.get_time_of_file(path)
            if time is None:
                print(f"Error: {path} is not a regular file.")
                return
            self.gameDataLastUpdate = time
            self.gameDataRaw = load_es3_json_file(path)
            self.parse_game_data()
        except:
            self.gameDataLastUpdate = oldUpdateTime
            self.gameDataRaw = oldDataRaw
            self.gameData = oldData
    
    def parse_game_data(self):
        if self.gameDataRaw is None:
            self.gameData = None
        else:
            self.gameData = GameData(self.gameDataRaw)
            self.parse_save_data() # when game data is updated, the save data instance must be updated too (but we don't need to reload the file itself)
    

    def has_save_data_updated(self) -> bool:
        return FileWatcher.has_file_updated(SaveData.get_last_save_path(), self.saveDataLastUpdate)
    
    def load_save_data(self):
        oldUpdateTime = self.saveDataLastUpdate
        oldDataRaw = self.saveDataRaw
        oldData = self.saveData
        try:
            path = SaveData.get_last_save_path()
            time = FileWatcher.get_time_of_file(path)
            if time is None:
                print(f"Error: {path} is not a regular file.")
                return
            self.saveDataLastUpdate = time
            self.saveDataRaw = load_es3_json_file(path)
            self.parse_save_data()
        except:
            self.saveDataLastUpdate = oldUpdateTime
            self.saveDataRaw = oldDataRaw
            self.saveData = oldData

    def parse_save_data(self):
        if self.saveDataRaw is None or self.gameData is None:
            self.saveData = None
        else:
            self.saveData = SaveData(self.saveDataRaw, self.saveDataLastUpdate, self.gameData)

    
    def wait_update(self):
        while True:
            try:
                willReturn = False
                if self.has_game_data_updated():
                    sleep(1)
                    self.load_game_data()
                    willReturn = True
                if self.has_save_data_updated():
                    sleep(1)
                    self.load_save_data()
                    willReturn = True
                if willReturn:
                    return
                sleep(0.3)
            except KeyboardInterrupt:
                exit(0)

    



    

    @staticmethod
    def has_file_updated(path: Path, prevTime: float) -> bool:
        time = FileWatcher.get_time_of_file(path)
        return time is not None and (prevTime == 0 or time > prevTime)

    @staticmethod
    def get_time_of_file(path: Path) -> Union[float, None]:
        """Return the last edit time of the provided file, or None if it's not a regular file."""
        if path is None or not path.is_file():
            return None
        return path.stat().st_mtime
