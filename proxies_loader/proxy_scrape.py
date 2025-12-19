import argparse
import json
import requests
import os, sys
import time

from proxy_logger import logger
from proxy_validator import ProxyTester
from initialization_args.custom_arg_types import str_bool_switcher_type


requests.adapters.DEFAULT_RETRIES = 0

class ProxyReceiver(object):
    def __init__(self, certificate, time_out:float, api_name:str, test_provider:str) -> None:
        self.sess = requests.Session()
        
        if type(certificate) is bool:
            self.sess.verify = certificate
        else:
            self.sess.cert = certificate
        self.sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        
        self.proxy_tester = ProxyTester(self.sess, test_provider)

        self.api_name = api_name
        self.time_out = time_out
        
        
    def retrieve_free_proxy_list(self) -> list[dict]:       
        try:
            match self.api_name:
                case 'geonode':
                    from proxy_list_api_modules.geonode import GeonodeClasss as ProxyListApi
                    
                case 'roundproxies':
                    from proxy_list_api_modules.roundproxies import RoundProxiesClasss as ProxyListApi
                    
            self.api_class = ProxyListApi()
                
            new_url = self.api_class.build_schema_url(self.get_current_directory(
                    os.path.join('schemas', 'proxy_providers_config', self.api_name + '.json')
                )
            )
            logger.info(f'Proxy List API URL: {new_url}')
            
            return self.api_class.build_schema_response(self.sess.get(new_url, timeout=10))
                        
        except Exception as e:
            logger.error(f'Requesting proxy list failed due to error: {repr(e)}')
            return []
    
    
    def open_file(self, path:str):
        try:
            return self.file_mode(path, 'r+')
        except FileNotFoundError:
            return self.file_mode(path, 'w+')
    
    
    @staticmethod
    def file_mode(path, mode:str):
        return open(os.path.join(path, 'Proxy List.json'), mode, encoding="utf-8")
    
    
    @staticmethod
    def write_file(file, data:dict) -> None:
        file.seek(0, 0)
        json.dump(data, file, indent=4)
        file.truncate()
    
    
    def write_valid_list(self, new_content:list[dict], out:str, limit:int):
        len_new_content = len(new_content)
        logger.info(f"There are {len_new_content} occurrences found.")
        
        file = self.open_file(out)        
        try:
            current_content = json.load(file)
            
        except json.JSONDecodeError:
            current_content = {
                'protocolsCount': {},
                'proxies': []
            }
        
        def test(server:dict, protocol:str) -> bool:            
            ip = server['ip']
            port = server['port']
            logger.info(f'Testing {ip}:{port} with protocol {protocol}')
            
            return self.proxy_tester.test_proxy(ip, port, protocol)
        
        def subtract_new_content(index:int) -> None:
            nonlocal len_new_content
            len_new_content-=1
            
            new_content.pop(index)
        
        index = 0
        while index < len_new_content:
            try:
                server = self.api_class.fix_data(new_content[index])
            except:
                subtract_new_content(index)
                logger.error('Invalid data, skipped.')
                continue
            
            protocol = server['protocol']
            try:                
                if current_content['protocolsCount'][protocol] == limit:
                    subtract_new_content(index)
                    continue
                
                if test(server, protocol):
                    self.api_class.confirm(server)
                    current_content['protocolsCount'][protocol] +=1
                    index += 1
                    
                    time.sleep(self.time_out)
                    continue
                            
            except KeyError:
                if test(server, protocol):
                    self.api_class.confirm(server)
                    current_content['protocolsCount'][protocol] = 1
                    index += 1
                    
                    time.sleep(self.time_out)
                    continue
            
            subtract_new_content(index)
            time.sleep(self.time_out)
            
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
    parser.add_argument('-i', '--test_provider', type=str, default='ipify')
    parser.add_argument('-c', '--certificate', type=str_bool_switcher_type, default=True) #Path to the ssl.pem certificate file
    parser.add_argument('-t', '--time_out', type=float, default=0.5)
    parser.add_argument('-o', '--output_folder', type=str, required=True)

    args = parser.parse_args()
    
    client = ProxyReceiver(
        args.certificate, 
        args.time_out,
        args.api_name.lower().replace(' ', ''), 
        args.test_provider.lower().replace(' ', '')
    )
    try:
        client.write_valid_list(client.retrieve_free_proxy_list(), args.output_folder, args.limit)

    except KeyboardInterrupt:
        pass
    logger.info("Operation terminated.")