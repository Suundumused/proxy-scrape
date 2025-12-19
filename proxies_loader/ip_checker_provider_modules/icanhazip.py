from requests import Session


def get_public_ip(sess:Session, proxies:dict=None) -> str:
    rex = sess.get('https://icanhazip.com/', proxies=proxies, timeout=10)
    rex.raise_for_status()
    
    return rex.content.decode()