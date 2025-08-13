# Proxy Scrape
Project to receive, validate and store a list of free proxies.

# Installation
 - `pip install -r .../Requirements.txt`

# Requirements
 - argparse
 - urllib3 
 - requests
 - jinja2 
 - requests[socks]
 - --
 - proxies_validator.py
 - custom_arg_types.py

## Usage 
These initial lines are required in proxy_scrape.py for basic functionality.

    import argparse
    import csv
    import json
    import requests
    import os
    import time
    
    from jinja2 import Template
    from proxies_validator import test_servers
    from custom_arg_types import str_bool_switcher_type, tuple_type
----
The Instance initially receives the arguments:

 - `-pem` Certificate file path file.pem
 - `-to` Time interval for testing each proxy server.
---

    client = ProxyReceiver(args.certificate, args.time_out)

## Overall arguments

 - `-p` Receives a tuple of desired protocols for proxy server search eg: --protocols 'https', 'socks5'
 - `-l` Limit of tested and valid proxies per protocol.
 - `-url` API URL that will have the list of IP:PORT proxy servers, the {{protocol_value}} parameter is mandatory after the protocol= variable or any protocol type reference variable.
 - `-out` It is the output folder that will have the csv file with the tested proxy list.

## Functions

    content = client.retrieve_free_proxy_list(args.link, protocol)
    

 - Receives the list of API-URL proxy servers with all protocols selected in string.

---

    client.write_valid_list(content, protocol, args.output_folder, args.limit)

 - Test, validate (test_servers(...)) and save the ip:port and protocol in a csv file.
 ---

    test_servers(protocol, row, self.sess, self.certificate, self.old_ip)
     
 - Individual function that tests the connection to the server and validates IP filtering.


## csv structure

|    url          |port                          |protocol                         |
|----------------|-------------------------------|-----------------------------|
|123.456.78.90   |1234                           |socks5                       |
|098.765.43.21   |4321                           |https                        |
.....


## Custom arg classes

    str_bool_switcher_type(arg)

 - It is used by the --certificate(-pem) argument, dynamically switches between string, bool.
 - str: When it is the path to the request certificate folder.
 - bool, True: integrated certificate.
 - bool, False: No check.

Usage example: 

    self.rex  =  self.sess.get('https://....', timeout=10, verify=self.certificate)


---
    tuple_type(arg)

 - It is used by the argument --protocols(-p), receives a list of protocols, eg: --protocols 'http', 'socks4'

Usage example: 

    for protocol in args.protocols:
	        print(f'---\nProtocol selected: {protocol}')
         
    	content = client.retrieve_free_proxy_list(args.link, protocol)
    	client.write_valid_list(content, protocol, args.output_folder, args.limit)

---

    proxies = {'http': f'{protocol}://{url}',
                    'https': f'{protocol}://{url}'}
---

    resp = self.sess.get('https://....', timeout=5, proxies=proxies, verify=self.certificate)
