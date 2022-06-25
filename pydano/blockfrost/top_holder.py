import logging
import os
import requests
import json
import tqdm
from collections import defaultdict, Counter
from datetime import datetime
from pycardano import Address, Network
from pycardano.exception import InvalidAddressInputException
def get_stake_address(address):
    try:
        addr = Address.from_primitive(address.strip())
        addr2 = Address(staking_part=addr.staking_part, network=Network.MAINNET)
        return {"stake_address": str(addr2)}
    except InvalidAddressInputException:
        # Return address if stake address can't be found
        return {"stake_address": address}
    except TypeError:
        return {"stake_address": address}

class TopHolders:
    asset_address_url = {
        "mainnet": "https://cardano-mainnet.blockfrost.io/api/v0/assets/{asset_id}/addresses"
    }
    asset_url = {
        "mainnet": "https://cardano-mainnet.blockfrost.io/api/v0/assets/{asset_id}/"
    }
    list_assts_url = {
        "mainnet": "https://cardano-mainnet.blockfrost.io/api/v0/assets/policy/{policy_id}"
    }
    stake_address_req = {
        "mainnet": "https://cardano-mainnet.blockfrost.io/api/v0/addresses/{address}"
    }

    def __init__(
        self,
        policy_id: str,
        api_key: str,
        total_pages: int,
        use_cache: bool,
        mainnet: bool,
    ):
        self.policy_id = policy_id
        self.api_key = api_key
        self.total_pages = total_pages
        self.use_cache = use_cache
        self.mainnet = mainnet
        self.url_identifier = "mainnet" if self.mainnet else "testnet"
        self.project_headers = {"project_id": self.api_key}
        self.all_assets = []
        self.c = Counter()
        self.stake_to_payment_address = defaultdict(list)
        self.assets_held = defaultdict(list)

    def get_holders_counter(self):
        return self.c

    def get_asset(self, asset_id):
        if self.use_cache and os.path.isfile(f"cache/main_{asset_id}.json"):
            address = json.load(open(f"cache/main_{asset_id}.json", "r"))
            return address
        asset_holder_url = self.asset_url[self.url_identifier].format(asset_id=asset_id)
        res = requests.get(asset_holder_url, headers=self.project_headers)
        if res.status_code == 200:
            asset = res.json()
            json.dump(asset, open(f"cache/main_{asset_id}.json", "w"))
            return asset
        print(f"asset Request Failed {asset_id} {res}")
        return None

    def get_asset_addresses(self, asset_id):
        if self.use_cache and os.path.isfile(f"cache/{asset_id}.json"):
            address = json.load(open(f"cache/{asset_id}.json", "r"))
            return address
        asset_holder_url = self.asset_address_url[self.url_identifier].format(
            asset_id=asset_id
        )
        addresses = []
        for page in tqdm.tqdm(range(1, 100)):
            res = requests.get(
                asset_holder_url, headers=self.project_headers, params={"page": page}
            )
            if res.status_code == 200:
                address = res.json()
                if len(address) == 0:
                    json.dump(addresses, open(f"cache/{asset_id}.json", "w"))
                    return addresses
                addresses.extend(address)
        print(f"asset Request Failed {asset_id}")
        return None

    def get_stake_address(self, holder):
        if self.use_cache and os.path.isfile(f"cache/stake_address_{holder}.json"):
            holder = json.load(open(f"cache/stake_address_{holder}.json", "r"))
            return holder
        res = requests.get(
            self.stake_address_req[self.url_identifier].format(address=holder),
            headers=self.project_headers,
        )
        if res.status_code == 200:
            data = res.json()
            json.dump(data, open(f"cache/stake_address_{holder}.json", "w"))
            return data
        print(f"stake address Request Failed {holder} {res}")
        return None

    def gather_assets(self):
        for page in range(1, self.total_pages + 1):
            logging.info(f"Requesting Page {page}")
            if self.use_cache and os.path.isfile(f"cache/page_{self.policy_id}_{page}.json"):
                assets = json.load(open(f"cache/page_{self.policy_id}_{page}.json", "r"))
                self.all_assets.extend(assets)
                continue
            res = requests.get(
                self.list_assts_url[self.url_identifier].format(
                    policy_id=self.policy_id
                ),
                headers=self.project_headers,
                params={"page": page},
            )
            if res.status_code == 200:
                assets = res.json()
                json.dump(assets, open(f"cache/page_{self.policy_id}_{page}.json", "w"))
                if len(assets) == 0:
                    return
                self.all_assets.extend(assets)
            else:
                raise Exception(f"Unable to get assets : {str(res)}")

    def query_assets(self, eligible=None):
        print("Total Assets: ", len(self.all_assets))
        for asset in tqdm.tqdm(self.all_assets):
            asset_id = asset["asset"]
            quantity = asset["quantity"]
            if quantity == 0:
                continue
            if eligible != None and not eligible(self.get_asset(asset_id)):
                continue
            tic = datetime.now()
            addresses = self.get_asset_addresses(asset_id)
            tac = datetime.now()
            print(tac-tic, "address", asset_id)
            if len(addresses) > 0 and type(addresses) == list:
                for address in tqdm.tqdm(addresses):
                    holder = address["address"]
                    holding_quantity = int(address["quantity"])
                    data = get_stake_address(holder)
                    if data:
                        unt_holder = data["stake_address"]
                        if not unt_holder:
                            unt_holder = holder
                        self.c[unt_holder] += holding_quantity
                        self.stake_to_payment_address[str(unt_holder)].append(holder)
                        self.assets_held[str(unt_holder)].append(asset_id)
                    else:
                        print(f"Cannot find the address: {holder}")

            else:
                print("No address returned", asset, addresses)

    def get_assets_metadata(self):
        all_assets = []
        for asset in tqdm.tqdm(self.all_assets):
            asset_id = asset["asset"]
            all_assets.append(self.get_asset(asset_id))
        return all_assets

    def get_all_holders(self):
        holders = []
        for value, count in self.c.most_common():
            holders.append(
                {
                    "stake_address": value,
                    "holding_count": count,
                    "assets_held": self.assets_held[value],
                }
            )
        return holders

    def get_payment_address(self, stake_address):
        if stake_address in self.stake_to_payment_address:
            return self.stake_to_payment_address[stake_address]
        raise ValueError(f"Stake address not found in cache: {stake_address}")
