from requests import Session


class IcanhazipProvider(object):
    def __init__(self, sess:Session):
        self.sess = sess

    
    def get_public_ip(self, proxies:dict=None) -> str:
        rex = self.sess.get('https://icanhazip.com/', proxies=proxies, timeout=10)
        rex.raise_for_status()
        
        return rex.content.decode()