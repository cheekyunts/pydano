# coding: utf-8
import os
import argparse
from pydano.transaction.transaction import TransactionConfig, BuildTransaction, SignTransaction, SubmitTransaction

# create a keyvalue class
class keyvalue(argparse.Action):
    # Constructor calling
    def __call__( self , parser, namespace,
                 values, option_string = None):
        setattr(namespace, self.dest, dict())

        for value in values:
            # split it into key and value
            key, value = value.split('=')
            # assign into dictionary
            getattr(namespace, self.dest)[key] = value

parser = argparse.ArgumentParser()
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

parser.add_argument("--pay", help="list of addresses and amount of lovelaces to pay",
                    nargs='*', 
                    action = keyvalue)
args = parser.parse_args()

if not args.input_address:
    raise ValueError("Except to have input_address to do transaction")

if not args.signing_key:
    raise ValueError("Except to have signing key for input address")

in_address = args.input_address
os.environ['CARDANO_NODE_SOCKET_PATH'] = args.node_socket 

tc = TransactionConfig(in_address)
tc.add_input_utxos(in_address)
for address, value in args.pay.items():
    try:
        lovalace = int(value)
    except Exception as e:
        raise ValueError(f"Cannot convert {value} to int")
    tc.add_tx_out(address, "lovelace", lovalace)

#tc.add_tx_out("addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp", "lovelace", 1000000)

print("Building Transaction")
cct = BuildTransaction(tc)
cct.run_transaction()
print("Signing Transaction")
st = SignTransaction(cct, args.signing_key)
st.run_transaction()
print("Submitting Transaction")
st = SubmitTransaction(st)
st.run_transaction()
