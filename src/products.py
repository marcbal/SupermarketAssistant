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

import math

from animationcurves import inverse_lerp, lerp, local_max
from gamedata import GameData, ProductSO
from savefile import SaveData, DisplaySlot, RackSlot, Box


class Product:

    def __init__(self, pSO: ProductSO, productsData: "ProductsData"):
        self.productSO = pSO
        self.productsData = productsData
        self.localizedName = productsData.gameData.productLocalization[pSO.id]

        self.licenseUnlockIndex: int = None

        self.currentPrice: float = None
        self.sellPriceSetByPlayer: float = None
        self.averageCosts: float = None
        self.dailyPriceChange: float = None
        self.previousPrice: float = None

        self.displaySlots: list[DisplaySlot] = []
        self.rackSlots: list[RackSlot] = []
        self.unstoredBoxes: list[Box] = []
    
    def get_by_license_sort_key(self):
        if self.licenseUnlockIndex is None:
            # ensure non purchased licenses are after purchased licenses
            return (1000000 + self.productSO.license.id, self.productSO.id)
        return (self.licenseUnlockIndex, self.productSO.indexInLicense)

    def selling_price(self):
        return self.sellPriceSetByPlayer if self.sellPriceSetByPlayer is not None else self.currentPrice

    def is_unlocked(self):
        return self.licenseUnlockIndex is not None
    
    def profit_rate_of_sell_price(self, sell_price: float):
        return (sell_price - self.currentPrice) * 100 / self.currentPrice
    
    def current_profit_rate(self):
        return self.profit_rate_of_sell_price(self.selling_price())
    
    def optimum_price(self):
        return self.currentPrice + self.currentPrice * self.productSO.optimumProfitRate / 100
    
    def optimum_price_100prcent_sell(self):
        return self.currentPrice + self.currentPrice * lerp(self.productSO.optimumProfitRate, self.productSO.maxProfitRate, 0.1) / 100
    
    def max_price(self):
        return self.currentPrice + self.currentPrice * self.productSO.maxProfitRate / 100

    def get_purchase_chance_of_sell_price(self, sell_price: float):
        profitRate = self.profit_rate_of_sell_price(sell_price)
        optiProfitRate = self.productSO.optimumProfitRate
        maxProfitRate = self.productSO.maxProfitRate
        if profitRate < 0:
            return 200.0
        if profitRate < optiProfitRate:
            t = inverse_lerp(0, optiProfitRate, profitRate)
            return self.productsData.gameData.priceCurves.purchaseChanceCurveForCheapPrice.evaluate(t)
        if profitRate < maxProfitRate:
            t = inverse_lerp(optiProfitRate, maxProfitRate, profitRate)
            return self.productsData.gameData.priceCurves.purchaseChanceCurveForExpensivePrice.evaluate(t)
        return 0.0

    
    def get_purchase_chance(self) -> float:
        return self.get_purchase_chance_of_sell_price(self.selling_price())
    
    def get_profit_per_chance_of_sell_price(self, sell_price: float) -> float:
        return (sell_price - self.currentPrice) * self.get_purchase_chance_of_sell_price(sell_price) / 100
    
    def get_profit_per_chance(self) -> float:
        return self.get_profit_per_chance_of_sell_price(self.selling_price())

    def get_sell_price_for_best_profit_per_chance(self) -> float:
        if not hasattr(self, "sellPriceForBestProfitPerChance"):
            self.sellPriceForBestProfitPerChance = local_max(lambda p: self.get_profit_per_chance_of_sell_price(p), self.optimum_price(), self.max_price(), 0.001)
        return self.sellPriceForBestProfitPerChance

    def get_best_rounded_price(self) -> float:
        pOpt = math.ceil(self.optimum_price() * 0.95) # 0.95 to authorize an integer price that is 5% below optimized price
        pBest = math.floor(self.get_sell_price_for_best_profit_per_chance())
        if pOpt <= pBest:
            return pBest
        pMin = min(pOpt, pBest)
        pMax = max(pOpt, pBest)
        if self.get_profit_per_chance_of_sell_price(pMin) > self.get_profit_per_chance_of_sell_price(pMax):
            return pMin
        return pMax
    



    

    def get_nb_displayed_items_per_slot(self):
        return [s.productCount for s in self.displaySlots]
    
    def get_nb_displayed_items(self):
        return sum(self.get_nb_displayed_items_per_slot() + [0])
    
    def get_max_displayed_items_total(self):
        return len(self.displaySlots) * self.productSO.productAmountOnDisplay
    
    def get_nb_items_in_stored_boxes(self):
        return [[b.productCount for b in s.rackedBoxDatas] for s in self.rackSlots]

    def get_nb_stored_boxes(self):
        return sum([len(s.rackedBoxDatas) for s in self.rackSlots] + [0])

    def get_nb_box_spots_in_storage(self):
        return (len(self.rackSlots) * self.productsData.gameData.boxes.byBoxSize[self.productSO.boxSize].boxCountInStorage) - self.get_nb_stored_boxes()
    
    def get_nb_stored_items(self):
        return sum([sum(l) for l in self.get_nb_items_in_stored_boxes()])

    def get_nb_unstored_boxes(self):
        return len(self.unstoredBoxes)
    
    def get_nb_items_in_unstored_boxes(self):
        return [b.productCount for b in self.unstoredBoxes]
    
    def get_nb_unstored_box_items(self):
        return sum(self.get_nb_items_in_unstored_boxes())
    
    def get_nb_items_in_all_boxes(self):
        tab = self.get_nb_items_in_unstored_boxes()
        for slot in self.get_nb_items_in_stored_boxes():
            tab += slot
        return tab
    
    def get_nb_items_in_all_nonfull_boxes(self):
        boxes = self.get_nb_items_in_all_boxes()
        max = self.productSO.productAmountOnPurchase
        return [b for b in boxes if b < max]
    
    def get_nb_items_total(self):
        return self.get_nb_displayed_items() + self.get_nb_stored_items() + self.get_nb_unstored_box_items()
    
    def get_max_displayable_and_storable_items(self):
        return self.get_max_displayed_items_total() + len(self.rackSlots) * self.productsData.gameData.boxes.byBoxSize[self.productSO.boxSize].boxCountInStorage * self.productSO.productAmountOnPurchase
    
    def get_nb_box_to_buy(self):
        return (self.get_max_displayable_and_storable_items() - self.get_nb_items_total()) // self.productSO.productAmountOnPurchase
    
    def get_max_storable_boxes(self):
        return len(self.rackSlots) * self.productsData.gameData.boxes.byBoxSize[self.productSO.boxSize].boxCountInStorage

    def get_estimated_duration_stock_emptying(self) -> float:
        """Will try to compute an estimation of how long it will take to empty the current stock of this product.
        The returned value has no specific unit, it is only used to sort the product to prioritize orders."""
        return self.get_nb_items_total() / (self.get_purchase_chance() / 100)


