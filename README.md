# Proxy Scrape
Projeto para receber, validar e armazenar uma lista de proxies gratuitos.

# Instação
 - `pip install -r .../Requirements.txt`

# Requisitos
 - argparse
 - urllib3 
 - requests
 - jinja2 
 - requests[socks]
 - --
 - proxies_validator.py
 - custom_arg_types.py

## Utilização 
Esta linhas iniciais são necessárias em proxy_scrape.py para a funcionalidade básica.

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
A Instância recebe inicialmente os argumentos: 

 - `-pem` Caminho do arquivo certificado arquivo.pem
 - `-to` Intervalo de tempo para teste de cada servidor proxy.
---

    client = ProxyReceiver(args.certificate, args.time_out)

## Argumentos gerais

 - `-p` Recebe uma tupla de protocolos desejados para busca de servidores proxy ex: --protocols 'https', 'socks5'
 - `-l` Limite de proxies testados e válidos por protocolo.
 - `-url` URL da API que terá a lista de servidores proxy IP:PORTA, o parâmetro {{protocol_value}} é obrigatório após a variável protocol= ou qualquer variável de referência a tipo de protocolo.
 - `-out` É a pasta de saída que terá o arquivo csv com a lista proxy testados.

## Funções

    content = client.retrieve_free_proxy_list(args.link, protocol)
    

 - Recebe a lista de servidores proxy da API-URL com todos os protocolos selecionados em string.

---

    client.write_valid_list(content, protocol, args.output_folder, args.limit)

 - Testa, valida(test_servers(...)) e salva o ip:porta e protocolo em um arquivo csv.
 ---

    test_servers(protocol, row, self.sess, self.certificate, self.old_ip)
     
 - Função individual que testa a conexão com o servidor e valida a filtragem do IP.


## Estrutura do csv

|    url          |port                          |protocol                         |
|----------------|-------------------------------|-----------------------------|
|123.456.78.90   |1234                           |socks5                       |
|098.765.43.21   |4321                           |https                        |
.....


## Classes de args customizados

    str_bool_switcher_type(arg)

 - É usado pelo argumento --certificate(-pem), alterna dinamicamente entre string, bool.
 - str: Quando for o caminho da pasta do certificado da requisição.
 - bool, True: certificado integrado.
 - bool, False: Sem verificação.

Exemplo de uso: 

    self.rex  =  self.sess.get('https://....', timeout=10, verify=self.certificate)


---
    tuple_type(arg)

 - É usado pelo argumento --protocols(-p), recebe uma lista de protocólos, ex: --protocols 'http', 'socks4'

Exemplo de uso: 

    for protocol in args.protocols:
	        print(f'---\nProtocol selected: {protocol}')
         
    	content = client.retrieve_free_proxy_list(args.link, protocol)
    	client.write_valid_list(content, protocol, args.output_folder, args.limit)

---

    proxies = {'http': f'{protocol}://{url}',
                    'https': f'{protocol}://{url}'}
---

    resp = self.sess.get('https://....', timeout=5, proxies=proxies, verify=self.certificate)

### Support
**BTC**: `bc1qa0xzyhcmcsuvppttmylzygwwfaken5jturhgek`
**ETH**: `0x2fA70716D1Ae2f4994Be8e249b609056D72Ce80a`
