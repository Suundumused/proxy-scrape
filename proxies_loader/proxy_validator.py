import socket
import urllib3

from requests import Session, exceptions
from proxy_logger import logger


class ProxyTester(object):
    def __init__(self, sess:Session, test_provider:str) -> None:                
        match test_provider:
            case 'ipify':
                from ip_checker_provider_modules.ipify import IpifyProvider as TestProvider
                
            case 'icanhazip':
                from ip_checker_provider_modules.icanhazip import IcanhazipProvider as TestProvider
        
        self.test_provider_instance = TestProvider(sess)
        self.old_ip = self.test_provider_instance.get_public_ip()
        
        logger.info(f'Selected Test Provider: {test_provider}')
        

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

            new_ip = self.test_provider_instance.get_public_ip(
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