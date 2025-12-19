# Proxy Scrape
**Project to receive, test, validate and store a list of free proxies.**

## Installation
    pip install -r ./requirements.txt

## Requirements
 - argparse
 - urllib3
 - requests[socks]

## Usage 
On `proxy_validator.py` Switch between providers available in `\ip_checker_provider_modules`. Those responsible for testing the proxy and the new masked IP address. The script for each schema always returns in string format, compatible with the program.

    from ip_checker_provider_modules.ipify import get_public_ip

----

On `\proxy_list_api_modules` you can add or edit the scripts for the Free Proxy List provider schemas. The configuration for each corresponding provider module is in the `schemas\proxy_providers_config` folder. All must return a list of dictionaries in the same format compatible with the rest of the program. Eg:.

    {
        "data": [
            {
                "_id": "xxxx",
                "ip": "xxx.xxx.xxx.xxx",
                "city": "Busan",
                "country": "KR",
                "lastChecked": 1766169816,
                "latency": 219.011,
                "port": "9400",
                "protocols": [
                    "socks4"
                ]
            },
            {
                "_id": "xxxx",
                "ip": "xxx.xxx.xxx.xxx",
                "city": "Khon Kaen",
                "country": "TH",
                "lastChecked": 1766169816,
                "latency": 236.013,
                "port": "8080",
                "protocols": [
                    "socks4"
                ]
            },
            ...
        ]
    }

The Instance initially receives the arguments:

 - `-c` Certificate file path `certificate.pem`. This can also be set to 'True' or 'False' to use a generic certificate or disable it.
 - `-t` Time interval for testing each proxy server.

## Overall Arguments
 - `-a` Name of the API provider from the list of free proxies. This should be an available option in `\proxy_list_api_modules`
 - `-l` Limit of tested and valid proxies per protocol.
 - `-o` It is the output folder that will have the json file with the tested proxy list.

## Some Functions

    retrieve_free_proxy_list(args.link, protocol)
    
 - Receives the list of API-URL proxy servers with all protocols selected in a json.

---
    write_valid_list(content, protocol, args.output_folder, args.limit)

 - Test, validate (test_servers(...)) and save the ip:port and protocol in a json file.
 ---

    test_servers(protocol, row, self.sess, self.certificate, self.old_ip)
     
 - Individual function that tests the connection to the server and validates IP filtering.

## Json Structure

    {
        "protocolsCount": {
            "socks5": 1,
            "socks4": 1
        },
        "proxies": [
            {
                "ip": "xxx.xxx.xxx.xxx",
                "port": "20000",
                "country": "RU",
                "latency": 44.981,
                "protocol": "socks5"
            },
            {
                "ip": "xxx.xxx.xxx.xxx",
                "port": "60111",
                "country": "FR",
                "latency": 9.506,
                "protocol": "socks4"
            }
        ]
    }


## Custom arg Classes

    str_bool_switcher_type(arg)

 - It is used by the --certificate(-c) argument, dynamically switches between string, bool.
 - str: When it is the path to the request certificate folder.
 - bool, True: integrated certificate.
 - bool, False: No check.