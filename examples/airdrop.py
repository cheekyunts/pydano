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

from pydano.transaction.transaction_config import TransactionConfig
from pydano.blockfrost.top_holder import TopHolders
from pydano.transaction.transaction import (
    BuildTransaction,
    SignTransaction,
    SubmitTransaction,
)

parser = argparse.ArgumentParser()

# Argument to interact with blockchain and do drop
parser.add_argument(
    "--input_address", help="Address of the input wallet", type=str, default=None
)
parser.add_argument("--signing_key", help="Signing Key", type=str, default=None)
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
parser.add_argument(
    "--node_socket",
    help="Location of node socket to talk to",
    type=str,
    default="/home/gaurav/Documents/crypto/pydano/node.socket",
)
parser.add_argument("--min_utxo", help="Minting script", type=int, default=1324100)
parser.add_argument(
    "--min_change_utxo", help="Minting script", type=int, default=1775768
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
parser.add_argument(
    "--exclude_address", help="Exclude Addresses", type=str, default=None
)

parser.add_argument(
    "--sample_airdrop",
    help="Number of people to sample for airdrop",
    type=int,
    default=1,
)

args = parser.parse_args()

logging.getLogger().setLevel(args.log_level)
if not args.total_pages:
    raise Exception("Give total_pages")

if len(args.policy_id) == 0:
    raise ValueError("Need atleast one policy_id to do the airdrop")

holders = []
for policy_id in args.policy_id:
    top_holders = TopHolders(
        policy_id, args.api_key, args.total_pages, args.use_cache, args.mainnet
    )
    top_holders.gather_assets()
    top_holders.query_assets()
    holders.append(top_holders.get_holders_counter())
if len(args.policy_id) > 1:
    top_holders.c = functools.reduce(lambda a, b: a & b, holders)
holders = top_holders.get_all_holders()

df = pd.DataFrame(holders)
df.to_csv("top_holders.csv")
if args.exclude_address:
    exclude_addresses = json.load(open(args.exclude_address, "r"))
    df = df[~df.stake_address.isin(exclude_addresses)]
raffle_addresses = []
if args.min_holdings:
    df = df[df.holding_count >= args.min_holdings]
for idx, row in df.iterrows():
    count = row["holding_count"] if args.allow_multiple else 1
    addr = row["stake_address"]
    raffle_addresses.extend([addr] * count)
print(
    "Total addresses: {len(raffle_addresses)}, unique addresses: {len(set(raffle_addresses))}"
)
print(f"Doing airdrop from: {len(raffle_addresses)}")
addresses = random.choices(raffle_addresses, k=args.sample_airdrop)
addresses = list(
    map(
        lambda x: {"stake": x, "payment": top_holders.get_payment_address(x)[0]},
        addresses,
    )
)
print(f"Do airdrop to:", addresses)
print("Holders found", len(holders))


##### Going to perform the actual drop
if args.in_address and args.node_socket:
    in_address = args.input_address
    os.environ["CARDANO_NODE_SOCKET_PATH"] = args.node_socket

    tc = TransactionConfig(
        in_address,
        args.min_utxo,
        testnet=not args.mainnet,
        min_change_utxo=args.min_change_utxo,
    )
    tc.add_input_utxos(in_address)
    all_available_tokens = list(tc.available_tokens)

    if len(all_available_tokens) < len(addresses):
        raise ValueError(
            "Not enough tokens in wallet: {args.in_address}, to do the airdrop"
        )

    for idx, address in enumerate(addresses):
        token_name = all_available_tokens[idx]
        address["token"] = token_name
        tc.add_tx_out(address["payment"], token_name, 1)

    bt = BuildTransaction(tc, testnet=not args.mainnet)
    bt.run_transaction()
    print("Signing Transaction")
    st = SignTransaction(bt, args.signing_key)
    st.run_transaction()
    print("Submitting Transaction")
    st = SubmitTransaction(st)
    st.run_transaction()

print("AIRDROP DONE")
print(addresses)
pd.DataFrame(addresses).to_csv("airdrop.csv")
