from crawler import BCBApi
from main import get_lower_price, parse_date, parse_prices
import unittest
from unittest import TestCase

class test_crawler(TestCase):
    
    def setUp(self):
        self.date = '20200310'
        self.BaseUrl = "https://ptax.bcb.gov.br/"
        self.cache = {}
        
        
    def test_make_link(self):
        date=parse_date(self.date,'d/m/y')
        link = BCBApi.make_link(date, '222')
        response =''.join([
                self.BaseUrl,
                "ptax_internet/",
                "consultaBoletim.do?",
                "method=gerarCSVFechamentoMoedaNoPeriodo",
                "&ChkMoeda=222",
                "&DATAINI=10/03/2020",
                "&DATAFIM=11/03/2020"]
                )

        self.assertEqual(link, response)
    
    def test_get_coins_response_keys(self):
        BCBApi.navigate()
        BCBApi.get_coins()
        
        response = ['simbolo', 'name']
        
        keys = BCBApi.coins[list(BCBApi.coins.keys())[0]].keys()

        self.assertEqual(list(keys), response)
    
    def test_get_price_response_keys(self):
        date=parse_date(self.date,'d/m/y')
        BCBApi.get_prices(date)
        
        response = [
            "simbolo",
            "paridadeCompra_USD",
            "paridadeVenda_USD",
            "paridadeCompra_BRL",
            "paridadeVenda_BRL",
            "name",
        ]
        clean_date = parse_date(self.date, 'dmy')
        keys = BCBApi.prices[clean_date][list(BCBApi.prices[clean_date].keys())[0]].keys()
        self.assertEqual(list(keys), response)

class test_main(TestCase):
    def setUp(self) -> None:
        self.date = '20200310'
        self.BaseUrl = "https://ptax.bcb.gov.br/"
        self.cache = {
                "expire": {
                    "prices": 1584370559.542857,
                    "coins": 1584370559.542866,
                    "default": 1584370559.542868
                },
                "coins": {
                    "1": {
                        "simbolo": "AFN",
                        "name": "AFEGANE AFEGANIST"
                    },
                    "2331": {
                        "simbolo": "MGA",
                        "name": "ARIARY MADAGASCAR"
                    },
                    "222": {
                        "simbolo": "EUR",
                        "name": "EURO"
                    },
                    "61": {
                        "simbolo": "USD",
                        "name": "DOLAR DOS EUA"
                    },
                },
                "prices":{
                "10032020": {
                    "USD": {
                        "simbolo": "USD",
                        "paridadeCompra_USD": 4,
                        "paridadeVenda_USD": 4,
                        "paridadeCompra_BRL": 4,
                        "paridadeVenda_BRL": 4,
                        "name": "NOT DEFINED"
                    },
                    "EUR": {
                        "simbolo": "EUR",
                        "paridadeCompra_USD": 1.1341,
                        "paridadeVenda_USD": 1.1343,
                        "paridadeCompra_BRL": 5.2948,
                        "paridadeVenda_BRL": 5.2964,
                        "name": "EURO"
                    },
                    "AFN": {
                        "simbolo": "AFN",
                        "paridadeCompra_USD": 76.06,
                        "paridadeVenda_USD": 76.26,
                        "paridadeCompra_BRL": 0.06122,
                        "paridadeVenda_BRL": 0.06139,
                        "name": "AFEGANE AFEGANIST"
                    },
                    "MGA": {
                        "simbolo": "MGA",
                        "paridadeCompra_USD": 3631.0,
                        "paridadeVenda_USD": 3750.0,
                        "paridadeCompra_BRL": 0.001245,
                        "paridadeVenda_BRL": 0.001286,
                        "name": "ARIARY MADAGASCAR"
                    }
                    
                }
            }
}
    
    def test_parse_date(self):
        date = parse_date(self.date, 'd/m/y')

        self.assertEqual(date, '10/03/2020')
    
    def test_get_lower_price_cache(self):
        lower_price = get_lower_price(self.date,_cache=self.cache['prices'])
        response = {
                    "simbolo": "MGA",
                    "paridadeCompra_USD": 1/3631.0,
                    "paridadeVenda_USD": 3750.0,
                    "paridadeCompra_BRL": 0.001245,
                    "paridadeVenda_BRL": 0.001286,
                    "name": "ARIARY MADAGASCAR"
                }
        self.assertDictEqual(lower_price,response)

    
    def test_parse_prices_cache(self):
        parsed_price = parse_prices(self.date, _cache=self.cache['prices'])
        response = 'MGA, ARIARY MADAGASCAR, 0.00027541'#'VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001369'
        self.assertEqual(parsed_price, response)




if __name__ == "__main__":
    unittest.main()