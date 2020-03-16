## BREAFING
Obter a cotação da moeda a partir do site do Banco Central
Você foi contratado como freelancer por uma empresa de análise de dados que precisa de uma solução para o seguinte problema:

Todos os dias a empresa precisa saber qual moeda possui a menor cotação frente ao dólar. Essa informação é importante para uma outra aplicação de ranking de moedas que eles irão desenvolver.

O gerente da empresa que te contratou te passou o link do banco central (https://www.bcb.gov.br/) como referência. Ele mesmo também não conhece o site do BC detalhadamente para indicar o lugar exato da fonte de dados, mas sabe que é possível baixar um arquivo com os dados desejados a partir do portal.

Neste momento, o que eles precisam é um programa que receba uma data no formato YYYYMMDD via terminal e exiba na saída uma linha com as seguintes informações separadas por vírgula:

* o símbolo da moeda com menor cotação, 
* o nome do país de origem da moeda e
* o valor da cotação desta moeda frente ao dólar na data especificada.

Caso não haja cotação no dia especificado o caracter x deve ser impresso na tela.

Escreva um programa que atenda aos requisitos acima.

## Docker

Para criar uma imagem docker basta entrar no diretório da aplicação e passar o comando:

``` 
docker build . -t lower_price:1.0
```

e em seguida:

``` 
docker run -it lower_price:1.0
```

para entrar no container. Dentro do mesme é possivel realizar as consultas chamando o variavel de ambiente `lower-price` 

No momento da montagem do container é passado o comando `--reload-simbols` para criar um cache com a relação dos simbolos e locais das moedas

``` 
$ lower-price --reload-simbols
Reload cache of currency symbols: 0.00%
Reload cache of currency symbols: 0.41%
Reload cache of currency symbols: 0.82%
Reload cache of currency symbols: 1.22%
```

## Visão Geral

A aplicação consiste em 4 modulos principais `Cli` , `main` , `crawler` , e `cache` 

### Cli

O modulo Cli foi feito para facilitar o gerenciamentos dos comandos e parametros passados.

Pela linha de comando é possivel passar diretamente a(s) data(s) desejadas

``` 
$ lower-price 20200310
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001369
```

ou

``` 
$ lower-price 20200310 20200311
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001369
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001367
```

Ou chamar os comandos abaixo:

**-loop**
Chama um loop para melhor digitação contínua.para sar do loop basta digitar **-q**

``` 
$ lower-price -loop
:> 20200308
x
:> 20200305
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001361
:> 20200216 2020030geckodriver.log1
x
x
:> -q
```

**-from**
Utiliza as datas do arquivo especificado

Obs: Passando o caminho sem a barra inicial será buscado o arquivo na pasta da aplicação

_dates.txt_

``` 
20200310
20200311
20200214
```

``` 
$ lower-price -from dates.txt
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001369
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001367
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001362
```

**-to** 
Salva as respostas no arquivo especificado junto com a respectiva data
Obs: Passando o caminho sem a barra inicial será buscado o arquivo na pasta da aplicação

``` 
$ lower-price -from dates.txt -to resp.txt
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001369
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001367
VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001362
```

_resp.txt_

``` 
20200310, VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001369
20200311, VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001367
20200214, VES, BOLIVAR SOBERANO VENEZUELANO, 0.00001362
```

Obs2: no caso do **-loop** todas as respostas serão salvas no caminho que foi especificado no inicio do mesmo

``` 
$ lower-price -loop -to resp.txt
:>
```


**--set-cache-time**
Altera o tempo de vida do cache. O valor deve ser um inteiro ou um inteiro começando com a letra correspondente a unidade de tempo desejada. Note que caso não seja fornecida nenhuma unidade de mediada o valor fornecido será registrado como segundos

``` 
'D':DIA
'M':MES
'Y':ANO
'h':hora
'm':minuto
's':segundo
```

pode ser passado tambem o parametro **-field** para especificar qual tabela alterar, caso não seja passado o campo "default" que será alterado.

``` 
$ lower-price --set-cache-time D2 -field coins
```

OBS: ps prefixos são case sensitve.

Para utilizar a aplicação sem o containter basta chamar `python3 Cli.py <comandos>` 

### Crawler

É o módulo responsavel pela coleta dos dados junto ao site. Inicialmente seria utilizada a própria API do BCB porem a mesma não fornecia todas a moedas disponiveis para cotação.

Para realizar a coleta dos dados é utilizado o selenium jundo com o chromedriver que roda em segundo plano.

Dentro dessa classe há tres métodos principais:

**get_coins()**
responsavel pela busca das moedas disponiveis para consulta no link:https://ptax.bcb.gov.br/ptax_internet/consultaBoletim.do?method=consultarBoletim e salva no arquivo de *cache*

**get_simbols(date)**_formato d/m/y_
Como não é possivel saber os simbolos das moedas pelo codigo fonte da pagina é feita a verificação individual e a medida que as os simbolos são encontrados tambem é atualizado no arquivo de *cache*

**get_prices(date)** _formato dmy_
busca o boletim do dia com a tabela das cotações de todas as moedas disponiveis e salvas no cache. Caso não aja boletim é adicionada um moeda com o simbolo "ERROR".

e alem desses métodos há o **make_dataset(date)** *formato d/m/y* que simplesmente verifica se é possivel buscar a informação no cache ou sequencia os passos acima e devolve a resposta

### main

Modulo principal de onde partem as solicitações e é feita a formataçã das datas e das respostas solicitadas.

### cache

Por depender de um crawler para obter os dados um arquivo de cache é necessário mara melhor performace.por padrão o tempo de vida do cache é de 24h após esse.

Todas informações de cache ficam armanenadas no arquivo `__CACHE__.json` , caso este não seja encontrado é criado. Ele é composto por três "tabelas" `expire` , `coins` , `prices` :

``` json
{
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
    },
    "prices":{
    "<DATA>": {
        "USD": {
            "simbolo": "USD",
            "paridadeCompra_USD": 4,
            "paridadeVenda_USD": 4,
            "paridadeCompra_BRL": 4,
            "paridadeVenda_BRL": 4,
            "name": "NOT DEFINED"
        }
        
    }
    }
}
```

**expire**
espefica quanto cata tabela tem de vida a data de validade(em timestamp) que cada tabela tem de vida.É atualizado automaticamente a cada fim de ciclo.os valores padroẽs podem ser alterados no arquivo `.cache.config` 

``` json
{
    "expire_time":{
        "default":86400,
        "coins":null,
        "prices":null

    }
}
```

caso esteja null será pego o valor default, note que o tempo está em segundos para facilitar converções.

**coins**
Inicialmente como é executado o metodo **Browser.get_coins()** todas as moedas são salvas como

``` json
"1": {
    "simbolo": null,
    "name": "AFEGANE AFEGANIST"
    }
```

após a execução do metodo  **Browser.get_simbols(date)** caso o simbolo da moeda seja encontrado é atualizado o `__CACHE__ .json` como o mesmo, caso contrário é resgistrado com "null"(em formato de string) para sinalizar que o mesmo foi procurado mas não foi encontrado evitando buscas desnecessárias.

``` json
"1": {
    "simbolo": "null",
    "name": "AFEGANE AFEGANIST"
    }
```

**prices**
Contem as cotações das moedas nas respectivas datas. No caso de datas que não possuem boletim financeiro, recebem duas moedas "ERROR" e "USD".

``` json
"17052020": {
            "ERROR": {
                "simbolo": "NULL",
                "paridadeCompra_USD": 1,
                "paridadeVenda_USD": 1,
                "paridadeCompra_BRL": 1,
                "paridadeVenda_BRL": 1,
                "name": "NOT DEFINED"
            },
            "USD": {
                "simbolo": "NULL",
                "paridadeCompra_USD": 1,
                "paridadeVenda_USD": 1,
                "paridadeCompra_BRL": 1,
                "paridadeVenda_BRL": 1,
                "name": "NOT DEFINED"
            }
        },
```


<hr>

### Decorators
Possui apenas o decorator `@feedback` para facilitar possiveis menssagens de erro 