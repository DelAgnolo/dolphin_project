import requests
import json
from urllib.parse import urlencode

class RESTManager :
  HOST_NAME = "dolphin.jump-technology.com"
  PORT = "8443"

  SCHEME = "https"
  URL = SCHEME + "://" + HOST_NAME + ":" + PORT + "/api/v1/"

  ID_PTF_USER = "1830"
  ID_PTF_REF = "2201"

  USER_AUTH = ("EPITA_GROUPE11", "23FAG45wFGraRMra")

  PERIOD_START_DATE = "2013-06-14"
  PERIOD_END_DATE = "2019-04-18"

  MIN_ACTIF = 15
  MAX_ACTIF = 40

  MIN_NAV_PER_LINE = 0.01
  MAX_NAV_PER_LINE = 0.1

  ID_BETA = "7"
  ID_CORRELATION = "11"
  ID_RETURN = "13"
  ID_ANNUAL_RETURN = "9"
  ID_SHARPE = "12"
  ID_VAR = "14"
  ID_VOL = "10"
  ID_EXPO = "15"

  def get_asset(self, asset_id=None, date=None, columns=list()):
    enc = ""
    if columns:
      enc = "?" + urlencode([("columns", x) for x in columns])
    if asset_id:
      enc = "/" + str(asset_id) + enc
    url = self.URL + "asset" + enc
    payload = {'date': date, 'fullResponse': False }
    res = requests.get(url, params=payload, auth=self.USER_AUTH, verify=True)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

 #voir asset_info_list pour les attributs
  def get_asset_attribute(self, asset_id, attr_name, date=None, columns=list()):
    enc = "asset/" + str(asset_id) + "/attribute/" + attr_name
    if columns:
      enc = enc + "?" + urlencode([("columns", x) for x in columns])
    url = self.URL + enc
    payload = {'date': date, 'fullResponse': False }
    res = requests.get(url, params=payload, auth=self.USER_AUTH, verify=True)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

  def get_asset_quote(self, asset_id, startDate=None, endDate=None):
    url = self.URL + "asset/" + str(asset_id) + "/quote"
    payload = {'start_date': startDate, 'end_date': endDate }
    res = requests.get(url, params=payload, auth=self.USER_AUTH, verify=True)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

  def get_ratio(self):
    url = self.URL + "ratio"
    res = requests.get(url, auth=self.USER_AUTH, verify=True)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

  def post_ratio(self, ratios, assets, start_date, end_date):
    url = self.URL + "ratio/invoke"
    payload = {
      'ratio': ratios,
      'asset': assets,
      'start_date': start_date,
      'end_date': end_date,
    }
    res = requests.post(url, json=payload, auth=self.USER_AUTH, verify=True)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

  def get_ptf(self, ptf_id):
    url = self.URL + "portfolio/" + str(ptf_id) + "/dyn_amount_compo"
    res = requests.get(url, auth=self.USER_AUTH, verify=True)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

  def put_ptf(self):
    return

  def get_change_rate(self, currency_src, currency_dst):
    url = self.URL + "currency/rate/" + currency_src + "/to/" + currency_dst
    res = requests.get(url, auth=self.USER_AUTH, verify=True)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()


def main():
  # Init Rest manager
  app = RESTManager()

  # Get assets
  assets = app.get_asset(columns=['ASSET_DATABASE_ID'])
  ids = list(map(lambda x: int(x['ASSET_DATABASE_ID']['value']), assets))

  # Get Sharpe ratio of assets
  ratios = app.post_ratio([app.ID_SHARPE], ids, app.PERIOD_START_DATE, app.PERIOD_END_DATE)
  filtered = {k: v for k, v in ratios.items() if v[app.ID_SHARPE]['type'] != 'error'}
  ratios.clear()
  ratios.update(filtered)

  # Sort assets according to their Sharpe ratio
  sorted_ratios_assets = sorted(ratios, key=lambda k: ratios[k][app.ID_SHARPE]['value'], reverse=True)
  sorted_ratios = list(map(lambda x: {x:ratios[x][app.ID_SHARPE]['value']} , sorted_ratios_assets[:app.MIN_ACTIF]))
  print(sorted_ratios)


if __name__ == "__main__":
    main()
