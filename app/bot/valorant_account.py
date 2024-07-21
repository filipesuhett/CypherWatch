import json
import os
import requests

class ValorantAccount:
    def __init__(self, account_name, puuid=None, region=None, has_notificated=False, to_mark=False):
        self.account_name = account_name
        self.has_notificated = has_notificated
        self.to_mark = to_mark
        if puuid is None or region is None:
            self.puuid, self.region = self.get_user(account_name)
        else:
            self.puuid = puuid
            self.region = region

    def to_dict(self):
        return {
            'account_name': self.account_name,
            'puuid': self.puuid,
            'region': self.region,
            'has_notificated': self.has_notificated,
            'to_mark': self.to_mark
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            account_name=data['account_name'],
            puuid=data.get('puuid'),
            region=data.get('region'),
            has_notificated=data.get('has_notificated', False),  # Default to False if not present
            to_mark=data.get('to_mark', False)  # Default to False if not present
        )
        
    def get_user(self, account_name):
        nickname, tag = account_name.split('#')
        url = f'https://api.henrikdev.xyz/valorant/v1/account/{nickname}/{tag}'
        api_key = os.getenv('API_KEY')
        
        # Parâmetros da requisição
        params = {'api_key': api_key}

        # Fazendo a requisição GET
        response = requests.get(url, params=params)

        if response.status_code == 200:
            # Obtém o conteúdo da resposta em JSON
            data = response.json()

            # Extraindo puuid e region
            puuid = data['data']['puuid']
            region = data['data']['region']

            return puuid, region
        else:
            print(f'Error: {response}')
            return None, None
