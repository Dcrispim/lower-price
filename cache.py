import json
import os
from datetime import datetime


__path_cache__= f'{os.sys.path[0]}/__CACHE__.json'
__path_cache_config__= f'{os.sys.path[0]}/.cache.config'

try:
    __CACHE__:dict = json.load(open(__path_cache__,'r'))

except FileNotFoundError:
    with open(__path_cache__,'w') as File:
        File.write('{}')
    __CACHE__:dict = json.load(open(__path_cache__,'r'))


try:
    _CONFIG_:dict = json.load(open(__path_cache_config__,'r'))

except FileNotFoundError:
    with open(__path_cache_config__,'w') as ConfigFile:
        ConfigFile.write('{"expire_time":{"default":86400,"coins":null,"prices":null}}')
    _CONFIG_:dict = json.load(open(__path_cache_config__,'r'))


expire_time = _CONFIG_['expire_time']


def get_expire(table='default'):
    try:
        return expire_time[table] if expire_time[table] else expire_time['default']

    except KeyError:
        return expire_time['default']




def is_expired(table='default'):
    if __CACHE__['expire'][table] - datetime.now().timestamp()>0:
        return False    

    return True


def cache_update(**tables):
    if is_expired('prices'):
        print('LIMP')
        __CACHE__.clear()
        __CACHE__['expire'] = datetime.now().timestamp()+expire_time
    
    __CACHE__.update(tables)

    with open(__path_cache__,'w') as _json_file:
        _json_file.write(json.dumps(__CACHE__))


def get_cache(date, coin):
    try:
        if not is_expired('prices'):
            return __CACHE__['prices'][date][coin]

    except KeyError:
        return None
    
    return None


def set_cache(date:str,coin:str, response):
    if 'prices' not in __CACHE__.keys():
        __CACHE__['prices']={}

    if date not in __CACHE__['prices'].keys():
        __CACHE__['prices'][date]={}
    
    __CACHE__[date][coin] = response

    with open(__path_cache__,'w') as _json_file:
        _json_file.write(json.dumps(__CACHE__))


def get_coin(code):
    try:
        if not is_expired('coins'):
            return __CACHE__['coins'][code]

    except KeyError:
        return None
    
    return None


def set_coin(code, response):
    if 'coins' not in __CACHE__.keys():
        __CACHE__['coins']={}
    
    __CACHE__['coins'][code] = response

    with open(__path_cache__,'w') as _json_file:
        _json_file.write(json.dumps(__CACHE__))


def get_name_by_simbol(simbol):
    try:
        if not is_expired('coins'):

            for coin in __CACHE__['coins'].keys():

                if __CACHE__['coins'][coin]['simbolo']==str(simbol).upper():

                    return __CACHE__['coins'][coin]['name']
                    
    except KeyError:
        return None
    
    return None


def get_cache_prices():
    try:
        return __CACHE__['prices']

    except:
        return {}


def clear_table(table):
    if table in __CACHE__.keys():
        __CACHE__[table].clear()

        with open(__path_cache__,'w') as _json_file:
            _json_file.write(json.dumps(__CACHE__))


def set_time_expire(_time, field='default'):
     _CONFIG_['expire_time'][field] = _time
     
     with open(__path_cache_config__,'w') as _json_file:
        _json_file.write(json.dumps(_CONFIG_))


if 'expire' not in __CACHE__.keys():
    __CACHE__['expire'] = {}
    __CACHE__['expire']['prices']=datetime.now().timestamp()+get_expire('prices')
    __CACHE__['expire']['coins']=datetime.now().timestamp()+get_expire('coins')
    __CACHE__['expire']['default']=datetime.now().timestamp()+get_expire('default')