import argparse
import csv
import json
import requests
import os
import time

from jinja2 import Template
from proxy_validator import test_servers
from proxy_custom_arg_types import str_bool_switcher_type, tuple_type

#pip install -U requests[socks]

requests.adapters.DEFAULT_RETRIES = 1

class ProxyReceiver(object):
    def __init__(self, certificate, time_out):
        self.sess = requests.Session()
        self.sess.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0'})
        self.certificate = certificate
        self.time_out = time_out
        
        try:
            self.rex = self.sess.get('https://api.ipify.org?format=json', timeout=10, verify=self.certificate) #Recebe IP público atual.
            self.rex.raise_for_status()
            self.old_ip = json.loads(self.rex.text)['ip']
            
            print(f"---\nCurrent IP: {self.old_ip}")
        
        except requests.exceptions.HTTPError as e:
            self.old_ip = '0.0.0.0'
            print("---\nIP_API failed with status code:", e.response.status_code)
            
        except Exception as e:
            self.old_ip = '0.0.0.0'
            print(f"---\nIP_API request failed due to error: {e}")
        
        
    def retrieve_free_proxy_list(self, url, protocol):       
        try:
            new_url = url.render(protocol_value=protocol)
            print(f'---\nProxy List API URL: {new_url}')
            
            res = self.sess.get(new_url, timeout=10, verify=self.certificate)                  
            return res.text
                        
        except Exception as e:
            print(f'---\nRequesting proxy list failed due to error: {e}\n---')
            return ''
    
    
    def open_file(self, path):
        db_file = open(path, 'a+', newline='', encoding="utf-8")
        db_writer = csv.writer(db_file, delimiter=",", dialect='excel', lineterminator="\r\n")    
        db_reader = csv.reader(db_file, delimiter=",", dialect='excel', lineterminator="\r\n")
        db_file.seek(0)
        
        if next(db_reader, None) is None:
            db_writer.writerow(['url', 'port', 'protocol'])
                    
        return db_file, db_writer, db_reader
    
    
    def write_valid_list(self, content, protocol, out, limit):
        new_content = content.replace(" ", "").split('\r\n')
        
        print(f"---\nThere were {len(new_content)} occurrences found.")
        
        path = os.path.join(out, 'proxy_db.csv')
        i = 0
        
        db_file, db_writer, db_reader = self.open_file(path)
        
        for index, row in enumerate(new_content):
            if i >= limit > 0:
                break
            
            elif index < len(new_content) - 1:
                db_file.seek(0)
                already_exists = False
                
                for index_file, file_row in enumerate(db_reader):
                    if index_file == 0:
                        continue
                    
                    elif file_row[1].strip() == '': #Se for hostname
                        if row == file_row[0].strip():
                            already_exists = True
                            break
                        
                    elif row == f'{file_row[0]}:{file_row[1]}'.strip():
                        already_exists = True
                        break
                    
                if not already_exists:
                    if test_servers(protocol, row, self.sess, self.certificate, self.old_ip):
                        db_file.seek(0, 2)
                        
                        try:
                            db_writer.writerow([f'{row.split(":")[0]}', f'{row.split(":")[1]}', protocol])
                        except IndexError:
                            db_writer.writerow([row, '', protocol]) #Se for hostname
                        finally:
                            i+=1
                            
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
    
    try:
        client = ProxyReceiver(args.certificate, args.time_out)
        
        for protocol in args.protocols:
            print(f'---\nProtocol selected: {protocol}')
            
            content = client.retrieve_free_proxy_list(args.link, protocol)
            client.write_valid_list(content, protocol, args.output_folder, args.limit)
        
        client.sess.close()
        
    except KeyboardInterrupt:
        print("---\nOperation terminated by user.\n---")
        
