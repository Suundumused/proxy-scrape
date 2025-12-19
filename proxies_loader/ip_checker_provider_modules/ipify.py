from requests import Session
from json import loads


class IpifyProvider(object):
    def __init__(self, sess:Session):
        self.sess = sess
        

    def get_public_ip(self, proxies:dict=None) -> str:
        rex = self.sess.get('https://api.ipify.org?format=json', proxies=proxies, timeout=10)
        rex.raise_for_status()
        
        return loads(rex.text)['ip']