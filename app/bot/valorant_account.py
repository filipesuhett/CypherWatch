import json
import requests
import os

class ValorantAccount:
    def __init__(self, account_name, puuid=None, region=None):
        self.account_name = account_name
        if puuid is None or region is None:
            self.puuid, self.region = self.get_user(account_name)
        else:
            self.puuid = puuid
            self.region = region

    def to_dict(self):
        return {
            'account_name': self.account_name,
            'puuid': self.puuid,
            'region': self.region
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            account_name=data['account_name'],
            puuid=data.get('puuid'),
            region=data.get('region')
        )
        
    def get_user(self, account_name):
        nickname, tag = account_name.split('#')
        print(f'Nickname: {nickname}, Tag: {tag}')
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
