import requests
from collections import Counter
import argparse
import tqdm
import json
import os
import logging

import pandas as pd

from pydano.blockfrost.top_holder import TopHolders
from pydano.transaction.transaction import TransactionConfig, BuildTransaction, SignTransaction, SubmitTransaction

parser = argparse.ArgumentParser()

# Argument to interact with blockchain and do drop
parser.add_argument("--input_address",
                    help="Address of the input wallet",
                    type=str,
                    default=None)
parser.add_argument("--signing_key",
                    help="Signing Key",
                    type=str,
                    default=None)
parser.add_argument("--node_socket",
                    help="Location of node socket to talk to",
                    type=str,
                    default='/home/gaurav/Documents/crypto/pydano/node.socket')
parser.add_argument("--min_utxo",
                    help="Minting script",
                    type=int,
                    default=1324100)
parser.add_argument("--min_change_utxo",
                    help="Minting script",
                    type=int,
                    default=1775768)
parser.add_argument("--log_level",
                     help="Set log level to",
                     type=str,
                     default="INFO")

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

logging.getLogger().setLevel(args.log_level)
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



##### Going to perform the actual drop
in_address = args.input_address
os.environ['CARDANO_NODE_SOCKET_PATH'] = args.node_socket 

tc = TransactionConfig(in_address, args.min_utxo, testnet=not args.mainnet, min_change_utxo=args.min_change_utxo)
tc.add_input_utxos(in_address)
all_available_tokens = list(tc.available_tokens)

if len(all_available_tokens) < len(addresses):
    raise ValueError("Not enough tokens in wallet: {args.in_address}, to do the airdrop")

for idx, address in enumerate(addresses):
    token_name = all_available_tokens[idx]
    address['token'] = token_name
    tc.add_tx_out(address['payment'], token_name, 1)

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