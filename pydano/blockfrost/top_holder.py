import logging
import os
import requests
import json
import tqdm
from collections import defaultdict, Counter

class TopHolders:
    assets_url = {
                    'mainnet': "https://cardano-mainnet.blockfrost.io/api/v0/assets/{asset_id}/addresses"
                 }
    list_assts_url = {
                        'mainnet': "https://cardano-mainnet.blockfrost.io/api/v0/assets/policy/{policy_id}" 
                     }
    stake_address_req = {
                            'mainnet': "https://cardano-mainnet.blockfrost.io/api/v0/addresses/{address}" 
                        }

    def __init__(self, policy_id: str,
                       api_key: str,
                       total_pages: int,
                       use_cache: bool,
                       mainnet: bool):
        self.policy_id = policy_id
        self.api_key = api_key
        self.total_pages = total_pages
        self.use_cache = use_cache
        self.mainnet = mainnet
        self.url_identifier = 'mainnet' if self.mainnet else 'testnet'
        self.project_headers = {'project_id': self.api_key}
        self.all_assets = []
        self.c = Counter()
        self.stake_to_payment_address = defaultdict(list)

    def get_asset(self, asset_id):
        if self.use_cache and os.path.isfile(f'cache/{asset_id}.json'):
            address = json.load(open(f'cache/{asset_id}.json', 'r'))
            return address
        asset_holder_url = self.assets_url[self.url_identifier].format(asset_id=asset_id)
        res = requests.get(asset_holder_url, headers=self.project_headers)
        if res.status_code == 200:
            address = res.json()
            json.dump(address, open(f'cache/{asset_id}.json', 'w'))
            return address
        print(f"asset Request Failed {asset_id}")
        return None

    def get_stake_address(self, holder):
        if self.use_cache and os.path.isfile(f'cache/stake_address_{holder}.json'):
            holder = json.load(open(f'cache/stake_address_{holder}.json', 'r'))
            return holder
        res = requests.get(self.stake_address_req[self.url_identifier].format(address=holder), headers=self.project_headers)
        if res.status_code == 200:
            data = res.json()
            json.dump(data, open(f'cache/stake_address_{holder}.json', 'w'))
            return data
        print(f"stake address Request Failed {holder} {res}")
        return None


    def gather_assets(self):
        for page in range(1,  self.total_pages+1):
            logging.info(f"Requesting Page {page}")
            res = requests.get(self.list_assts_url[self.url_identifier].format(policy_id=self.policy_id), headers=self.project_headers, params={'page': page})
            assets = res.json()
            self.all_assets.extend(assets)

    def query_assets(self):
        print("Total Assets: ", len(self.all_assets))
        for asset in tqdm.tqdm(self.all_assets):
            asset_id = asset['asset']
            address = self.get_asset(asset_id)
            if len(address) > 0 and type(address) == list:
                holder = address[0]['address']
                data = self.get_stake_address(holder)
                if data:
                    unt_holder = data['stake_address']
                    self.c[unt_holder] += 1
                    self.stake_to_payment_address[str(unt_holder)].append(holder)
                else:
                    print(f"Cannot find the address: {holder}")

            else:
                print("No address returned", asset, address)

    def get_all_holders(self):
        holders = []
        for value, count in self.c.most_common():
            #print(value, count)
            holders.append({'stake_address': value, 'holding_count': count})
        return holders

    def get_payment_address(self, stake_address):
        if stake_address in self.stake_to_payment_address:
            return self.stake_to_payment_address[stake_address]
        raise ValueError("Stake address not found in cache")
