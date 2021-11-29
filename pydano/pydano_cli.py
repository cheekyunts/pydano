# coding: utf-8
import os
import argparse
import logging
import json

from blockfrost import BlockFrostApi, ApiError, ApiUrls

from pydano.transaction.transaction_config import TransactionConfig
from pydano.transaction.transaction import (
    BuildTransaction,
    SignTransaction,
    SubmitTransaction,
    BuildRawTransaction,
    MintRawTransaction,
)
from pydano.transaction.policy_transaction import PolicyIDTransaction
from pydano.query.utxo import UTXOs
from pydano.addresses.generate_address import Address
from pydano.scripts.minting_script import MintingScript


def do_receive_mint(args, blockfrost_api):
    query_utxo = UTXOs(testnet=not args.mainnet)
    utxos, _, _ = query_utxo.utxos(args.input_address)
    for utxo in utxos:
        try:
            utxo_hash, utxo_index, utxo_amount = (
                utxo["utxo_hash"],
                utxo["utxo_index"],
                utxo["utxo_amount"],
            )
            # 0.16 This is to cover the transaction fees.
            tc = MintingConfig(
                args.minting_script_file,
                args.input_address,
                args.min_utxo,
                testnet=not args.mainnet,
                metadata_json=args.metadata_json_file,
                min_change_utxo=args.min_change_utxo,
            )
            tc.add_tx_in(utxo_hash, utxo_index)
            if utxo_amount > (args.token_cost + args.min_utxo):
                send_amount = utxo_amount - args.token_cost
                address = blockfrost_api.transaction_utxos(utxo_hash).inputs[0].address
                token_name = args.token_name
                tc.add_tx_out(address, "lovelace", send_amount)
                tc.add_tx_out(
                    args.receiver_wallet, "lovelace", args.token_cost, fee_payer=True
                )
                tc.add_mint(address, token_name)
                bt = MintRawTransaction(tc, testnet=not args.mainnet)
                bt.run_raw_transaction()
                bt.submit(args.signing_key)
            elif utxo_amount > args.transaction_cost + 999978:
                address = blockfrost_api.transaction_utxos(utxo_hash).inputs[0].address
                send_amount = utxo_amount
                tc.add_tx_out(address, "lovelace", send_amount, fee_payer=True)
                bt = BuildRawTransaction(tc, testnet=not args.mainnet)
                bt.run_raw_transaction()
                bt.submit(args.signing_key)
            else:
                print(f"Ignoring {utxo_hash}#{utxo_index} with amount {utxo_amount}")
        except Exception as e:
            print(e)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_address", help="Address of the input wallet", type=str, default=None
    )
    parser.add_argument("--signing_key", help="Signing Key", type=str, default=None)
    parser.add_argument(
        "--log_level", help="Set log level to", type=str, default="INFO"
    )
    parser.add_argument(
        "--mainnet", help="Set transaction network to mainnet", action="store_true"
    )
    parser.add_argument(
        "--node_socket",
        help="Location of node socket to talk to",
        type=str,
        default="/home/gaurav/Documents/crypto/pydano/node.socket",
    )
    parser.add_argument("--min_utxo", help="Minting script", type=int, default=1324100)
    parser.add_argument(
        "--min_change_utxo", help="Minting script", type=int, default=4275768
    )

    parser.add_argument(
        "--minting_script", help="Minting script", type=str, default=None
    )
    parser.add_argument(
        "--metadata_json", help="Metadata Json file", type=str, default=None
    )
    parser.add_argument(
        "--pay",
        help="A json file with list of all payments to be made.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--mint",
        help="A json file with list tokens to mint and address to send them to.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--receive_mint", help="enable receive mint.", action="store_true"
    )
    parser.add_argument(
        "--token_cost", help="Cost for minting the token", type=int, default=2000000
    )
    parser.add_argument(
        "--transaction_cost",
        help="Cost incurred for the network",
        type=int,
        default=160000,
    )
    parser.add_argument(
        "--receiver_wallet",
        help="Address of the receiver wallet",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--token_name", help="Token name for receiver mint", type=str, default=None
    )

    parser.add_argument(
        "--blockfrost_key", help="Api key of blockfrost", type=str, default=None
    )

    parser.add_argument(
        "--generate_address", help="Generate Address files", action="store_true"
    )

    parser.add_argument(
        "--dirname", help="Directory to store the keys in", default=None
    )

    parser.add_argument("--key_name", help="Key name", default=None)

    parser.add_argument(
        "--generate_script", help="Generate minting script.", action="store_true"
    )

    parser.add_argument("--locking_slot", help="Locking slot of the script.", type=int)

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    logging.getLogger().setLevel(args.log_level)

    is_testnet = not args.mainnet
    blockfrost_base_url = ApiUrls.mainnet.value
    if is_testnet:
        blockfrost_base_url = ApiUrls.testnet.value

    blockfrost_api = None
    if args.receive_mint and not args.blockfrost_key:
        raise ValueError("Need blockfrost_key to do receive_mint")
    if args.receive_mint:
        blockfrost_api = BlockFrostApi(
            project_id=args.blockfrost_key, base_url=blockfrost_base_url
        )

    address_generated = False
    if args.generate_address:

        if not args.dirname:
            raise ValueError("Expected dirname argument for generating the address")
        addr = Address(args.dirname, args.key_name, not args.mainnet)
        addr.create_address()
        print("Finished generating the address, exiting")
        address_generated = True
        if not args.generate_script:
            return

    if args.generate_script:

        if not address_generated:
            if not args.dirname or not args.key_name:
                raise FileNotFoundError(
                    "Unable to find the keyname and dirname to generate script"
                )
            addr = Address(args.dirname, args.key_name, not args.mainnet)
            addr.load()
        minting_script = MintingScript(
            addr, args.locking_slot, file_name=args.minting_script
        )
        print(f"Minting script file is {minting_script.policy_script_file}")
        return

    if not args.input_address:
        raise ValueError("Except to have input_address to do transaction")

    if not args.signing_key:
        raise ValueError("Except to have signing key for input address")

    in_address = args.input_address
    os.environ["CARDANO_NODE_SOCKET_PATH"] = args.node_socket

    if args.pay:
        print("Doing Pay Transaction")
        tc = TransactionConfig(
            in_address,
            args.min_utxo,
            testnet=not args.mainnet,
            min_change_utxo=args.min_change_utxo,
        )
        tc.add_input_utxos(in_address)
        all_payee = json.load(open(args.pay, "r"))
        for payee in all_payee:
            address = payee["address"]
            token_name = payee["token_name"]
            quantity = payee["quantity"]
            tc.add_tx_out(address, token_name, quantity)
        print("Building Transaction")
        bt = BuildRawTransaction(tc, testnet=not args.mainnet)
        bt.run_raw_transaction()
        bt.submit(args.signing_key)
    elif args.mint:
        print("Doing Mint Transaction")
        mc = MintingConfig(
            args.minting_script,
            in_address,
            args.min_utxo,
            testnet=not args.mainnet,
            metadata_json_file=args.metadata_json,
            min_change_utxo=args.min_change_utxo,
        )
        mc.add_input_utxos(in_address)
        all_payee = json.load(open(args.mint, "r"))
        for payee in all_payee:
            address = payee["address"]
            token_name = payee["token_name"]
            mc.add_mint(address, token_name)
        bt = MintRawTransaction(mc, testnet=not args.mainnet)
        bt.run_raw_transaction()
        bt.submit(args.signing_key)
    elif args.receive_mint:
        while True:
            try:
                do_receive_mint(args, blockfrost_api)
            except Exception as e:
                print(e)
                pass
        exit(0)


if __name__ == "__main__":
    main()
