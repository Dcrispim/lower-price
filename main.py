from decorators import feedback
from crawler import BCBApi
from cache import cache_update, clear_table, get_cache_prices


cache_update()

@feedback()
def parse_date(date: str, p='dmy') -> str:
    y = date[:4]
    d = date[6:8]
    m = date[4:6]

    return p.replace('d', d).replace('m', m).replace('y', y)


@feedback()
def get_lower_price(date, _cache:dict=None):
    def is_true_price_dolar(coin, dolar):
        diff = coin['paridadeCompra_BRL']/dolar['paridadeCompra_BRL'] 
        pDolar = 1/coin['paridadeCompra_USD']

        if abs(diff-pDolar)<0.0001:
            return pDolar

        else: 
            return coin['paridadeCompra_USD']

    lower = {"simbolo": 'x'}
    
    _date = parse_date(date, 'dmy')
    _cache_prices = _cache if _cache else get_cache_prices()

    if  _cache_prices and _date in _cache_prices.keys() and 'ERROR' not in _cache_prices[_date].keys() :
        coins = _cache_prices[_date] 

    else:
        BCBApi.navigate()
        coins = BCBApi.make_dataset(parse_date(date, 'd/m/y'))

    try:
        Min = max([ coins[coin]['paridadeCompra_USD'] for coin in coins.keys()])

    except TypeError:
        Min=100

    for coin in coins.keys():
        _price:dict = coins[coin]
        _price_dolar = is_true_price_dolar(_price, coins['USD'])

        if _price_dolar < Min and coin!='ERROR' and  coin!='USD':
            lower.update(coins[coin])
            lower['paridadeCompra_USD'] = _price_dolar
            Min = _price_dolar


    return lower



def parse_prices(date, _cache=None):
    lower_price = get_lower_price(date,_cache=_cache)

    if len(lower_price.keys()) < 2:
        return lower_price['simbolo']

    else:
        return f"{lower_price['simbolo']}, {lower_price['name']}, {lower_price['paridadeCompra_USD']:0.8f}"


def get_simbols():
    clear_table('coins')
    BCBApi.navigate()
    BCBApi.get_coins()
    BCBApi.get_simbols('10/03/2020')
