class Asset:
    def __init__(self, id, is_portfolio, type=None, nav=None, ratios=None, quantity=None):
        self.id = id
        self.is_portfolio = is_portfolio
        self.type = type
        self.nav = nav
        self.quantity = quantity
        self.ratios = ratios


class AssetRatio:
    def __init__(self, asset_id, sharpe=None, vol=None, ret=None):
        self.asset_id = asset_id
        self.sharpe = sharpe
        self.vol = vol
        self.ret = ret


class Portfolio:
    def __init__(self, id, label, sharpe=None, assets=None):
        self.id = id
        self.sharpe = sharpe
        if assets is None:
            self.assets = []
        else:
            self.assets = assets
