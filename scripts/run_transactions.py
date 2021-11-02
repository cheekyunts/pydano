# coding: utf-8
import os
import argparse
from pydano.transaction.transaction import TransactionConfig, BuildTransaction, SignTransaction, SubmitTransaction
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

parser.add_argument("--pay", help="A json file with list of all payments to be made.",
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

tc = TransactionConfig(in_address)
tc.add_input_utxos(in_address)
all_payee = json.load(open(args.pay, 'r'))
for payee in all_payee:
    address = payee['address']
    token_name = payee['token_name']
    quantity = payee['quantity']
    tc.add_tx_out(address, token_name, quantity)

print("Building Transaction")
cct = BuildTransaction(tc)
cct.run_transaction()
print("Signing Transaction")
st = SignTransaction(cct, args.signing_key)
st.run_transaction()
print("Submitting Transaction")
st = SubmitTransaction(st)
st.run_transaction()
