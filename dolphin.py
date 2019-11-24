import json
from functools import reduce

from api_logic import APILogic
from models import Asset

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

def improve_ptf(app, assets, stop_assets_up, stop_assets_down, base_ratio):
  if len(stop_assets_up) == len(assets) and len(stop_assets_down) == len(assets):
    print("Dolphin: final quantities:")
    print("[", end=" ")
    for item in assets:
      print(item.quantity, end=", ")
    print("]")

    print("Dolphin: Best final ratio: " + str(base_ratio))
    return
  total_nav = int(reduce(lambda a, b: a + b.nav * b.quantity, assets, 0))
  stop_assets_up = []
  stop_assets_down = []
  ratios_up = []
  ratios_down = []
  for item in assets:
    print("Dolphin: Trying up with " + str(item.id))
    if item.id not in stop_assets_up:
      new_percent_up = (item.quantity * 1.1 * item.nav)/(total_nav - (item.quantity * item.nav) + int(item.quantity * 1.1) * item.nav)
      if (new_percent_up > 0.1 or new_percent_up < 0.01):
        print("Dolphin: max found for asset " + str(item.id))
        ratios_up.append(0)
        stop_assets_up.append(item.id)
      else:
        print("Dolphin: updating quantity for asset " + str(item.id))
        save_quantity = item.quantity
        item.quantity = int(item.quantity * 1.1)
        app.update_ptf(assets)
        app.update_ptf(assets)
        new_ratio = app.get_user_ptf_sharpe()
        print("Dolphin: got ratio " + str(new_ratio))
        ratios_up.append(new_ratio)
        item.quantity = save_quantity
    else:
      ratios_up.append(0)

    print("Dolphin: Trying down with " + str(item.id))
    if item.id not in stop_assets_down:
      new_percent_down = (item.quantity * 0.9 * item.nav)/(total_nav - (item.quantity * item.nav) + int(item.quantity * 0.9) * item.nav)
      if (new_percent_down > 0.1 or new_percent_down < 0.01):
        print("Dolphin: max found for asset " + str(item.id))
        ratios_down.append(0)
        stop_assets_down.append(item.id)
      else:
        print("Dolphin: updating quantity for asset " + str(item.id))
        save_quantity = item.quantity
        item.quantity = int(item.quantity * 0.9)
        app.update_ptf(assets)
        app.update_ptf(assets)
        new_ratio = app.get_user_ptf_sharpe()
        print("Dolphin: got ratio " + str(new_ratio))
        ratios_down.append(new_ratio)
        item.quantity = save_quantity
    else:
      ratios_down.append(0)


  max_diff_up = ratios_up.index(max(ratios_up, key=lambda x: x))
  max_diff_down = ratios_down.index(max(ratios_down, key=lambda x: x))

  up = True if ratios_up[max_diff_up] > ratios_down[max_diff_down] else False

  max_value = ratios_up[max_diff_up] if up else ratios_down[max_diff_down]
  max_index = max_diff_up if up else max_diff_down

  if max_value <= base_ratio:
    print("Dolphin: ratio not better than base")
    print("Dolphin: final quantities:")
    print("[", end=" ")
    for item in assets:
      print(item.quantity, end=", ")
    print("]")

    print("Dolphin: Best final ratio: " + str(base_ratio))
    return

  if not up:
    assets[max_index].quantity = int(assets[max_index].quantity * 0.9)
    print("Dolphin: Going down with asset " + str(assets[max_index].id))
  else:
    assets[max_index].quantity = int(assets[max_index].quantity * 1.1)
    print("Dolphin: Going up with asset " + str(assets[max_index].id))


  print("Dolphin: new quantities:")
  print("[", end=" ")
  for item in assets:
    print(item.quantity, end=", ")
  print("]")

  new_ratio = ratios_up[max_index] if up else ratios_down[max_index]


  print("Dolphin: Best new ratio: " + str(new_ratio))

  improve_ptf(app, assets, stop_assets_up, stop_assets_down, new_ratio)


def main():
    app = APILogic()
    assets = app.get_assets()
    filtered = remove_negatives(assets)
    sorted_assets = sorted(
        filtered, key=lambda x: get_weight(x.ratios), reverse=True)
    best_assets = sorted_assets[:TOTAL_ASSETS]

    app.get_assets_nav(best_assets)

    total_nav = int(reduce(lambda a, b: a + b.nav, best_assets, 0))
    print("Dolphin:  total nav : " + str(total_nav))

    total_nav2 = 0
    for item in best_assets:
        item.quantity = int(((total_nav)/TOTAL_ASSETS/item.nav)*1000)
        print(item.id +  " - " + str(item.quantity) + " - " + str(item.nav))
        total_nav2 += item.nav*item.quantity

    return

    app.update_ptf(best_assets)
    app.update_ptf(best_assets)

    new_ratio = app.get_user_ptf_sharpe()
    print("Dolphin: new ratio :" + str(new_ratio))

    improve_ptf(app, best_assets, [], [], new_ratio)

    print("Dolphin: new ratio :" + str(new_ratio))


def check():
    app = APILogic()
    ptf = app.get_user_ptf()
    for item in ptf.assets:
        print(item.id + " - " + str(item.quantity))

    print("Dolphin: ratio :" + app.get_user_ptf_sharpe())

def save():
  app = APILogic()

  assets = [Asset(2112, quantity=8027, nav=14.35),
    Asset(1990, quantity=12771, nav=9.02),
    Asset(2064, quantity=2689, nav=42.84),
    Asset(1968, quantity=59076, nav=1.95),
    Asset(1897, quantity=21021, nav=5.48),
    Asset(1956, quantity=37524, nav=3.07),
    Asset(2120, quantity=81, nav=1418.0),
    Asset(1877, quantity=30901, nav=3.728),
    Asset(1585, quantity=4170, nav=27.62),
    Asset(1960, quantity=20682, nav=5.57),
    Asset(2013, quantity=5835, nav=19.74),
    Asset(1958, quantity=874, nav=131.75),
    Asset(2000, quantity=12972, nav=8.88),
    Asset(1912, quantity=13076, nav=8.81),
    Asset(1872, quantity=4129, nav=27.9),
  ]

  new_quantities = [ 4738, 12771, 4327, 95140, 21021, 22155, 81, 30901, 4170, 10989, 9394, 514, 10506, 13076, 2193 ] # 2.512252348115
  new_quantities = [ 2516, 9308, 4327, 95140, 15323, 11772, 89, 30901, 4170, 2511, 9394, 114, 6202, 13076, 497 ] # 2.556050614378
  new_quantities = [ 2516, 9308, 4327, 95140, 15323, 10594, 89, 30901, 4170, 2511, 9394, 114, 6202, 13076, 497 ] # 2.55606999004
  for i, quant in enumerate(new_quantities):
     assets[i].quantity = quant

  app.update_ptf(assets)
  app.update_ptf(assets)

  ratio = app.get_user_ptf_sharpe()
  print("Dolphin: intial ratio :" + str(ratio))


  improve_ptf(app, assets, [], [], ratio)


if __name__ == "__main__":
    save()
