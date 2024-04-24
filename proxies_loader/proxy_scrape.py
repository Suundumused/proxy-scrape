import argparse
import csv
import json
import requests
import os
import time

from jinja2 import Template
from proxy_logger import logger
from proxy_validator import test_servers
from proxy_custom_arg_types import str_bool_switcher_type, tuple_type

#pip install -U requests[socks]

requests.adapters.DEFAULT_RETRIES = 0


class ProxyReceiver(object):
    def __init__(self, certificate, time_out:float) -> None:
        self.sess = requests.Session()
        self.sess.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'})
        self.certificate = certificate
        self.time_out = time_out
        
        try:
            self.rex = self.sess.get('https://api.ipify.org?format=json', timeout=10, verify=self.certificate) #Recebe IP público atual.
            self.rex.raise_for_status()
            self.old_ip = json.loads(self.rex.text)['ip']
            
            logger.info(f"Current IP: {self.old_ip}")
        
        except requests.exceptions.HTTPError as e:
            self.old_ip = '0.0.0.0'
            logger.error(f"IP_API failed with status code: {e.response.status_code}")
            
        except Exception as e:
            self.old_ip = '0.0.0.0'
            logger.error(f"IP_API request failed due to error: {e.args[-1]}")
        
        
    def retrieve_free_proxy_list(self, url:str, protocol:str) -> str:       
        try:
            new_url = url.render(protocol_value=protocol)
            logger.info(f'Proxy List API URL: {new_url}')
            
            res = self.sess.get(new_url, timeout=10, verify=self.certificate)                  
            return res.text
        
        except KeyboardInterrupt:
            quit()
                        
        except Exception as e:
            logger.error(f'Requesting proxy list failed due to error: {e.args[-1]}')
            return ''
    
    
    def open_file(self, path:str):
        db_file = open(path, 'a+', newline='', encoding="utf-8")
        db_writer = csv.writer(db_file, delimiter=";", dialect='excel', lineterminator="\r\n")    
        db_reader = csv.reader(db_file, delimiter=";", dialect='excel', lineterminator="\r\n")
        db_file.seek(0)
        
        if next(db_reader, None) is None:
            db_writer.writerow(['url', 'port', 'protocol'])
                    
        return db_file, db_writer, db_reader
    
    
    def write_valid_list(self, content:str, protocol:str, out:str, limit:int):
        new_content = content.replace(" ", "").split('\r\n')
        logger.info(f"There were {len(new_content)} occurrences found.")
        
        path = os.path.join(out, 'proxy_db.csv')        
        db_file, db_writer, db_reader = self.open_file(path)
        len_new_content = len(new_content)
        
        for index in range(0, len_new_content-limit if 0 < limit < len_new_content else len_new_content):
            row = new_content[index]
            db_file.seek(0)
            already_exists = False
            
            for file_row in db_reader:
                var_file_row = file_row
                if var_file_row[1].strip() == '': #Se for hostname
                    if row == var_file_row[0].strip():
                        already_exists = True
                        break        
                elif row == f'{var_file_row[0]}:{var_file_row[1]}'.strip():
                    already_exists = True
                    break
                
            if not already_exists:
                if test_servers(protocol, row, self.sess, self.certificate, self.old_ip):
                    db_file.seek(0, 2)  
                    try:
                        db_writer.writerow([f'{row.split(":")[0]}', f'{row.split(":")[1]}', protocol])
                    except IndexError:
                        db_writer.writerow([row, '', protocol]) #Se for hostname
                time.sleep(self.time_out)
        db_file.close()

      
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-p', '--protocols', type=tuple_type, default=('socks5', 'socks4')) #ex: -p 'http','https'    
    parser.add_argument('-l', '--limit', type=int, default=3) # -1 sem limite.        
    parser.add_argument('-url', '--link', type=Template, default=Template('https://api.proxyscrape.com/v2/?request=displayproxies&protocol={{protocol_value}}&timeout=10000&country=all&ssl=all&anonymity=all')) #'https://www.proxy-list.download/api/v1/get?type={{protocol_value}}&anon=elite&country=US'
    parser.add_argument('-pem', '--certificate', type=str_bool_switcher_type, default=True) #Caminho do arquivo certificado ssl.pem
    parser.add_argument('-to', '--time_out', type=float, default=0.33)
    parser.add_argument('-out', '--output_folder', type=str, required=True)

    args = parser.parse_args()
    
    protocol:str = None
    content:str = None
    client = ProxyReceiver(args.certificate, args.time_out)
        
    for protocol in args.protocols:
        logger.info(f'Protocol selected: {protocol}')
        try:
            content = client.retrieve_free_proxy_list(args.link, protocol)
            client.write_valid_list(content, protocol, args.output_folder, args.limit)

        except KeyboardInterrupt:
            logger.info(f"Protocol {protocol} skipped by user.")
    logger.info("Operation terminated.")
