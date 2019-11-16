import requests
import json
from urllib.parse import urlencode

class RESTManager :
  HOST_NAME = "dolphin.jump-technology.com"
  PORT = "8443"

  SCHEME = "https"
  URL = SCHEME + "://" + HOST_NAME + ":" + PORT + "/api/v1/"

  ID_PTF_USER = "564" #faux
  ID_PTF_BALANCED_USER = "565" #faux
  ID_PTF_RISKY_USER = "566" #faux
  ID_PTF_PRUDENT_USER = "567" #faux

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
    res = requests.get(url, params=payload, auth=self.USER_AUTH, verify=False)
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
    res = requests.get(url, params=payload, auth=self.USER_AUTH, verify=False)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

  def get_asset_quote(self, asset_id, startDate=None, endDate=None):
    url = self.URL + "asset/" + str(asset_id) + "/quote"
    payload = {'start_date': startDate, 'end_date': endDate }
    res = requests.get(url, params=payload, auth=self.USER_AUTH, verify=False)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

  def get_ratio(self):
    url = self.URL + "ratio"
    res = requests.get(url, auth=self.USER_AUTH, verify=False)
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
    res = requests.post(url, json=payload, auth=self.USER_AUTH, verify=False)
    if res.status_code != 200:
      print("QUERY FAILED : ERROR " + str(res.status_code))
    return res.json()

  def get_ptf(self):
    return

  def put_ptf(self):
    return

app = RESTManager()
#col = ["ASSET_DATABASE_ID", "LABEL", "TYPE", "LAST_CLOSE_VALUE_IN_CURR"]
assets = app.get_asset(columns=['ASSET_DATABASE_ID'])
ids = list(map(lambda x: int(x['ASSET_DATABASE_ID']['value']), assets))
ratios = app.post_ratio([app.ID_SHARPE], ids, app.PERIOD_START_DATE, app.PERIOD_END_DATE)
#ratios = sorted(ratios, key = lambda x: x[0]['value'])
#print(ratios[:app.MIN_ACTIF])
#app.get_asset(2)
#print(app.get_asset(asset_id=2097, date=app.PERIOD_END_DATE, columns=col))
#print(app.get_asset_quote(asset_id=2097, startDate=app.PERIOD_END_DATE, endDate=app.PERIOD_END_DATE))
#app.get_asset(date=app.PERIOD_START_DATE, columns=col)
#print(get_data(app))
#print(get_data("asset/1792", "2018-10-27"))
#print(app.get_ptf(11))
