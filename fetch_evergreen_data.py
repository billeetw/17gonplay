import requests
import datetime

STOCK_ID = '2603'  # Evergreen Marine
ETF_IDS = ['0050', '006208']

TWSE_MARGIN_URL = 'https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN'
TWSE_SBL_URL = 'https://openapi.twse.com.tw/v1/SBL/TWT96U'
TWSE_T86_URL = 'https://www.twse.com.tw/rwd/zh/fund/T86'


def get_margin_data(stock_id=STOCK_ID):
    resp = requests.get(TWSE_MARGIN_URL, timeout=10)
    resp.raise_for_status()
    for item in resp.json():
        if item.get('股票代號') == stock_id:
            fin = int(item['融資今日餘額'].replace(',', ''))
            short = int(item['融券今日餘額'].replace(',', ''))
            ratio = short / fin * 100 if fin else None
            return {'margin_balance': fin, 'short_balance': short, 'short_margin_ratio': ratio}
    return None


def get_sbl_available(stock_id=STOCK_ID):
    resp = requests.get(TWSE_SBL_URL, timeout=10)
    resp.raise_for_status()
    for item in resp.json():
        if item.get('TWSECode') == stock_id:
            avail = int(item['TWSEAvailableVolume'].replace(',', ''))
            return {'sbl_available': avail}
    return None


def fetch_t86(date, stock_id):
    params = {'date': date, 'selectType': 'ALL', 'response': 'json'}
    resp = requests.get(TWSE_T86_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    fields = data.get('fields', [])
    for row in data.get('data', []):
        if row[0] == stock_id:
            return dict(zip(fields, row))
    return None


def get_investor_trading(date, stock_id=STOCK_ID):
    row = fetch_t86(date, stock_id)
    if not row:
        return None
    buy = int(row['外陸資買進股數(不含外資自營商)'].replace(',', ''))
    sell = int(row['外陸資賣出股數(不含外資自營商)'].replace(',', ''))
    foreign_net = int(row['外陸資買賣超股數(不含外資自營商)'].replace(',', ''))
    return {'foreign_net': foreign_net, 'foreign_buy': buy, 'foreign_sell': sell}


def get_etf_trading(date, etf_ids=ETF_IDS):
    params = {'date': date, 'selectType': 'ETF', 'response': 'json'}
    resp = requests.get(TWSE_T86_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    fields = data.get('fields', [])
    results = {}
    for row in data.get('data', []):
        code = row[0]
        if code in etf_ids:
            info = dict(zip(fields, row))
            net = int(info['三大法人買賣超股數'].replace(',', ''))
            results[code] = net
    return results


def get_ccfi_scfi():
    # Attempt to fetch CCFI and SCFI data from SSE, may fail due to restrictions
    urls = [
        'https://en.sse.net.cn/enjson/scfi.json',
        'https://en.sse.net.cn/enjson/ccfi.json',
    ]
    values = {}
    for u in urls:
        try:
            resp = requests.get(u, timeout=10)
            if resp.ok:
                values[u.split('/')[-1].split('.')[0].lower()] = resp.json()
        except Exception:
            pass
    return values


def main():
    date = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
    margin = get_margin_data()
    sbl = get_sbl_available()
    investor = get_investor_trading(date)
    etf = get_etf_trading(date)
    indexes = get_ccfi_scfi()

    print('Date:', date)
    print('Margin:', margin)
    print('SBL Available:', sbl)
    print('Foreign Trading:', investor)
    print('ETF Trading:', etf)
    print('Indexes:', indexes or 'Unavailable')


if __name__ == '__main__':
    main()
