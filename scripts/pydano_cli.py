# coding: utf-8
import os
import argparse
from pydano.transaction.transaction import TransactionConfig, BuildTransaction, SignTransaction, SubmitTransaction
from pydano.transaction.mint_transaction import MintTransaction
from pydano.query.utxo import UTXOs
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
parser.add_argument("--mainnet",
                     help="Set transaction network to mainnet",
                     action='store_true')
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
                    default=4275768)

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
parser.add_argument("--receive_mint", help="enable receive mint.",
                    action='store_true')
parser.add_argument("--token_cost",
                    help="Cost for minting the token",
                    type=int,
                    default=2000000)
parser.add_argument("--transaction_cost",
                    help="Cost incurred for the network",
                    type=int,
                    default=160000)
parser.add_argument("--receiver_wallet",
                    help="Address of the receiver wallet",
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

tc = TransactionConfig(in_address, args.min_utxo, testnet=not args.mainnet, min_change_utxo=args.min_change_utxo)
if args.pay:
    print("Doing Pay Transaction")
    tc.add_input_utxos(in_address)
    all_payee = json.load(open(args.pay, 'r'))
    for payee in all_payee:
        address = payee['address']
        token_name = payee['token_name']
        quantity = payee['quantity']
        tc.add_tx_out(address, token_name, quantity)
    print("Building Transaction")
    bt = BuildTransaction(tc, testnet=not args.mainnet)
    bt.run_transaction()
elif args.mint:
    print("Doing Mint Transaction")
    tc.add_input_utxos(in_address)
    bt = MintTransaction(tc, minting_script_file=args.minting_script, metadata_json_file=args.metadata_json, testnet=not args.mainnet)
    all_payee = json.load(open(args.mint, 'r'))
    for payee in all_payee:
        address = payee['address']
        token_name = payee['token_name']
        tc.add_mint(address, bt.policyID, token_name)
    bt.transaction_config = tc
    bt.run_transaction()
elif args.receive_mint:
    query_utxo = UTXOs(testnet=not args.mainnet)
    utxos, available_lovelace, available_tokens = query_utxo.utxos(args.input_address)
    for utxo in utxos:
        do_signing = False
        utxo_hash, utxo_index, utxo_amount = utxo['utxo_hash'], utxo['utxo_index'], utxo['utxo_amount']
        # 0.16 This is to cover the transaction fees.
        tc = TransactionConfig(in_address, args.min_utxo, testnet=not args.mainnet, min_change_utxo=args.min_change_utxo)
        tc.add_tx_in(utxo_hash, utxo_index)
        print(utxo_amount, args.token_cost + args.min_utxo + args.transaction_cost)
        if utxo_amount > (args.token_cost + args.min_utxo + args.transaction_cost):
            bt = MintTransaction(tc, minting_script_file=args.minting_script, metadata_json_file=args.metadata_json, testnet=not args.mainnet)
            send_amount = utxo_amount - args.token_cost - args.transaction_cost  - 999978
            address = 'addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp'
            token_name = 'cheekyirvine'
            tc.add_tx_out(address, 'lovelace', send_amount)
            tc.add_tx_out(args.receiver_wallet, 'lovelace', args.token_cost)
            tc.add_mint(address, bt.policyID, token_name)
            bt.transaction_config =  tc
            bt.run_transaction()
            do_signing = True
        elif utxo_amount > args.transaction_cost + 999978:
            address = 'addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp'
            send_amount = utxo_amount - args.transaction_cost - 999978
            tc.add_tx_out(address, 'lovelace', send_amount)
            bt = BuildTransaction(tc, testnet=not args.mainnet)
            bt.run_transaction()
            do_signing = True
        else:
            print(f"Ignoring {utxo_hash}#{utxo_index} with amount {utxo_amount}")
        if do_signing:
            print("Signing Transaction")
            st = SignTransaction(bt, args.signing_key)
            st.run_transaction()
            print("Submitting Transaction")
            st = SubmitTransaction(st)
            st.run_transaction()
    exit(0)
                                

print("Signing Transaction")
st = SignTransaction(bt, args.signing_key)
st.run_transaction()
print("Submitting Transaction")
st = SubmitTransaction(st)
st.run_transaction()
