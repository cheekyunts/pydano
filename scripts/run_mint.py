# coding: utf-8
import os
import argparse
from pydano.transaction.transaction import TransactionConfig, SignTransaction, SubmitTransaction
from pydano.transaction.mint_transaction import MintTransaction
import logging


# create a keyvalue class
class keyvalue(argparse.Action):
    # Constructor calling
    def __call__( self , parser, namespace,
                 values, option_string = None):
        setattr(namespace, self.dest, list())

        print("sdfds", values)
        for value in values:
            # split it into key and value
            key, value = value.split('=')
            # assign into dictionary
            getattr(namespace, self.dest).append((key, value))

parser = argparse.ArgumentParser()
parser.add_argument("--input_address",
                    help="Address of the input wallet",
                    type=str,
                    default=None)
parser.add_argument("--signing_key",
                    help="Signing Key",
                    type=str,
                    default=None)
parser.add_argument("--minting_key",
                    help="Minting Key",
                    type=str,
                    default=None)

parser.add_argument("--minting_lovlace",
                    help="Minting script",
                    type=int,
                    default=1724100)
parser.add_argument("--minting_script",
                    help="Minting script",
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

parser.add_argument("--pay", help="list of addresses and amount of lovelaces to pay",
                    nargs='*', 
                    action = keyvalue)
args = parser.parse_args()

logging.getLogger().setLevel(args.log_level)

if not args.input_address:
    raise ValueError("Except to have input_address to do transaction")

if not args.signing_key:
    raise ValueError("Except to have signing key for input address")

in_address = args.input_address
os.environ['CARDANO_NODE_SOCKET_PATH'] = args.node_socket 

tc = TransactionConfig(in_address)
# This is a hack to get the policyID for now
mt = MintTransaction(tc, minting_script_file=args.minting_script)
tc.add_input_utxos(in_address)
first_transaction = True
print(args.pay)
for address, value in args.pay:
    print(f"Doint {address}:{value}")
    if first_transaction:
        tc.add_tx_out(address, "lovelace", args.minting_lovlace)
        first_transaction = False
    tc.add_mint(address, mt.policyID, value)

#tc.add_tx_out("addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp", "lovelace", 1000000)

print("Building Transaction")
mt = MintTransaction(tc, minting_script_file=args.minting_script)
mt.run_transaction()
print("Signing Transaction")
st = SignTransaction(mt, args.signing_key)
st.run_transaction()
print("Submitting Transaction")
st = SubmitTransaction(st)
st.run_transaction()
