import socket
import urllib3

from requests import Session, exceptions
from ip_checker_provider_modules.ipify import get_public_ip
from proxy_logger import logger


class ProxyTester(object):
    def __init__(self, sess:Session) -> None:
        self.sess = sess
        self.old_ip = get_public_ip(self.sess)


    def test_proxy(self, ip:str, port, protocol:str) -> bool:
        url = ip + ':' + port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            
            #parsed_url = urllib3.parse.urlparse(url)
            #hostname = parsed_url.hostname
            #ip = socket.gethostbyname(hostname) #If hostname
            #port = parsed_url.port            
            
            sock.connect((ip, int(port)))
            sock.close()
            
            scheme = (
                protocol + 'a' if protocol == 'socks4' else
                protocol + 'h' if protocol == 'socks5' else
                protocol.replace('https', 'http')
            )

            new_ip = get_public_ip(
                self.sess, 
                {
                    'http': f'{scheme}://{url}',
                    'https': f'{scheme}://{url}'
                }
            )
            
            if new_ip != self.old_ip:
                logger.info(f"Proxy server functioning correctly. {url}")
                return True
            else:
                raise Exception(f"The public IP address was not masked with proxy {url}, skipped.")

        except exceptions.HTTPError as e:
            logger.error("Request failed with status code:", e.response.status_code)
            return False
        
        except socket.gaierror as e:
            logger.error(f"Could not resolve hostname due to error: {repr(e)}")
            return False 
            
        except Exception as e:
            logger.error(f'Request failed due to error: {repr(e)}')
            return False