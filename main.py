from datetime import datetime, timedelta

from selenium import webdriver
from webscrap import BCBApi, Cotacao
import requests
from Cli import Cli
from cache import cache_update, set_cache,get_cache

try:
    BaseURL = 'https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/'

    cache_update()


    def get_price_dolar(date):
        dolar_URL = f"{BaseURL}CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{date}'&$top=100&$format=json"
        return requests.get(dolar_URL).json()['value']

    def parse_date(date:str, p='dmy')->str:
        y = date[:4]
        d = date[6:8]
        m = date[4:6]

        return p.replace('d',d).replace('m',m).replace('y',y)

    def get_coins():
        coins = f'{BaseURL}Moedas?$top=100&$format=json&$select=simbolo,nomeFormatado,tipoMoeda'
        return requests.get(coins).json()['value']

    def get_price(coin, date):
        try:
            return BCBApi.prices[date][coin]
        except KeyError as err:
            print(err,f'Erro Get_price({coin}{date})')
            return {'paridadeCompra':101}



    def get_prices(date):
        lower = {"simbolo":'x'}
        Min = 1000000
        coins = BCBApi.make_dataset(date)
        for coin in coins.keys():
            _price:dict = coins[coin]
            if _price['paridadeCompra']<Min:
                lower.update(coins[coin])
                Min =_price['paridadeCompra']
        
        return lower


    def parse_prices(date):
        #- o símbolo da moeda com menor cotação,
        #- o nome do país de origem da moeda e
        #- o valor da cotação desta moeda frente ao dólar na data especificada
        _price = get_prices(parse_date(date))
        try:
            flag=''
            dolar = get_price_dolar(parse_date(date,'m-d-y'))[0]['cotacaoVenda']
        except:
            flag='Paridade'
            dolar = 1
        if len(_price.keys())<2:
            return _price['simbolo']
        else:
            return f"{_price['simbolo']}, {_price['name']}, {_price['paridadeCompra']*dolar:0.2f} {flag}"




    class priceCli(Cli):
        def __init__(self) -> None:
            Cli.__init__(self)
            self.cmd_cache_time = 1
        def cmd_loop(self, arg, list_args, **kwargs):
            work =True
            while work:
                input_date = input(':> ')
                if '-q' in input_date:
                    print('saindo...')
                    work = False
                for date in input_date.split():
                    if len(date)>=8:
                        print(parse_prices(date))
            
            print('Saindo do loop')
        
        def __default__(self, arg, list_args, **kargs):
            dates = [list_args[a] for a in list_args.keys() if type(a)==int]
            for a in dates:
                if len(a)>=8:
                    print(parse_prices(a))


    priceCli().listen_os()
finally:
    BCBApi.close()
