import argparse
import csv
import json
import requests
import os, sys
import time

from proxy_logger import logger
from proxy_validator import test_proxy, current_ip
from initialization_args.custom_arg_types import str_bool_switcher_type, tuple_type


requests.adapters.DEFAULT_RETRIES = 0

class ProxyReceiver(object):
    def __init__(self, certificate, time_out:float, api_name:str) -> None:
        self.sess = requests.Session()
        self.sess.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'})
        self.api_name = api_name
        self.certificate = certificate
        self.time_out = time_out
        self.old_ip = current_ip(self.sess, self.certificate)
        
        
    def retrieve_free_proxy_list(self) -> str:       
        try:
            match self.api_name:
                case 'geonode':
                    from proxy_list_api_modules.geonode import GeonodeClasss as ProxyListApi
                    self.api_class = ProxyListApi()
                
            new_url = self.api_class.build_schema_url(self.get_current_directory(
                    os.path.join('schemas', 'proxy_list_api', self.api_name + '_api', self.api_name + '.json')
                )
            )
            logger.info(f'Proxy List API URL: {new_url}')
            
            return self.api_class.build_schema_response(self.sess.get(new_url, timeout=10, verify=self.certificate))
        
        except KeyboardInterrupt:
            quit()
                        
        except Exception as e:
            logger.error(f'Requesting proxy list failed due to error: {repr(e)}')
            return ''
    
    
    @staticmethod
    def open_file(path:str):
        return open(os.path.join(path, 'Proxy List.json'), 'w+', encoding="utf-8")
    
    
    @staticmethod
    def write_file(file, data:dict) -> None:
        json.dump(data, file, indent=4)
    
    
    def write_valid_list(self, new_content:list[dict], out:str, limit:int):
        logger.info(f"There are {len(new_content)} occurrences found.")
        
        file = self.open_file(out)        
        try:
            current_content = json.load(file)
            current_content['protocolsCount'] = {}
        except:
            current_content = {
                'protocolsCount': {},
                'proxies': []
            }
        
        def test(server:dict, protocol:str) -> bool:            
            ip = server['ip']
            port = server['port']
            
            logger.info(f'Testing {ip}:{port} with protocol {protocol}')
            
            return test_proxy(ip, port, protocol, self.sess, self.certificate, self.old_ip)
        
        index = 0
        while index < len(new_content):    
            server = self.api_class.fix_data(new_content[index])
            protocol = server['protocol']
            
            try:                
                if current_content['protocolsCount'][protocol] > limit:
                    continue
                
                if test(server, protocol):
                    current_content['protocolsCount'][protocol] +=1
                    self.api_class.confirm(server)
                    
                    index += 1
                    continue
                            
            except KeyError:
                if test(server, protocol):
                    current_content['protocolsCount'][protocol] = 1
                    self.api_class.confirm(server)
                    
                    index += 1
                    continue
            
            new_content.pop(index)
            time.sleep(self.time_out)
            
        print(current_content['protocolsCount'])
        del current_content['protocolsCount']
        current_content['proxies'].extend(new_content)
        
        self.write_file(file, current_content)
            
 
    @staticmethod
    def get_current_directory(path:str = None):
        newpath = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(sys.argv[0]))

        return os.path.join(newpath, path) if path else newpath
      
      
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-l', '--limit', type=int, default=3) # -1 no limit.        
    parser.add_argument('-a', '--api_name', type=str, default='geonode')
    parser.add_argument('-c', '--certificate', type=str_bool_switcher_type, default=True) #Path to the ssl.pem certificate file
    parser.add_argument('-t', '--time_out', type=float, default=0.5)
    parser.add_argument('-o', '--output_folder', type=str, required=True)

    args = parser.parse_args()
    
    client = ProxyReceiver(args.certificate, args.time_out, args.api_name)
    try:
        client.write_valid_list(client.retrieve_free_proxy_list(), args.output_folder, args.limit)

    except KeyboardInterrupt:
        pass
    logger.info("Operation terminated.")