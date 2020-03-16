import os
from main import *
from cache import set_time_expire

__DIRNAME__ = os.sys.path[0]

help_text = """
-loop            :  Chama um loop para melhor digitação contínua.para sar do loop basta digitar -q

-from            :  Utiliza as datas do arquivo especificado
                    OBS: Passando o caminho sem a barra inicial será buscado o arquivo na pasta 
                    da aplicação

-to              :  Salva as respostas no arquivo especificado junto com a respectiva data
                    OBS: Passando o caminho sem a barra inicial será buscado o arquivo na pasta 
                    da aplicação
                    OBS2: no caso do -loop todas as respostas serão salvas no caminho que foi 
                    especificado no inicio do mesmo

--set-cache-time :  Altera o tempo de vida do cache. O valor deve ser um inteiro ou um 
                    inteiro começando com a letra correspondente a unidade de tempo desejada. 
                    Note que caso não seja fornecida nenhuma unidade de mediada o valor 
                    fornecido será registrado como segundos

                    'D':DIA
                    'M':MES
                    'Y':ANO
                    'h':hora
                    'm':minuto
                    's':segundo

                    pode ser passado tambem o parametro -field para especificar qual tabela 
                    alterar, caso não seja passado o campo "default" que será alterado.
                    OBS: os prefixos são case sensitve.
--reload-simbols :  Força a atualização do cache dos simbolos
"""

class Cli:
    
    def __init__(self):
        self._exclude = []
        self._args = {}
        self.cmd_to = ''

    
    def get_price_from_dates(self, dates:list, to=''): 
        for date in dates:

             if 0<len(date)<8 and  date[0]!='-':  
                print(f'Data: {date} em formato incorreto')

        lower_price = [parse_prices(_price.strip()) for _price in dates if len(_price)>=8]
        responses ='\n'.join(lower_price).strip('\n')

        if to:
            file_path = to if to[0]=='/' else os.path.join(__DIRNAME__,to)

            with open(file_path,'a') as resp_file:

                save_resp = [
                    f'{dates[i]}, {lower_price[i]}' for i in range(len(lower_price))
                ]

                resp_file.write('\n'.join(save_resp)+'\n')
            
        return responses


    def cmd__set_cache_time(self, arg:str, list_args, **kwargs):
        time = False
        field = 'default' if '-field' not in list_args.keys() else list_args['-field']
        conversor = {
            'D':86400,
            'M':2592000,
            'Y':94608000,
            'h':3600,
            'm':60,
            's':1
        }
        
        if arg[0] in ['D','M','Y','h','m','s']:
            time = int(arg[1:])*conversor[arg[0]]

        elif arg.isnumeric():
            time = int(arg)

        if time!=False:
            set_time_expire(time, field)

    
    def cmd_loop(self, arg, list_args, **kwargs):
        work = True

        while work:
            input_date = input(':> ')

            if '-q' in input_date:
                print('saindo...')
                work = False
            
            dates = [date for date in input_date.split()]
            to = '' if '-to' not in list_args.keys() else list_args['-to']

            print(self.get_price_from_dates(dates,to=to))


    def cmd_from(self, arg, list_args, **kwargs):
        file_path = arg if arg[0]=='/' else os.path.join(__DIRNAME__,arg)

        with open(file_path,'r') as date_file:

            to = '' if '-to' not in list_args.keys() else list_args['-to']
            response = self.get_price_from_dates(
                            date_file.read().split(),
                            to=to
                        )
            
            print(response)

    def cmd_tests(self, arg, list_args={}, **kwargs):
        os.system(f'python3 {os.path.join(__DIRNAME__,"tests.py")}')
    
    def __default__(self, arg, list_args, **kargs):
        dates = [list_args[a] for a in list_args.keys() if type(a) == int]
        to = '' if '-to' not in list_args.keys() else list_args['-to']

        print(self.get_price_from_dates(dates,to=to))

    
    def parse_args(self, list_args:list):
        """get a list of args and convert do dict of all args and values."""    

        for i in range(len(list_args)):

            if list_args[i][0] == "-":
                try:
                    _next_arg=list_args[i+1]
                    if _next_arg[0] != "-":

                        if _next_arg[0]=="'" or _next_arg[0]=='"':

                            arg_parts = []
                            firstKey = _next_arg[0]

                            for word in list_args[i+1:]:
                                arg_parts.append(word)
                                self._exclude.append(word)

                                if word[-1] == firstKey:
                                    break

                            self._args[list_args[i]] = ' '.join(arg_parts)[1:-1]
                            
                        else:
                            self._args[list_args[i]] = list_args[i + 1]
                            self._exclude.append(list_args[i + 1])

                    else:
                        self._args[list_args[i]] = True

                except IndexError:
                    self._args[list_args[i]] = True

            elif list_args[i] not in self._exclude:
                self._args[i] = list_args[i]
    
    
    def cmd__help(self, arg:any, list_args:dict, **kwargs)->None:
        help = help_text
        print(help)

    
    def __get_cmds__(self)->dict:
        cmds = {}

        for method in self.__dir__():

            if "cmd_" == method[:4]:
                cmds[f'-{method[4:]}'.replace('_','-')] = self.__getattribute__(method)

        return cmds

    
    def cmd__reload_simbols(self, arg:any, list_args:dict, **kwargs)->None:
        get_simbols()
        
    
    def run_commands(self, **kwargs)->None:
        _cmd = self.__get_cmds__()

        for key in self._args.keys():
            try:
                _cmd[key](self._args[key], self._args, **kwargs)
                
            except KeyError as k:
                self.__default__(self._args[key], self._args, **kwargs)

            except TypeError as t:

                if type(_cmd[key]) == bool:
                    pass

                if type(_cmd[key]) == str:
                    print(_cmd[key])

            return None

    
    
    def listen_os(self,**kwargs):

        self.parse_args(os.sys.argv[1:])
        self.run_commands(**kwargs)

try:
    Cli().listen_os()
    
finally:
    BCBApi.close()