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





class ProductSO:
    """Static data of a product from the game sources."""

    def __init__(self, soData, boxSizeEnum: type[Enum], displayTypeEnum: type[Enum], productCategoryEnum: type[Enum]):
        self.assetId = int(soData["_ES3Ref"])
        self.id = int(soData["ID"])
        self.productName = soData["ProductName"]
        self.brand = soData["ProductBrand"]
        self.productDisplayType = displayTypeEnum(int(soData["ProductDisplayType"]))
        self.category = productCategoryEnum(int(soData["Category"]))
        self.productAmountOnPurchase = int(soData["ProductAmountOnPurchase"])
        self.basePrice = float(soData["BasePrice"])
        self.minDynamicPrice = float(soData["MinDynamicPrice"])
        self.maxDynamicPrice = float(soData["MaxDynamicPrice"])
        self.optimumProfitRate = float(soData["OptimumProfitRate"])
        self.maxProfitRate = float(soData["MaxProfitRate"])
        self.boxSize = boxSizeEnum(int(soData["GridLayoutInBox"]["boxSize"]))
        self.productAmountOnDisplay = int(soData["GridLayoutInStorage"]["productCount"])

        self.license: ProductLicenseSO = None
        self.indexInLicense: int = None


class ProductsCollection:

    def __init__(self, data, boxSizeEnum: type[Enum], displayTypeEnum: type[Enum], productCategoryEnum: type[Enum]):
        data = data["value"]
        self.byId: dict[int, ProductSO] = {}
        self.byAssetId: dict[int, ProductSO] = {}
        for soData in data:
            productSO: ProductSO = ProductSO(soData, boxSizeEnum, displayTypeEnum, productCategoryEnum)
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

    def __init__(self, soData, boxSizeEnum: type[Enum]):
        self.assetId = int(soData["_ES3Ref"])
        self.id = int(soData["ID"])
        self.boxSize = boxSizeEnum(int(soData["BoxSize"]))
        self.boxCountInStorage = int(soData["GridLayout"]["boxCount"])
        


class BoxesCollection:

    def __init__(self, data, boxSizeEnum: type[Enum]):
        data = data["value"]
        self.byId: dict[int, BoxSO] = {}
        self.byBoxSize: dict[Enum, BoxSO] = {}
        self.byAssetId: dict[int, BoxSO] = {}
        for soData in data:
            plSO = BoxSO(soData, boxSizeEnum)
            self.byId[plSO.id] = plSO
            self.byBoxSize[plSO.boxSize] = plSO
            self.byAssetId[plSO.assetId] = plSO





class CashierSO:
    """Static data of a cashier from the game sources."""

    def __init__(self, soData):
        self.assetId = int(soData["_ES3Ref"])
        self.id = int(soData["ID"])
        self.cashierName = str(soData["CashierName"])
        self.dailyWage = float(soData["DailyWage"])
        self.hiringCost = float(soData["HiringCost"])
        self.checkoutGoalToUnlock = int(soData["CheckoutGoalToUnlock"])
        self.requiredStoreLevel = int(soData["RequiredStoreLevel"])
        


class CashiersCollection:

    def __init__(self, data):
        data = data["value"]
        self.byId: dict[int, CashierSO] = {}
        self.byAssetId: dict[int, CashierSO] = {}
        for soData in data:
            cSO = CashierSO(soData)
            self.byId[cSO.id] = cSO
            self.byAssetId[cSO.assetId] = cSO





class PriceCurves:

    def __init__(self, data):
        data = data["value"]
        self.purchaseChanceCurveForExpensivePrice = AnimationCurve(data["m_PurchaseChanceCurveForExpensivePrice"])
        self.purchaseChanceCurveForCheapPrice = AnimationCurve(data["m_PurchaseChanceCurveForCheapPrice"])



class GameData:

    def __init__(self, data):
        self.rawData = data

        self.boxSizeEnum = Enum('BoxSize', data["boxsize-enum"]["value"])
        self.playerPaymentTypeEnum = Enum('PlayerPaymentType', data["playerpaymenttype-enum"]["value"])
        self.displayTypeEnum = Enum('DisplayType', data["displaytype-enum"]["value"])
        self.productCategoryEnum = Enum('ProductCategory', data["productcategory-enum"]["value"])
        self.products = ProductsCollection(data["products"], self.boxSizeEnum, self.displayTypeEnum, self.productCategoryEnum)
        self.licenses = ProductLicensesCollection(data["licenses"], self.products)
        self.boxes = BoxesCollection(data["boxes"], self.boxSizeEnum)
        self.cashiers = CashiersCollection(data["cashiers"])
        self.priceCurves = PriceCurves(data["price-curves"])
        self.productLocalization: dict[int, str] = data["products-localization"]["value"]
        self.licensesLocalization: dict[int, str] = data["licenses-localization"]["value"]
        self.playerPaymentTypeLocalization: dict[int, str] = data["playerpaymenttype-localization"]["value"]
        for k in self.playerPaymentTypeLocalization.keys():
            self.playerPaymentTypeLocalization[k] = self.playerPaymentTypeLocalization[k].strip(" :")
        self.displayTypeLocalization: dict[int, str] = data["displaytype-localization"]["value"]


    @staticmethod
    def from_file(path):
        return GameData(load_es3_json_file(path))

    @staticmethod
    def from_workdir():
        return GameData.from_file("game-data.dat")
    
    @staticmethod
    def from_live_game_savedir():
        return GameData.from_file(Path.home().joinpath("AppData", "LocalLow", "Nokta Games", "Supermarket Simulator", "game-data.dat"))


