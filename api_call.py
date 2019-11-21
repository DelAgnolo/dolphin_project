import requests
import json
from urllib.parse import urlencode
from functools import reduce


class RESTManager:
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
        payload = {'date': date, 'fullResponse': False}
        res = requests.get(url, params=payload,
                           auth=self.USER_AUTH, verify=True)
        if res.status_code != 200:
            print("QUERY FAILED : ERROR " + str(res.status_code))
        return res.json()

     # voir asset_info_list pour les attributs
    def get_asset_attribute(self, asset_id, attr_name, date=None, columns=list()):
        enc = "asset/" + str(asset_id) + "/attribute/" + attr_name
        if columns:
            enc = enc + "?" + urlencode([("columns", x) for x in columns])
        url = self.URL + enc
        payload = {'date': date, 'fullResponse': False}
        res = requests.get(url, params=payload,
                           auth=self.USER_AUTH, verify=True)
        if res.status_code != 200:
            print("QUERY FAILED : ERROR " + str(res.status_code))
        return res.json()

    def get_asset_quote(self, asset_id, startDate=None, endDate=None):
        url = self.URL + "asset/" + str(asset_id) + "/quote"
        payload = {'start_date': startDate, 'end_date': endDate}
        res = requests.get(url, params=payload,
                           auth=self.USER_AUTH, verify=True)
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
        res = requests.post(url, json=payload,
                            auth=self.USER_AUTH, verify=True)
        if res.status_code != 200:
            print("QUERY FAILED : ERROR " + str(res.status_code))
        return res.json()

    def get_ptf(self, ptf_id):
        url = self.URL + "portfolio/" + str(ptf_id) + "/dyn_amount_compo"
        res = requests.get(url, auth=self.USER_AUTH, verify=True)
        if res.status_code != 200:
            print("QUERY FAILED : ERROR " + str(res.status_code))
        return res.json()

    def put_ptf(self, ptf_id, label, assets):
        url = self.URL + "portfolio/" + str(ptf_id) + "/dyn_amount_compo"
        payload = {
            'label': label,
            'currency': {
                'code': 'EUR'
            },
            'type': 'front',
            'values': {self.PERIOD_START_DATE: assets}
        }
        print(payload)
        res = requests.put(url, json=payload, auth=self.USER_AUTH, verify=True)
        if res.status_code != 200:
            print("QUERY FAILED : ERROR " + str(res.status_code))
            return False
        return True

    def get_change_rate(self, currency_src, currency_dst):
        url = self.URL + "currency/rate/" + currency_src + "/to/" + currency_dst
        res = requests.get(url, auth=self.USER_AUTH, verify=True)
        if res.status_code != 200:
            print("QUERY FAILED : ERROR " + str(res.status_code))
        return res.json()


def find_asset_by_id(json, id):
    for asset in json:
        if asset['ASSET_DATABASE_ID']['value'] == id:
            return asset

def get_weight(app, ratios, x):
  return (2*float(ratios[x][app.ID_SHARPE]['value'].replace(',', '.'))
    * float(ratios[x][app.ID_RETURN]['value'].replace(',', '.'))
    / float(ratios[x][app.ID_VOL]['value'].replace(',', '.')))

def main():
    # Init Rest manager
    app = RESTManager()

    # Get assets
    assets = app.get_asset(
        columns=['ASSET_DATABASE_ID', 'LAST_CLOSE_VALUE', 'CURRENCY', 'IS_PORTFOLIO'])
    assets = list(
        filter(lambda x: x['IS_PORTFOLIO']['value'] == 'false', assets))
    ids = list(map(lambda x: int(x['ASSET_DATABASE_ID']['value']), assets))

    # Get Sharpe/Vol/Return ratio of assets
    ratios = app.post_ratio([app.ID_SHARPE, app.ID_VOL, app.ID_RETURN],
                            ids, app.PERIOD_START_DATE, app.PERIOD_END_DATE)

    # Remove assets with missing ratios
    filtered = {k: v for k, v in ratios.items(
    ) if v[app.ID_SHARPE]['type'] != 'error'
    and v[app.ID_RETURN]['type'] != 'error'
    and v[app.ID_VOL]['type'] != 'error'
    and float(v[app.ID_SHARPE]['value'].replace(',', '.')) > 0.8
    and float(v[app.ID_RETURN]['value'].replace(',', '.')) > 2
    and float(v[app.ID_VOL]['value'].replace(',', '.')) > 0}
    ratios.clear()
    ratios.update(filtered)

    # Sort assets according to their Sharpe ratio
    total_assets = 15

    sorted_ratios = sorted(ratios, key=lambda x: get_weight(app, ratios, x), reverse=True)
    assets_ratios = list(map(lambda x: {
      'weight': get_weight(app, ratios, x),
      'sharpe': ratios[x][app.ID_SHARPE]['value'],
      'vol': ratios[x][app.ID_VOL]['value'],
      'return': ratios[x][app.ID_RETURN]['value'],
      'asset': find_asset_by_id(assets, x)}, sorted_ratios[:total_assets]))

    total_sum = reduce(lambda a, b: a + float(b['asset']['LAST_CLOSE_VALUE']
                                              ['value'].split(' ')[0].replace(',', '.')), assets_ratios, 0)

    ptf_assets = []
    for asset in assets_ratios:
        ret = float(asset['return'].replace(',', '.'))
        vol = float(asset['vol'].replace(',', '.'))
        sharpe = float(asset['sharpe'].replace(',', '.'))
        weight = asset['weight']
        val = float(asset['asset']['LAST_CLOSE_VALUE']
                    ['value'].split(' ')[0].replace(',', '.'))

        print(asset['asset']['ASSET_DATABASE_ID']['value'] + " - " + str(weight) + " - " + str(sharpe) + " - " + str(vol) + " - " + str(ret))
        ptf_assets.append({
            'asset': {
                'asset': asset['asset']['ASSET_DATABASE_ID']['value'],
                'quantity': str(asset['weight']*(total_sum/total_assets/val))
            },
        })
    print("nb assets : " + str(len(ptf_assets)))
   # print([(x['asset']['quantity']) for x in ptf_assets])

    res = app.put_ptf(app.ID_PTF_USER, "EPITA_PTF_11", ptf_assets)
    check()


def check():
    app = RESTManager()

    ratios = app.post_ratio([12], [int(app.ID_PTF_REF), int(
        app.ID_PTF_USER)], app.PERIOD_START_DATE, app.PERIOD_END_DATE)
    print('group: ' + ratios[app.ID_PTF_USER][app.ID_SHARPE]['value'])
    print('ref: ' + ratios[app.ID_PTF_REF][app.ID_SHARPE]['value'])

if __name__ == "__main__":
    main()
