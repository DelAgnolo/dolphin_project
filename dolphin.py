import json
from functools import reduce

from api_logic import APILogic

TOTAL_ASSETS = 15


def get_weight(ratios):
    return (2*ratios.sharpe*ratios.ret)/ratios.vol


def remove_negatives(assets):
    new_assets = []
    for item in assets:
        if item.ratios.sharpe >= 0.5 and \
                item.ratios.vol >= 0 and \
                item.ratios.ret >= 2:
            new_assets.append(item)

    return new_assets


def main():
    app = APILogic()
    assets = app.get_assets()
    filtered = remove_negatives(assets)
    sorted_assets = sorted(
        filtered, key=lambda x: get_weight(x.ratios), reverse=True)
    best_assets = sorted_assets[:TOTAL_ASSETS]

    app.get_assets_nav(best_assets)

    total_nav = int(reduce(lambda a, b: a + b.nav, best_assets, 0))
    print("total nav : " + str(total_nav))

    total_nav2 = 0
    for item in best_assets:
        item.quantity = int(((total_nav)/TOTAL_ASSETS/item.nav)*1000)
        total_nav2 += item.nav*item.quantity

    app.update_ptf(best_assets)
    app.update_ptf(best_assets)

    print("new ratio :" + app.get_user_ptf_sharpe())


def check():
    app = APILogic()
    ptf = app.get_user_ptf()
    for item in ptf.assets:
        print(item.id + " - " + str(item.quantity))

    print("ratio :" + app.get_user_ptf_sharpe())


if __name__ == "__main__":
    main()
