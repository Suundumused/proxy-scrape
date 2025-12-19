from requests import Session


def get_public_ip(sess:Session, certificate, proxies:dict=None) -> str:
    rex = sess.get('https://icanhazip.com/', proxies=proxies, timeout=10, verify=certificate)
    rex.raise_for_status()
    
    return rex.content.decode()