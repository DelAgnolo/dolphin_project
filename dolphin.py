import json
from functools import reduce

from api_logic import APILogic

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
  sorted_assets = sorted(filtered, key=lambda x: get_weight(x.ratios), reverse=True)
  best_assets = sorted_assets[:15]

  app.get_assets_nav(best_assets)

  total_nav = reduce(lambda a, b: a + b.nav, best_assets, 0)

  total_quantity = 0
  for item in best_assets:
    item.quantity = int((total_nav/15)*get_weight(item.ratios))
    total_quantity += item.quantity

  app.update_ptf(best_assets)

  print("new ratio :" + app.get_user_ptf_sharpe())


if __name__ == "__main__":
    main()
