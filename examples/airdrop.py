import requests
from collections import Counter
import argparse
import tqdm
import json
import os

import pandas as pd
from pydano.blockfrost.top_holder import TopHolders

parser = argparse.ArgumentParser()
parser.add_argument("--policy_id", help="Policy Id to get top holders for",
                    type=str, default=None)
parser.add_argument("--api_key", help="Blockfrost API Key",
                    type=str)
parser.add_argument("--total_pages", help="Total Pages to request",
                    type=int)
parser.add_argument("--use_cache", help="Use cache instead of running",
                    action='store_true')
parser.add_argument("--mainnet", help="Use Mainnet",
                    action='store_true')
parser.add_argument("--exclude_address", help="Exclude Addresses",
                    type=str, default='exclude_address.json')
parser.add_argument("--sample_airdrop", help='Number of people to sample for airdrop',
                    type=int, default=1)
args = parser.parse_args()

if not args.total_pages:
    raise Exception("Give total_pages")


top_holders = TopHolders(args.policy_id, args.api_key, args.total_pages, args.use_cache, args.mainnet)
top_holders.gather_assets()
top_holders.query_assets()
holders = top_holders.get_all_holders()

df = pd.DataFrame(holders)
df.to_csv('top_holders.csv')
if args.exclude_address:
    exclude_addresses = json.load(open(args.exclude_address, 'r'))
    df = df[~df.stake_address.isin(exclude_addresses)]
    df = df[df.holding_count >= 4]
    print(df)
    print(f"Doing airdrop from: {len(df)}")
    df = df.sample(args.sample_airdrop)
    addresses = df.stake_address.to_list()
    addresses = list(map(lambda x: {'stake': x, 'payment': top_holders.get_payment_address(x)[0]}, addresses))
    print(f"Do airdrop to:", addresses)
print("Holders found", len(holders))
