import os
import requests
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from cache import cache_update, get_cache_prices, get_coin, get_name_by_simbol, set_coin
import chromedriver_binary
from decorators import feedback


BaseURL = 'https://ptax.bcb.gov.br/'


@feedback()
def add_day(date:str, days):
    date = date.replace('/','').replace('-','')
    d1 = datetime(int(date[4:8]),int(date[2:4]), int(date[:2])).timestamp()
    d2 = d1+(days*86400)
    dt = datetime.fromtimestamp(d2)
    d = dt.day
    m = dt.month
    y = dt.year

    return f'{d:0>2}/{m:0>2}/{y:0>4}'


class Browser:

    def __init__(self, driver, options=None) -> None:
        self.driver=driver(chrome_options=options)
        self.options = options
        self.url = f'{BaseURL}ptax_internet/consultaBoletim.do?method=consultarBoletim'
        self.coins = {}
        self.prices = {}
        self.prices.update(get_cache_prices())
        self._open_ = False


    def navigate(self):
        self.driver.get(self.url)


    @feedback()
    def set_date(self, date, _id='DATAINI'):
        self.DATE = self.driver.find_element_by_id(_id)
        self.DATE.clear()
        self.DATE.send_keys(date)


    @feedback()
    def CheckBoxSelect(self, _op='1'):
        options = self.driver.find_elements_by_id('RadOpcao')

        for op in options:

            if op.get_attribute('value') == _op:
                op.click()


    @feedback()
    def get_coins(self):
        select = self.driver.find_element_by_name('ChkMoeda')
        options = select.find_elements_by_tag_name('option')

        for option in options:

            _code = option.get_attribute('value')
            _cache_coin = get_coin(_code)

            if _cache_coin:
                self.coins[_code] = _cache_coin

            else:
                self.coins[_code] = {'simbolo': None, 'name': option.text}
                set_coin(_code, {'simbolo': None, 'name': option.text})


    @feedback()
    def submit(self):
        btn = self.driver.find_element_by_xpath(
            "//input[contains(@title, 'Pesquisar')]")
        btn.click()

    def make_link(self, date_i, coin=''):
        return BaseURL + f"ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda={coin}&DATAINI={date_i}&DATAFIM={add_day(date_i,1)}"

    @feedback()
    def get_prices(self, date_i, date_f='----'):
        base_link = '/ptax_internet/consultaBoletim.do'
        
        try:
            link = self.driver.find_element_by_xpath(
                f"//a[contains(@href, '{base_link}')]").get_attribute('href')
            _resp = requests.get(link).text.strip().replace(',', '.')

            for line in _resp.split('\n'):

                if line.split(';')[0] not in self.prices.keys():
                    self.prices[line.split(';')[0]] = {}

                _price = {
                    'simbolo': line.split(';')[3], 
                    'paridadeCompra_USD': float(line.split(';')[6]), 
                    'paridadeVenda_USD': float(line.split(';')[7]), 
                    'paridadeCompra_BRL': float(line.split(';')[4]), 
                    'paridadeVenda_BRL': float(line.split(';')[5]), 
                    'name': get_name_by_simbol(line.split(';')[3]), 
                    }
                                 
                self.prices[line.split(';')[0]][line.split(';')[3]] = _price

            self.driver.back()  

        except NoSuchElementException:

            self.prices[date_i.replace('/','')]={
                'ERROR':{
                    'simbolo': 'NULL', 
                    'paridadeCompra_USD': 1, 
                    'paridadeVenda_USD': 1, 
                    'paridadeCompra_BRL':1, 
                    'paridadeVenda_BRL': 1, 
                    'name': 'NOT DEFINED', 
                },
                'USD':{
                    'simbolo': 'NULL', 
                    'paridadeCompra_USD': 1, 
                    'paridadeVenda_USD': 1, 
                    'paridadeCompra_BRL':1, 
                    'paridadeVenda_BRL': 1, 
                    'name': 'NOT DEFINED', 
                }
            }
        

    @feedback()
    def get_simbols(self,date):
        i=0
        _clear = False

        for coin in self.coins.keys():
            response = {}
            response.update(self.coins[coin])

            if response['simbolo'] == None:
                print(f'Reload cache of currency symbols: {100*(i/len(self.coins.keys())):2.2f}%')
                
                _clear =True
                _resp = requests.get(self.make_link(
                    date, coin)).text.strip().replace(',', '.').split(';')
                
                if _resp[0] == date.replace('/', ''):
                    response.update({'simbolo': _resp[3]})
                
                else:
                    response.update({'simbolo': 'null'})

                set_coin(coin, response)
            
            i+=1
        
        if _clear:
            os.system('clear')
                
    @feedback()
    def make_dataset(self, date):
        _date = date.replace('/','').replace('-','')

        if date in self.prices.keys() and 'ERROR' not in self.prices[date].keys():
            return self.prices[date]

        else:
            self.get_coins()
            self.get_simbols(date)
            self.CheckBoxSelect('2')
            self.set_date(_date)
            self.submit()
            self.get_prices(_date)

            try:
                del self.prices[date.replace('/','')]['XAU']

            except:
                pass
            
            cache_update(prices=self.prices)
            
            return self.prices[date.replace('/','')]

    def close(self):
        try:

            self.driver.close()
            self.driver.quit()
            
        except:
            pass
            


chrome_options=webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("window-size=1400,2100") 
chrome_options.add_argument('--disable-gpu')

BCBApi = Browser(webdriver.Chrome, options=chrome_options)
