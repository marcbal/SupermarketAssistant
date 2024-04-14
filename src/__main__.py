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
from datetime import datetime

from ansi.colour import fg, fx

from consoletable import ConsoleTable, ColumnDefinition, TextAlignment
from filewatcher import FileWatcher
from gamedata import ProductLicenseSO
from products import ProductsData, Product
from windows_console import enable_coloring_in_windows_console

enable_coloring_in_windows_console()



def as_price(value: float) -> str:
    return "-.--$" if value is None else f"{'%.2f' % (value)}$"


watcher = FileWatcher()


while True:
    watcher.wait_update()
    gameData = watcher.gameData
    saveData = watcher.saveData

    productsData = ProductsData(gameData, saveData)


    print("\033c", end="")

    # #############################################################################
    # ############################### General data ################################
    # #############################################################################

    print(f"{fg.brightgreen}General game data:{fx.reset}")

    ConsoleTable.print_objects([None], [
        ColumnDefinition("Save time", lambda _: datetime.fromtimestamp(int(saveData.modificationTime)), alignment=TextAlignment.RIGHT),
        ColumnDefinition("Game day", lambda _: saveData.progression.currentDay, alignment=TextAlignment.RIGHT),
        ColumnDefinition("Money"   , lambda _: as_price(saveData.progression.money), alignment=TextAlignment.RIGHT),
        ColumnDefinition("Level"   , lambda _: saveData.progression.currentStoreLevel, alignment=TextAlignment.RIGHT),
    ])
    print()

    # #############################################################################
    # ############################ Show awaiting bills ############################
    # #############################################################################


    bills = saveData.expenses.bills + saveData.expenses.rents + saveData.expenses.loanRepayments

    if len(bills) > 0:
        print(f"{fg.brightred}Bills to pay:{fx.reset}")

        ConsoleTable.print_objects(bills, [
            ColumnDefinition("Expense Day", lambda b: b.date, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Type"       , lambda b: gameData.playerPaymentTypeLocalization[b.paymentType.value]),
            ColumnDefinition("Amount"     , lambda b: as_price(b.amount), alignment=TextAlignment.RIGHT),
        ])
        print()
    billsSum = sum([b.amount for b in bills])
    playerMoneyAfterBills = saveData.progression.money - billsSum

    # #############################################################################
    # ############################# Show pricing data #############################
    # #############################################################################

    maxCheckoutsToDo = max([c.checkoutGoalToUnlock for c in gameData.cashiers.byId.values()])
    exactPrices = saveData.progression.completedCheckoutCount >= maxCheckoutsToDo

    productList: list[Product] = list(productsData.unlocked)
    if exactPrices:
        productList = list(filter(lambda p: abs(p.get_sell_price_for_best_profit_per_chance() - p.selling_price()) > 0.01, productList))
    else:
        productList = list(filter(lambda p: abs(p.get_best_rounded_price() - p.selling_price()) > 0.01, productList))

    if len(productList) > 0:
        
        print(f"{fg.brightred}Products to update prices:{fx.reset}")

        if exactPrices:
            print(f"{fg.green}Using exact prices because you have reached the maximum checkout goal to hire all cashiers.{fx.reset}")
        else:
            remainingCheckouts = maxCheckoutsToDo - saveData.progression.completedCheckoutCount
            print(f"{fg.green}Using rounded prices because you still need to do {remainingCheckouts} checkout{'s' if remainingCheckouts > 1 else ''} before you can hire all cashiers.{fx.reset}")
            
        ConsoleTable.print_objects(productList, [
            #ColumnDefinition("Id"           , lambda b: b.productSO.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Lic."         , lambda b: b.productSO.license.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Name"         , lambda b: b.localizedName),
            ColumnDefinition("Brand"        , lambda b: b.productSO.brand),
            ColumnDefinition("Curr. $"      , lambda b: as_price(b.selling_price()),
                                              lambda _: fg.red, alignment=TextAlignment.RIGHT),
            ColumnDefinition("New $"        , lambda b: as_price(b.get_sell_price_for_best_profit_per_chance() if exactPrices else b.get_best_rounded_price()),
                                              lambda _: fg.brightgreen, alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Base price"   , lambda b: as_price(b.productSO.basePrice), alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Price range"  , lambda b: f"{as_price(b.productSO.minDynamicPrice)} - {as_price(b.productSO.maxDynamicPrice)}", alignment=TextAlignment.RIGHT),
            ColumnDefinition("Opt/Max rate" , lambda b: f"{round(b.productSO.optimumProfitRate)}%-{str(round(b.productSO.maxProfitRate)).rjust(3)}%", alignment=TextAlignment.RIGHT),
            ColumnDefinition("Buy $"        , lambda b: as_price(b.currentPrice), alignment=TextAlignment.RIGHT),
            ColumnDefinition("Opt $"        , lambda b: as_price(b.optimum_price()), alignment=TextAlignment.RIGHT),
            ColumnDefinition("Opt+ $"       , lambda b: as_price(b.optimum_price_100prcent_sell()), alignment=TextAlignment.RIGHT),
            ColumnDefinition("Opt00$/chance", lambda b: as_price(b.get_best_rounded_price()) + f"-{str(round(b.get_purchase_chance_of_sell_price(b.get_best_rounded_price()))).rjust(3)}%",
                                              alignment=TextAlignment.RIGHT),
            ColumnDefinition("Opt++$/chance", lambda b: as_price(b.get_sell_price_for_best_profit_per_chance()) + f"-{str(round(b.get_purchase_chance_of_sell_price(b.get_sell_price_for_best_profit_per_chance()))).rjust(3)}%",
                                              alignment=TextAlignment.RIGHT),
            ColumnDefinition("Max $"        , lambda b: as_price(b.max_price()), alignment=TextAlignment.RIGHT),
            ColumnDefinition("Curr $/chance", lambda b: as_price(b.selling_price()) + f"-{str(round(b.get_purchase_chance(), 1)).rjust(5)}%", alignment=TextAlignment.RIGHT),
            ColumnDefinition("Profit/sell"  , lambda b: as_price(b.selling_price() - b.currentPrice), alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Profit*chance", lambda b: as_price(b.get_profit_per_chance()), alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Avg cost"     , lambda b: as_price(b.averageCosts), alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Sell price change", lambda b: "" if b.dailyPriceChange is None else f"{as_price(b.previousPrice)} -> {as_price(b.dailyPriceChange)}"),
        ])
        print()



    # #############################################################################
    # ############################# Displays to fill ##############################
    # #############################################################################

    productList: list[Product] = list(productsData.unlocked)
    productList = list(filter(lambda p: (len(p.displaySlots) == 0 or p.get_nb_displayed_items() < p.get_max_displayed_items_total()), productList)) # keep products with no display slot or when existing slots are not full
    productList = list(filter(lambda p: (p.get_nb_stored_items() + p.get_nb_unstored_box_items()) > 0, productList)) # keep product that have stock in existing boxes
    if len(saveData.employees.restockers) > 0: # if there is restockers
        productList = list(filter(lambda p: p.get_nb_stored_items() < p.get_max_displayed_items_total() - p.get_nb_displayed_items() and p.get_nb_unstored_box_items() > 0, productList)) # keep product that restockers can't fully restock themselves

    if len(productList) > 0:
        productList = sorted(productList, key=lambda p: p.get_by_license_sort_key())

        if len(saveData.employees.restockers) > 0: # if there is restockers
            print(f"{fg.brightred}Store shelves that restockers can't fully restock themselves:{fx.reset}")
        else:
            print(f"{fg.brightred}Store shelves to fill:{fx.reset}")

        ConsoleTable.print_objects(productList, [
            #ColumnDefinition("Id"      , lambda b: b.productSO.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Lic."    , lambda b: b.productSO.license.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Name"    , lambda b: b.localizedName),
            ColumnDefinition("Brand"   , lambda b: b.productSO.brand),
            ColumnDefinition("Max/slot", lambda b: b.productSO.productAmountOnDisplay),
            ColumnDefinition("Display #it #/slot", lambda b: f"{str(b.get_nb_displayed_items()).rjust(2)} [{','.join([str(v) for v in b.get_nb_displayed_items_per_slot()])}]"),
            ColumnDefinition("Storage #it #boxes #/boxes", lambda b: f"{str(b.get_nb_stored_items()).rjust(3)} {str(b.get_nb_stored_boxes()).rjust(2)} {','.join(['[' + ','.join([str(vv) for vv in v]) + ']' for v in b.get_nb_items_in_stored_boxes()])}"),
            ColumnDefinition("Unstored", lambda b: f"{str(b.get_nb_unstored_box_items()).rjust(3)} {str(b.get_nb_unstored_boxes()).rjust(2)} [{','.join([str(v) for v in b.get_nb_items_in_unstored_boxes()])}]"),
        ])
        print()



    # #############################################################################
    # ############################## Boxes to store ###############################
    # #############################################################################

    productList: list[Product] = list(productsData.unlocked)
    productList = list(filter(lambda p: p.get_nb_unstored_boxes() > 0 and p.get_nb_box_spots_in_storage() > 0
                            , productList))

    if len(productList) > 0:
        productList = sorted(productList, key=lambda p: p.get_by_license_sort_key())

        print(f"{fg.brightred}Boxes to put in storage shelves:{fx.reset}")

        ConsoleTable.print_objects(productList, [
            #ColumnDefinition("Id"      , lambda b: b.productSO.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Lic."    , lambda b: b.productSO.license.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Name"    , lambda b: b.localizedName),
            ColumnDefinition("Brand"   , lambda b: b.productSO.brand),
            ColumnDefinition("Storage #it #boxes #/boxes", lambda b: f"{str(b.get_nb_stored_items()).rjust(3)} {str(b.get_nb_stored_boxes()).rjust(2)} {','.join(['[' + ','.join([str(vv) for vv in v]) + ']' for v in b.get_nb_items_in_stored_boxes()])}"),
            ColumnDefinition("Unstored", lambda b: f"{str(b.get_nb_unstored_box_items()).rjust(3)} {str(b.get_nb_unstored_boxes()).rjust(2)} [{','.join([str(v) for v in b.get_nb_items_in_unstored_boxes()])}]"),
        ])
        print()



    # #############################################################################
    # ############################## Boxes to merge ###############################
    # #############################################################################

    productList: list[Product] = list(productsData.unlocked)
    productList = list(filter(lambda p: math.ceil(sum(p.get_nb_items_in_all_nonfull_boxes()) / p.productSO.productAmountOnPurchase) < len(p.get_nb_items_in_all_nonfull_boxes()), productList))

    if len(productList) > 0:
        productList = sorted(productList, key=lambda p: p.get_by_license_sort_key())

        print(f"{fg.brightred}Boxes to merge contents:{fx.reset}")

        ConsoleTable.print_objects(productList, [
            #ColumnDefinition("Id"      , lambda b: b.productSO.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Lic."    , lambda b: b.productSO.license.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Name"    , lambda b: b.localizedName),
            ColumnDefinition("Brand"   , lambda b: b.productSO.brand),
            ColumnDefinition("Storage #it #boxes #/boxes", lambda b: f"{str(b.get_nb_stored_items()).rjust(3)} {str(b.get_nb_stored_boxes()).rjust(2)} {','.join(['[' + ','.join([str(vv) for vv in v]) + ']' for v in b.get_nb_items_in_stored_boxes()])}"),
            ColumnDefinition("Unstored", lambda b: f"{str(b.get_nb_unstored_box_items()).rjust(3)} {str(b.get_nb_unstored_boxes()).rjust(2)} [{','.join([str(v) for v in b.get_nb_items_in_unstored_boxes()])}]"),
        ])
        print()




    # #############################################################################
    # ############################# Show boxes to buy #############################
    # #############################################################################




    productList: list[Product] = list(productsData.unlocked)
    productList = list(filter(lambda p: p.get_nb_box_to_buy() > 0, productList))

    if (len(productList) > 0):

        productBuyColumns: list[ColumnDefinition[Product]] = [
            #ColumnDefinition("Id"      , lambda b: b.productSO.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Lic."    , lambda b: b.productSO.license.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Name"    , lambda b: b.localizedName),
            ColumnDefinition("Brand"   , lambda b: b.productSO.brand),
            ColumnDefinition("To buy"  , lambda b: b.get_nb_box_to_buy(),
                                        lambda _: fg.boldgreen, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Total"   , lambda b: as_price(b.get_nb_box_to_buy() * b.currentPrice * b.productSO.productAmountOnPurchase),
                                        lambda _: fg.boldcyan, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Unit $"  , lambda b: as_price(b.currentPrice), alignment=TextAlignment.RIGHT),
            ColumnDefinition("#/box"   , lambda b: b.productSO.productAmountOnPurchase, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Box $"   , lambda b: as_price(b.currentPrice * b.productSO.productAmountOnPurchase), alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Prio"    , lambda b: round(b.get_estimated_duration_stock_emptying(), 1), alignment=TextAlignment.RIGHT),
            #ColumnDefinition("Storage #it #boxes #/boxes", lambda b: f"{str(b.get_nb_stored_items()).rjust(3)} {str(b.get_nb_stored_boxes()).rjust(2)} {','.join(['[' + ','.join([str(vv) for vv in v]) + ']' for v in b.get_nb_items_in_stored_boxes()])}"),
            #ColumnDefinition("Unstored", lambda b: f"{str(b.get_nb_unstored_box_items()).rjust(3)} {str(b.get_nb_unstored_boxes()).rjust(2)} [{','.join([str(v) for v in b.get_nb_items_in_unstored_boxes()])}]"),
        ]

        productListUrgentBase = list(filter(lambda p: p.get_nb_box_to_buy() >= p.get_max_storable_boxes() / 2, productList))
        productListUrgentBase.sort(key=lambda p: p.get_estimated_duration_stock_emptying())
        productListUrgent: list[Product] = []
        productListUrgentIds: set[int] = set()
        productListBuySum = 0

        for p in productListUrgentBase:
            productTotal = p.get_nb_box_to_buy() * p.currentPrice * p.productSO.productAmountOnPurchase + 1 # +1 for shipping cost, even if it's more complicated than that
            if productListBuySum + productTotal > playerMoneyAfterBills:
                break
            productListUrgent.append(p)
            productListUrgentIds.add(p.productSO.id)
            productListBuySum += productTotal

        if len(productListUrgent) > 0:
            print(f"{fg.brightred}Boxes to buy urgently:{fx.reset}")

            productListUrgent.sort(key=lambda p: p.get_by_license_sort_key())
            ConsoleTable.print_objects(productListUrgent, productBuyColumns)
            print(f"{fg.brightblue}Total amount with estimated shipping: {fg.boldcyan}{as_price(productListBuySum)}{fx.reset}")
            print()


        productListNonUrgent = list(filter(lambda p: not p.productSO.id in productListUrgentIds, productList))
        if len(productListNonUrgent) > 0:
            print(f"{fg.red}Boxes to buy eventually:{fx.reset}")

            productListNonUrgent.sort(key=lambda p: p.get_by_license_sort_key())
            total = sum([b.get_nb_box_to_buy() * b.currentPrice * b.productSO.productAmountOnPurchase for b in productListNonUrgent])
            ConsoleTable.print_objects(productListNonUrgent, productBuyColumns)
            print(f"{fg.brightblue}Total amount without shipping: {fg.boldcyan}{as_price(total)}{fx.reset}")
            print()




    # #############################################################################
    # ############################ Show next licenses #############################
    # #############################################################################



    unlockableLicenses: list[ProductLicenseSO] = list(filter(lambda l: l.id not in saveData.progression.unlockedLicenses and saveData.progression.currentStoreLevel >= l.requiredPlayerLevel, gameData.licenses.byId.values()))

    if (len(unlockableLicenses) > 0):
        print(f"{fg.brightgreen}Next unlockable licenses:{fx.reset}")

        licenseColumns: list[ColumnDefinition[ProductLicenseSO]] = [
            ColumnDefinition("License: Id"        , lambda l: l.id, lambda _: fg.darkgray, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Cost"              , lambda l: as_price(l.purchasingCost), alignment=TextAlignment.RIGHT)
        ]

        productColumns: list[ColumnDefinition[Product]] = [
            ColumnDefinition("Products: Name"     , lambda b: b.localizedName),
            ColumnDefinition("Brand"              , lambda b: b.productSO.brand),
            ColumnDefinition("Price (min-max)"    , lambda b: f"{as_price(b.productSO.minDynamicPrice).rjust(7)}-{as_price(b.productSO.maxDynamicPrice).rjust(7)}", alignment=TextAlignment.RIGHT),
            ColumnDefinition("#/box"              , lambda b: b.productSO.productAmountOnPurchase, alignment=TextAlignment.RIGHT),
            ColumnDefinition("Box price (min-max)", lambda b: f"{as_price(b.productSO.minDynamicPrice * b.productSO.productAmountOnPurchase).rjust(7)}-{as_price(b.productSO.maxDynamicPrice * b.productSO.productAmountOnPurchase).rjust(7)}", alignment=TextAlignment.RIGHT),
            ColumnDefinition("Box size (#/stor.)" , lambda b: f"{b.productSO.boxSize.name.lower()} ({gameData.boxes.byBoxSize[b.productSO.boxSize].boxCountInStorage})"),
            ColumnDefinition("Display"            , lambda b: gameData.displayTypeLocalization[b.productSO.productDisplayType.value]),
            ColumnDefinition("#/display"          , lambda b: b.productSO.productAmountOnDisplay),
        ]

        for l in unlockableLicenses:
            ConsoleTable.print_objects([l], licenseColumns)
            ConsoleTable.print_objects([productsData.byId[pSO.id] for pSO in l.products], productColumns)
            print()



