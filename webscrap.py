
from cache import cache_update, get_cache, get_cache_prices, get_coin, get_name_by_simbol, set_coin
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
import requests
from selenium import webdriver
from selenium.webdriver.support.select import Select

DATE_START = '28111984'

URL = 'https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes'
BaseURL = 'https://ptax.bcb.gov.br/'
u = "ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda=222&DATAINI=07/02/2020&DATAFIM=08/02/2020"

cache_update()


class Cotacao:
    def __init__(self, driver) -> None:
        self.driver = driver
        self.url = 'https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=consultarBoletim'
        self.coins = {}
        self.prices = {}
        self.prices.update(get_cache_prices())


    def navigate(self):
        print('Abrindo Browser...')
        self.driver.get(self.url)

    def set_date(self, date, _id='DATAINI'):
        self.DATE = self.driver.find_element_by_id(_id)
        self.DATE.clear()
        self.DATE.send_keys(date)

    def CheckBoxSelect(self, _op='1'):
        options = self.driver.find_elements_by_id('RadOpcao')
        for op in options:
            if op.get_attribute('value') == _op:
                op.click()


    def get_coins(self, index=0):
        select = self.driver.find_element_by_name('ChkMoeda')
        try:
            option = select.find_elements_by_tag_name('option')[index]
            _code = option.get_attribute('value')
            _cache_coin = get_coin(_code)
            if _cache_coin and len(_cache_coin.keys())>=3:
                self.coins[_code] = _cache_coin
            else:
                    
                option.click()
                self.submit()
                text = self.driver.find_elements_by_tag_name('div')[0].text
                
                if 'Cotações de Fechamento' in text:
                    parse_text = text.split('\n')[0].split(',')
                    _name = parse_text[0].split('Cotações de Fechamento do')[-1].strip()
                    _simbol = parse_text[2].split('Símbolo da Moeda:')[-1].strip()
                    

                    self.coins[_code] = {
                            'name':_name,
                            'simbolo':_simbol
                        }
                    
                    self.driver.back()
                    select = self.driver.find_element_by_name('ChkMoeda')
                else:
                    self.coins[_code] = {'simbolo': None, 'name': option.text}
                    set_coin(_code, {'simbolo': None, 'name': option.text})
            print(self.coins[_code])      
            return self.get_coins(index=index+1)
        except IndexError:
            pass 
    
        

    def set_coin(self, value):
        select = Select(self.driver.find_element_by_name('ChkMoeda'))
        select.select_by_value(value)

    def submit(self):
        btn = self.driver.find_element_by_xpath(
            "//input[contains(@title, 'Pesquisar')]")
        btn.click()

    def make_link(self, date_i, coin=''):
        return BaseURL + f"ptax_internet/consultaBoletim.do?method=gerarCSVFechamentoMoedaNoPeriodo&ChkMoeda={coin}&DATAINI={date_i}"

    def get_prices(self, date_i, date_f='----'):
        base_link = '/ptax_internet/consultaBoletim.do?method=gerarCSVTodasAsMoedas&'
        
        try:
            link = self.driver.find_element_by_xpath(
                f"//a[contains(@href, '{base_link}')]").get_attribute('href')
            _resp = requests.get(link).text.strip().replace(',', '.')

            for line in _resp.split('\n'):
                if line.split(';')[0] not in self.prices.keys():
                    self.prices[line.split(';')[0]] = {}

                self.prices[line.split(';')[0]][line.split(';')[3]] = {
                        'simbolo': line.split(';')[3], 
                        'paridadeCompra': float(line.split(';')[6]), 
                        'paridadeVenda': float(line.split(';')[7]), 
                        'name': get_name_by_simbol(line.split(';')[3]) }
            self.driver.back()  
        except NoSuchElementException:
            self.prices[date_i.replace('/','')]={'x':'x'}
        

    def get_simbols(self,date):
        for coin in self.coins.keys():
            response = {}
            response.update(self.coins[coin])
            if response['simbolo'] == None:

                _resp = requests.get(self.make_link(
                    date, coin)).text.strip().replace(',', '.').split(';')
                if _resp[0] == date.replace('/', ''):
                    response.update({'simbolo': _resp[3]})
                else:
                    print(_resp[0][:8])
                    response.update({'simbolo': 'null'})

                set_coin(coin, response)
                print(response)

    def make_dataset(self, date):
        if date.replace('/','') in self.prices.keys():
            return self.prices[date.replace('/','')]
        else:
            self.get_coins()
            self.get_simbols(date)
            self.CheckBoxSelect('2')
            self.set_date(date)
            self.submit()
            self.get_prices(date)
            try:
                del self.prices[date.replace('/','')]['XAU']
            except:
                pass
            
            cache_update(prices=self.prices)
            
            return self.prices[date.replace('/','')]

    def close(self):
        print('Fechando Browser...')
        return self.driver.quit()

options = Options()
options.headless = False
BCBApi = Cotacao(webdriver.Firefox(options=options))
BCBApi.navigate()

