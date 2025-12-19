import socket
import urllib3

from requests import Session, exceptions
from schemas.check_public_ip.ipify import get_public_ip
from proxy_logger import logger


def current_ip(sess:Session, certificate):
    return get_public_ip(sess, certificate)


def test_proxy(ip:str, port, protocol:str, sess:Session, certificate, old_ip:str) -> bool:
    url = ip + ':' + port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
            
        #parsed_url = urllib3.parse.urlparse(url)
        #hostname = parsed_url.hostname
        
        #IP = socket.gethostbyname(hostname) #Se for hostname
        #PORT = parsed_url.port            
        sock.connect((ip, int(port)))
        sock.close()
        
        scheme = (
            protocol + 'a' if protocol == 'socks4' else
            protocol + 'h' if protocol == 'socks5' else
            protocol.replace('https', 'http')
        )
        
        new_ip = get_public_ip(
            sess, 
            certificate,
            {
                'http': f'{scheme}://{url}',
                'https': f'{scheme}://{url}'
            }
        )
        
        if new_ip != old_ip:
            logger.info(f"New IP found: {new_ip} using {url}")
            
            return True
        else:
            raise Exception(f"Public IP isn't new using {url} proxy, skipped.")

    except exceptions.HTTPError as e:
        logger.error("Request failed with status code:", e.response.status_code)
        return False
    
    except socket.gaierror as e:
        logger.error(f"Could not resolve hostname due to error: {repr(e)}")
        return False 
        
    except Exception as e:
        logger.error(f'Request failed due to error: {repr(e)}')
        return False