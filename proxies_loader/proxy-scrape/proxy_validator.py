import json
import socket
import requests
import urllib3

def test_servers(protocol, url, sess, certificate, old_ip):    
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
            print(f"---\nNew IP found: {json.loads(resp.text)['ip']} using {url}")
            return True 
        else:
            raise Exception(f"---\nPublic IP isn't new using {url}, skipped.")

    except requests.exceptions.HTTPError as e:
        print("---\nRequest failed with status code:", e.response.status_code)
        return False
    
    except socket.gaierror as e:
        print(f"---\nCould not resolve hostname due to error: {e}")
        return False     
        
    except Exception as e:
        print(f'---\nRequest failed due to error: {e}')
        return False