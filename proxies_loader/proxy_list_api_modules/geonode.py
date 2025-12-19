from json import load, loads
from requests import Response


UNNEEDED_KEYS = ('_id', 'anonymityLevel', 'asn', 'region', 'created_at', 'google', 'isp', 'lastChecked')

class GeonodeClasss(object):
    def build_schema_url(self, settings_path:str) -> str:
        with open(settings_path, 'r') as data:
            data = load(data)
            uri:str = data['uri']
            uri = uri if uri.endswith('?') else uri + '?'
            data = data['inputParams']
            
            return uri + f"protocols={'%2C'.join(data['protocols'])}&filterUpTime={data['filterUpTime']}&limit={data['limit']}&page={data['page']}&sort_by={data['sort_by']}&sort_type={data['sort_type']}"
        
        
    @staticmethod
    def build_schema_response(response:Response) -> list[dict]:
        return loads(response.content)['data']


    @staticmethod
    def fix_data(item:dict) -> dict:
        item['protocol'] = item.pop('protocols')[0]
        return item
            
            
    def confirm(self, item:dict) -> None:
        for key in UNNEEDED_KEYS:
            del item[key]