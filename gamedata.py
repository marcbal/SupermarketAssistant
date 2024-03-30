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
from animationcurves import AnimationCurve


class BoxSize(Enum):
    """Enum extracted from source code BoxSize.cs."""

    _8x8x8 = 0
    _20x10x7 = 1
    _20x20x10 = 2
    _20x20x20 = 3
    _30x20x20 = 4
    _15x15x15 = 5
    _40x26x26 = 6 # for furniture


class DisplayType(Enum):
    """Enum extracted from source code DisplayType.cs."""

    FREEZER = 0
    FRIDGE = 1
    CRATE = 2
    SHELF = 3




class ProductSO:
    """Static data of a product from the game sources."""

    def __init__(self, soData):
        self.assetId = int(soData["_ES3Ref"])
        self.id = int(soData["ID"])
        self.productName = soData["ProductName"]
        self.brand = soData["ProductBrand"]
        self.productDisplayType = DisplayType(int(soData["ProductDisplayType"]))
        self.productAmountOnPurchase = int(soData["ProductAmountOnPurchase"])
        self.basePrice = float(soData["BasePrice"])
        self.minDynamicPrice = float(soData["MinDynamicPrice"])
        self.maxDynamicPrice = float(soData["MaxDynamicPrice"])
        self.optimumProfitRate = float(soData["OptimumProfitRate"])
        self.maxProfitRate = float(soData["MaxProfitRate"])
        self.boxSize = BoxSize(int(soData["GridLayoutInBox"]["boxSize"]))
        self.productAmountOnDisplay = int(soData["GridLayoutInStorage"]["productCount"])

        self.license: ProductLicenseSO = None
        self.indexInLicense: int = None


class ProductsCollection:

    def __init__(self, data):
        data = data["value"]
        self.byId: dict[int, ProductSO] = {}
        self.byAssetId: dict[int, ProductSO] = {}
        for soData in data:
            productSO: ProductSO = ProductSO(soData)
            self.byId[productSO.id] = productSO
            self.byAssetId[productSO.assetId] = productSO





class ProductLicenseSO:
    """Static data of a product license from the game sources."""

    def __init__(self, soData, products: ProductsCollection):
        self.assetId = int(soData["_ES3Ref"])
        self.id = int(soData["ID"])
        self.requiredPlayerLevel = int(soData["RequiredPlayerLevel"])
        self.purchasingCost = float(soData["PurchasingCost"])
        self.products: list[ProductSO] = []
        for i, pData in enumerate(soData["Products"]):
            pAssetId = int(pData["_ES3Ref"])
            if pAssetId not in products.byAssetId:
                print(f"Product License {self.id} define a product with unknown asset id {pAssetId}")
                continue
            p = products.byAssetId[pAssetId]
            self.products.append(p)
            p.license = self
            p.indexInLicense = i



class ProductLicensesCollection:

    def __init__(self, data, products: ProductsCollection):
        data = data["value"]
        self.byId: dict[int, ProductLicenseSO] = {}
        self.byAssetId: dict[int, ProductLicenseSO] = {}
        for soData in data:
            plSO = ProductLicenseSO(soData, products)
            self.byId[plSO.id] = plSO
            self.byAssetId[plSO.assetId] = plSO





class BoxSO:
    """Static data of a box size from the game sources."""

    def __init__(self, soData):
        self.assetId = int(soData["_ES3Ref"])
        self.id = int(soData["ID"])
        self.boxSize = BoxSize(int(soData["BoxSize"]))
        self.boxCountInStorage = int(soData["GridLayout"]["boxCount"])
        


class BoxesCollection:

    def __init__(self, data):
        data = data["value"]
        self.byId: dict[int, BoxSO] = {}
        self.byBoxSize: dict[BoxSize, BoxSO] = {}
        self.byAssetId: dict[int, BoxSO] = {}
        for soData in data:
            plSO = BoxSO(soData)
            self.byId[plSO.id] = plSO
            self.byBoxSize[plSO.boxSize] = plSO
            self.byAssetId[plSO.assetId] = plSO





class PriceCurves:

    def __init__(self, data):
        data = data["value"]
        self.purchaseChanceCurveForExpensivePrice = AnimationCurve(data["m_PurchaseChanceCurveForExpensivePrice"])
        self.purchaseChanceCurveForCheapPrice = AnimationCurve(data["m_PurchaseChanceCurveForCheapPrice"])



class GameData:

    def __init__(self, data):
        self.rawData = data

        self.products = ProductsCollection(data["products"])
        self.licenses = ProductLicensesCollection(data["licenses"], self.products)
        self.boxes = BoxesCollection(data["boxes"])
        self.priceCurves = PriceCurves(data["price-curves"])
        self.productLocalization: dict[int, str] = data["products-localization"]["value"]


    @staticmethod
    def from_file(path):
        return GameData(load_es3_json_file(path))

    @staticmethod
    def from_workdir():
        return GameData.from_file("game-data.dat")
    
    @staticmethod
    def from_live_game_savedir():
        return GameData.from_file(Path.home().joinpath("AppData", "LocalLow", "Nokta Games", "Supermarket Simulator", "game-data.dat"))


