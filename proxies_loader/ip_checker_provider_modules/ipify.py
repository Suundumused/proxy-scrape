from requests import Session
from json import loads


def get_public_ip(sess:Session, proxies:dict=None) -> str:
    rex = sess.get('https://api.ipify.org?format=json', proxies=proxies, timeout=10)
    rex.raise_for_status()
    
    return loads(rex.text)['ip']