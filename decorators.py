from typing import Callable

def feedback(IN:str='', OUT:str='', ERROR:str='')->Callable:
    """Print the feedback message IN or OUT for void functions and ERROR in case of error.\n
        :arg IN: str = Message before the function
        :arg OUT: str = Message after the function
        :arg ERROR: str = Error message (you can use the consts:
            '$FUNC' for the name func
            '$FILENAME' to get the file name
            '$LINE' to get the error line number
            '$ERROR' to get system message error
            '$ARGS' to get arguments
            '$FULLPATH' to get the full file path
            )

    Exemple:
        'Erro "$ERROR" em "$FUNC($ARGS)" em "$FILENAME" na linha "$LINE"
        'Erro "Index Error" em "fuction(arg1=2)" em "somefile.py" na linha "6"
    """

    def inner(func):
        def inner2(*arg,**kwargs):

            if IN:
                print(IN)

            try:
                _a = func(*arg, **kwargs)

            except Exception as err:

                def parse_erro_msg(msg):
                    name_erro = str(err)
                    fullpath = str(func.__globals__['__file__'])
                    File = fullpath.split('/')[-1]

                    line = str(err.__traceback__.tb_next.tb_lineno)
                    args = f'{",".join(arg)},{",".join([f"{k}={kwargs[k]}" for k in kwargs.keys()])}'.strip().strip(',')
                    
                    return msg.replace(
                            '$FUNC',func.__name__).replace(
                            '$FILENAME',File).replace(
                            '$LINE',line).replace(
                            '$ERROR', name_erro).replace(
                            '$ARGS', args
                            ).replace(
                            '$FULLPATH', fullpath
                            )

                _a = err

                if ERROR:
                    print(parse_erro_msg(ERROR))

                else:
                    print(parse_erro_msg(
                        'Erro "$ERROR" em "$FUNC($ARGS)" em "$FILENAME" na linha "$LINE"'
                    ))

            if OUT and type(_a)==type(None):
                print(OUT)

            return _a
        
        return inner2

    return inner

