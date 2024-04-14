# Copyright (c) 2024 Marc Baloup
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
from time import sleep
from typing import Union

from es3json import load_es3_json_file
from gamedata import GameData
from savefile import SaveData




class FileWatcher:

    def __init__(self):
        self.gameDataLastUpdate = 0.0
        self.gameDataRaw = None
        self.gameData: GameData = None

        self.saveDataLastUpdate = 0.0
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
                gameDataFirstLoad = self.gameDataLastUpdate == 0.0
                if self.has_game_data_updated():
                    if not gameDataFirstLoad:
                        sleep(1) # wait to be sure the game have written all the file
                    self.load_game_data()
                    willReturn = True
                saveDataFirstLoad = self.saveDataLastUpdate == 0.0
                if self.has_save_data_updated():
                    if not saveDataFirstLoad:
                        sleep(1) # wait to be sure the game have written all the file
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
