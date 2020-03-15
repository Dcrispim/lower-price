from crawler import close_browser
from main import *
import os

__DIRNAME__ = os.sys.path[0]

class Cli:
    def __init__(self):
        self._exclude = []
        self._args = {}

    def cmd_loop(self, arg, list_args, **kwargs):
        work = True
        while work:
            input_date = input(':> ')
            if '-q' in input_date:
                print('saindo...')
                work = False
            for date in input_date.split():
                if len(date) >= 8:
                    print(parse_prices(date))


    def cmd_tests(self, arg, list_args={}, **kwargs):
        os.system(f'python3 {os.path.join(__DIRNAME__,"tests.py")}')

    def __default__(self, arg, list_args, **kargs):
        dates = [list_args[a] for a in list_args.keys() if type(a) == int]
        lower_price = [parse_prices(_price) for _price in dates if len(_price)>=8]
        print('\n'.join(lower_price).strip('\n'))

    def parse_args(self, list_args:list):
        """get a list of args and convert do dict of all args and values
        """    
        for i in range(len(list_args)):
            if list_args[i][0] == "-":
                try:
                    _next_arg = list_args[i + 1]
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
        help = """"
        This Class help you to build a cli more easyer:
        """
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