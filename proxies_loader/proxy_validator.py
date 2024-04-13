import json
import socket
import requests
import urllib3

from proxy_logger import logger

requests.adapters.DEFAULT_RETRIES = 0


def test_servers(protocol:str, url:str, sess:requests.Session, certificate, old_ip:str) -> bool:    
    proxies = {'http': f'{protocol}://{url}',
                'https': f'{protocol}://{url}'}          
    try:    
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        try:
            IP, PORT = url.split(":")[0], int(url.split(":")[1])
            
        except IndexError:
            parsed_url = urllib3.parse.urlparse(url)
            hostname = parsed_url.hostname
            
            IP = socket.gethostbyname(hostname) #Se for hostname
            PORT = parsed_url.port            
        finally:
            sock.connect((IP, PORT))
            sock.close()
                        
        resp = sess.get('https://api.ipify.org?format=json', proxies=proxies, timeout=5, verify=certificate) #Testa receber novo IP público de api.my-ip.io com a proxy selecionada.
        resp.raise_for_status()
        
        if json.loads(resp.text)['ip'] != old_ip:
            logger.info(f"New IP found: {json.loads(resp.text)['ip']} using {url}")
            return True 
        else:
            raise Exception(f"Public IP isn't new using {url} proxy, skipped.")

    except requests.exceptions.HTTPError as e:
        logger.error("Request failed with status code:", e.response.status_code)
        return False
    
    except socket.gaierror as e:
        logger.error(f"Could not resolve hostname due to error: {e.args[-1]}")
        return False 
        
    except Exception as e:
        logger.error(f'Request failed due to error: {e.args[-1]}')
        return False
