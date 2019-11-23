import json
from api_service import RESTManager
from models import *


def check_ratio(ratio):
  return ratio is not None and ratio['type'] != 'error'

class APILogic:
    def __init__(self):
      self.api = RESTManager()

    def get_assets(self):
        assets = self.api.get_asset(
          columns=['ASSET_DATABASE_ID', 'IS_PORTFOLIO'])

        assets_list = []
        if (assets is not None):
          ids = list(map(lambda x: int(x['ASSET_DATABASE_ID']['value']), assets))
          ratios = self.api.post_ratio([self.api.ID_SHARPE, self.api.ID_VOL, self.api.ID_RETURN],
                            ids, self.api.PERIOD_START_DATE, self.api.PERIOD_END_DATE)
          if ratios is None:
            return
          for item in assets:
            if item['IS_PORTFOLIO']['value'] == 'false':
              asset_ratio_json = ratios[item['ASSET_DATABASE_ID']['value']]
              if asset_ratio_json is not None:
                asset_ratio = AssetRatio(
                  item['ASSET_DATABASE_ID']['value'],
                  float(asset_ratio_json[self.api.ID_SHARPE]['value'].replace(',', '.')) if check_ratio(asset_ratio_json[self.api.ID_SHARPE]) else None,
                  float(asset_ratio_json[self.api.ID_VOL]['value'].replace(',', '.')) if check_ratio(asset_ratio_json[self.api.ID_VOL]) else None,
                  float(asset_ratio_json[self.api.ID_RETURN]['value'].replace(',', '.')) if check_ratio(asset_ratio_json[self.api.ID_RETURN]) else None,
                )
                if asset_ratio.sharpe is not None and asset_ratio.vol is not None and asset_ratio.ret is not None:
                  assets_list.append(
                    Asset(item['ASSET_DATABASE_ID']['value'],
                      item['IS_PORTFOLIO']['value'],
                      ratios=asset_ratio))
        return assets_list

    def get_assets_nav(self, assets):
      for item in assets:
        asset_quote = self.api.get_asset_quote(item.id, startDate=self.api.PERIOD_START_DATE, endDate=self.api.PERIOD_START_DATE)
        if asset_quote is not None and len(asset_quote) > 0:
          item.nav = float(asset_quote[0]['nav']['value'].replace(',', '.'))


    def get_user_ptf_sharpe(self):
      json = self.api.post_ratio([12], [int(self.api.ID_PTF_USER), int(
        self.api.ID_PTF_USER)], self.api.PERIOD_START_DATE, self.api.PERIOD_END_DATE)
      if json is not None:
        return json[self.api.ID_PTF_USER][self.api.ID_SHARPE]['value']


    def update_ptf(self, assets):
      if not isinstance(assets, list):
        return
      ptf_assets = []
      for item in assets:
        if not isinstance(item, Asset):
          return
        ptf_assets.append({
          'asset': {
            'asset': item.id,
            'quantity': item.quantity
          }
        })
      return self.api.put_ptf(self.api.ID_PTF_USER, "EPITA_PTF_11", ptf_assets)