class ProductsData:
    def __init__(self, gameData: GameData, saveData: SaveData):
        self.gameData = gameData
        self.saveData = saveData
        self.byId: dict[int, Product] = {pId: Product(pSO, self) for pId, pSO in gameData.products.byId.items()}
        
        # getting live product data (license unlock, price, stock) from save file
        for i, plId in enumerate(saveData.progression.unlockedLicenses):
            for pSO in gameData.licenses.byId[plId].products:
                self.byId[pSO.id].licenseUnlockIndex = i

        for e in saveData.price.prices:
            self.byId[e.productId].currentPrice = e.price
        for e in saveData.price.pricesSetByPlayer:
            self.byId[e.productId].sellPriceSetByPlayer = e.price
        for e in saveData.price.averageCosts:
            self.byId[e.productId].averageCosts = e.price
        for e in saveData.price.dailyPriceChanges:
            self.byId[e.productId].dailyPriceChange = e.price
        for e in saveData.price.previousPrices:
            self.byId[e.productId].previousPrice = e.price

        for display in saveData.progression.displayDatas:
            for slot in display.displaySlots:
                if slot.productId is not None:
                    self.byId[slot.productId].displaySlots.append(slot)
        for rack in saveData.progression.rackDatas:
            for slot in rack.rackSlots:
                if slot.productId is not None:
                    self.byId[slot.productId].rackSlots.append(slot)
        for box in saveData.progression.boxDatas:
            if box.productId in self.byId:
                self.byId[box.productId].unstoredBoxes.append(box)
        
        self.unlocked: list[Product] = sorted(
            list(filter(lambda p: p.is_unlocked(), self.byId.values())),
            key=lambda p: p.get_by_license_sort_key()
            )
    