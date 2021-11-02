# coding: utf-8
import os
import argparse
from pydano.transaction.transaction import TransactionConfig, BuildTransaction, SignTransaction, SubmitTransaction
from pydano.transaction.mint_transaction import MintTransaction
import logging
import json

parser = argparse.ArgumentParser()
parser.add_argument("--input_address",
                    help="Address of the input wallet",
                    type=str,
                    default=None)
parser.add_argument("--signing_key",
                    help="Signing Key",
                    type=str,
                    default=None)
parser.add_argument("--log_level",
                     help="Set log level to",
                     type=str,
                     default="INFO")
parser.add_argument("--node_socket",
                    help="Location of node socket to talk to",
                    type=str,
                    default='/home/gaurav/Documents/crypto/pydano/node.socket')
parser.add_argument("--min_utxo",
                    help="Minting script",
                    type=int,
                    default=1724100)
parser.add_argument("--minting_script",
                    help="Minting script",
                    type=str,
                    default=None)
parser.add_argument("--metadata_json",
                    help="Metadata Json file",
                    type=str,
                    default=None)
parser.add_argument("--pay", help="A json file with list of all payments to be made.",
                    type=str,
                    default=None)
parser.add_argument("--mint", help="A json file with list tokens to mint and address to send them to.",
                    type=str,
                    default=None)
args = parser.parse_args()

logging.getLogger().setLevel(args.log_level)

if not args.input_address:
    raise ValueError("Except to have input_address to do transaction")

if not args.signing_key:
    raise ValueError("Except to have signing key for input address")

in_address = args.input_address
os.environ['CARDANO_NODE_SOCKET_PATH'] = args.node_socket 

tc = TransactionConfig(in_address, args.min_utxo)
tc.add_input_utxos(in_address)
if args.pay:
    print("Doing Pay Transaction")
    all_payee = json.load(open(args.pay, 'r'))
    for payee in all_payee:
        address = payee['address']
        token_name = payee['token_name']
        quantity = payee['quantity']
        tc.add_tx_out(address, token_name, quantity)
    print("Building Transaction")
    bt = BuildTransaction(tc)
    bt.run_transaction()
elif args.mint:
    print("Doing Mint Transaction")
    bt = MintTransaction(tc, minting_script_file=args.minting_script, metadata_json_file=args.metadata_json)
    all_payee = json.load(open(args.mint, 'r'))
    for payee in all_payee:
        address = payee['address']
        token_name = payee['token_name']
        tc.add_mint(address, bt.policyID, token_name)
    bt.transaction_config = tc
    bt.run_transaction()

print("Signing Transaction")
st = SignTransaction(bt, args.signing_key)
st.run_transaction()
print("Submitting Transaction")
st = SubmitTransaction(st)
st.run_transaction()
