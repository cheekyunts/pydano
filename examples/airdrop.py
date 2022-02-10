import requests
from collections import Counter
import argparse
import tqdm
import json
import os
import logging
import random
import functools

import pandas as pd

from pydano.blockfrost.top_holder import TopHolders

parser = argparse.ArgumentParser()

parser.add_argument(
    "--allow_multiple",
    help="Allow multiple entry from a single person",
    action="store_true",
)
parser.add_argument(
    "--min_holdings",
    help="Minimum holding to be eligible for airdrop",
    type=int,
    default=1,
)
parser.add_argument("--log_level", help="Set log level to", type=str, default="INFO")

parser.add_argument(
    "--policy_id",
    help="Policy Id to get top holders for",
    type=str,
    nargs="+",
    default=None,
)
parser.add_argument("--api_key", help="Blockfrost API Key", type=str)
parser.add_argument(
    "--total_pages", help="Total Pages to request", type=int, default=1000
)
parser.add_argument(
    "--use_cache", help="Use cache instead of running", action="store_true"
)
parser.add_argument("--mainnet", help="Use Mainnet", action="store_true")
parser.add_argument("--only_naked", help="Use Mainnet", action="store_true")
parser.add_argument(
    "--exclude_address", help="Exclude Addresses", type=str, default=None
)

parser.add_argument(
    "--sample_airdrop",
    help="Number of people to sample for airdrop",
    type=int,
    default=1,
)

parser.add_argument(
    "--token_name",
    help="Used to add token in airdrop transaction file",
    type=str,
    default=None,
)

parser.add_argument(
    "--store_metadata",
    help="Stores 1 policy-id's metadata to this file (overwrites the file), (only gives metadata for last policy",
    type=str,
    default=None,
)
args = parser.parse_args()

logging.getLogger().setLevel(args.log_level)

holders_file_suffix = ""
if not args.total_pages:
    raise Exception("Give total_pages")

if len(args.policy_id) == 0:
    raise ValueError("Need atleast one policy_id to do the airdrop")

holders = []


def naked_unts(asset_obj):
    if not asset_obj:
        return False
    if "onchain_metadata" not in asset_obj:
        return False
    metadata = asset_obj["onchain_metadata"]
    # Not a valid metadata
    if not metadata or "unt" not in metadata:
        return False
    forbidden_for_naked = [
        "face",
        "eyes",
        "hat",
        "accessory",
        "righty",
        "lefty",
        "mouth",
    ]
    return not any([i in metadata for i in forbidden_for_naked])


for policy_id in args.policy_id:
    top_holders = TopHolders(
        policy_id, args.api_key, args.total_pages, args.use_cache, args.mainnet
    )
    top_holders.gather_assets()
    holders_file_suffix += "_" + policy_id + "_"
    if args.only_naked:
        top_holders.query_assets(naked_unts)
    else:
        top_holders.query_assets()
    holders.append(top_holders.get_holders_counter())
if len(args.policy_id) > 1:
    top_holders.c = functools.reduce(lambda a, b: a & b, holders)
holders = top_holders.get_all_holders()

if args.store_metadata:
    all_metadata = top_holders.get_assets_metadata()
    json.dump(all_metadata, open(args.store_metadata, "w"), indent=4)

if args.only_naked:
    holders_file_suffix += "_" + "only_naked" + "_"
    for holder in holders:
        held_unts = []
        print(holder)
        for asset_id in holder["assets_held"]:
            asset = top_holders.get_asset(asset_id)
            unt = asset["onchain_metadata"]["unt"]
            name = asset["onchain_metadata"]["name"]
            held_unts.append({"unt": unt, "name": name})
        holder["held_unts"] = held_unts
        holder["address"] = top_holders.get_payment_address(holder["stake_address"])[0]

df = pd.DataFrame(holders)
df.to_csv(f"top_holders_{holders_file_suffix}.csv")
df.to_pickle("top_holders_{holders_file_suffix}.pkl")
if args.exclude_address:
    exclude_addresses = json.load(open(args.exclude_address, "r"))
    df = df[~df.stake_address.isin(exclude_addresses)]
raffle_addresses = []
if args.min_holdings:
    df = df[df.holding_count >= args.min_holdings]
for idx, row in df.iterrows():
    count = row["holding_count"] if args.allow_multiple else 1
    addr = row["stake_address"]
    if not addr:
        continue
    raffle_addresses.extend([addr] * count)
print(
    f"Total addresses: {len(raffle_addresses)}, unique addresses: {len(set(raffle_addresses))}"
)
print(f"Doing airdrop from: {len(raffle_addresses)}")
addresses = random.sample(raffle_addresses, args.sample_airdrop)
addresses = list(
    map(
        lambda x: {"stake": x, "address": top_holders.get_payment_address(x)[0]},
        addresses,
    )
)
if args.token_name:
    for i in addresses:
        i["token_name"] = args.token_name

json.dump(addresses, open("airdrop_pydano_transaction.json", "w"), indent=4)

print(f"Do airdrop to:", addresses)
print("Holders found", len(holders))
