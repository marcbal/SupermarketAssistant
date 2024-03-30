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
from enum import Enum
from es3json import load_es3_json_file


class PlayerPaymentType(Enum):
    RENT = 0
    BILL = 1
    LOAN = 2
    STAFF = 3

class Expense:
    def __init__(self, data):
        self.date = int(data["Date"])
        self.amount = float(data["Amount"])
        self.paymentType = PlayerPaymentType(int(data["PaymentType"]))
        self.latePaymentFee = float(data["LatePaymentFee"])

class SaveDataExpenses:
    def __init__(self, data):
        data = data["value"]
        self.bills:          list[Expense] = [Expense(d) for d in data["Bills"]]
        self.rents:          list[Expense] = [Expense(d) for d in data["Rents"]]
        self.loanRepayments: list[Expense] = [Expense(d) for d in data["LoanRepayments"]]



class ProductPrice:
    def __init__(self, data):
        self.productId = int(data["ProductID"])
        self.price = float(data["Price"])
        

class SaveDataPrice:
    def __init__(self, data):
        data = data["value"]
        self.prices:            list[ProductPrice] = [ProductPrice(d) for d in data["Prices"]]
        self.pricesSetByPlayer: list[ProductPrice] = [ProductPrice(d) for d in data["PricesSetByPlayer"]]
        self.averageCosts:      list[ProductPrice] = [ProductPrice(d) for d in data["AverageCosts"]]
        self.dailyPriceChanges: list[ProductPrice] = [ProductPrice(d) for d in data["DailyPriceChanges"]]
        self.previousPrices:    list[ProductPrice] = [ProductPrice(d) for d in data["PreviousPrices"]]


class Box:
    def __init__(self, data):
        self.isOpen = bool(data["IsOpen"])
        self.productId = int(data["ProductID"])
        self.productCount = int(data["ProductCount"])


class DisplaySlot:
    def __init__(self, data):
        # If one day you can put multiple product type in the same slot:
        #self.products: dict[int, int] = data["Products"]

        self.productId: int = None
        self.productCount: int = 0
        # Because there is only one type of product in a display slot:
        for k, v in data["Products"].items():
            self.productId = k
            self.productCount = v
            return


class Display:
    def __init__(self, data):
        self.displaySlots = [DisplaySlot(d) for d in data["DisplaySlots"]]
        self.furnitureId = int(data["FurnitureID"])


class RackSlot:
    def __init__(self, data):
        self.productId = int(data["ProductID"]) if data["ProductID"] != -1 else None
        self.rackedBoxDatas = [Box(d) for d in data["RackedBoxDatas"]]

class Rack:
    def __init__(self, data):
        self.rackSlots = [RackSlot(d) for d in data["RackSlots"]]
        self.furnitureId = int(data["FurnitureID"])


class SaveDataProgression:
    def __init__(self, data):
        data = data["value"]
        self.unlockedLicenses: list[int] = data["UnlockedLicenses"]
        self.money = float(data["Money"])
        self.boxDatas: list[Box] = [Box(d) for d in data["BoxDatas"]]
        self.displayDatas: list[Display] = [Display(d) for d in data["DisplayDatas"]]
        self.rackDatas: list[Rack] = [Rack(d) for d in data["RackDatas"]]
        self.currentTime = data["CurrentTime"]
        self.currentDay = data["CurrentDay"]
        self.completedCheckoutCount = data["CompletedCheckoutCount"]
        self.currentStorePoint = data["CurrentStorePoint"]
        self.currentStoreLevel = data["CurrentStoreLevel"]
        self.storeUpgradeLevel = data["StoreUpgradeLevel"]
        self.isStoreOpen = data["IsStoreOpen"]
        pass


class SaveData:

    def __init__(self, data):
        self.data = data

        self.expenses = SaveDataExpenses(data["Expenses"])
        self.price = SaveDataPrice(data["Price"])
        self.progression = SaveDataProgression(data["Progression"])


    @staticmethod
    def from_file(path):
        return SaveData(load_es3_json_file(path))

    @staticmethod
    def from_workdir():
        return SaveData.from_file("SaveFile.es3")
    
    @staticmethod
    def from_live_game_savedir():
        return SaveData.from_file(Path.home().joinpath("AppData", "LocalLow", "Nokta Games", "Supermarket Simulator", "SaveFile.es3"))


