import json
from datetime import datetime
__path_cache__= './__CACHE__.json'
try:
    __CACHE__:dict = json.load(open(__path_cache__,'r'))
except FileNotFoundError:
    with open(__path_cache__,'w') as File:
        File.write('{}')
    __CACHE__:dict = json.load(open(__path_cache__,'r'))

timestamp_day = 86400


if 'expire' not in __CACHE__.keys():
    __CACHE__['expire'] = datetime.now().timestamp()+timestamp_day


def is_expired():
    if __CACHE__['expire'] - datetime.now().timestamp()>0:
        return False    
    return True


def cache_update(**tables):
    if is_expired():
        print('LIMP')
        __CACHE__.clear()
        __CACHE__['expire'] = datetime.now().timestamp()+timestamp_day
    

    __CACHE__.update(tables)
    json.dump(__CACHE__,open(__path_cache__,'w'))

def get_cache(date, coin):
    try:
        if not is_expired():
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

    json.dump(__CACHE__,open(__path_cache__,'w'))

def get_coin(code):
    try:
        if not is_expired():
            return __CACHE__['coins'][code]
    except KeyError:
        return None
    
    return None

def set_coin(code, response):
    if 'coins' not in __CACHE__.keys():
        __CACHE__['coins']={}
    
    __CACHE__['coins'][code] = response

    json.dump(__CACHE__,open(__path_cache__,'w'))

def get_name_by_simbol(simbol):
    try:
        if not is_expired():
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