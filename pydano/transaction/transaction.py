import os
import uuid
from collections import defaultdict
import logging
import json

from pydano.cardano_cli import CardanoCli
from pydano.cardano_temp import tempdir
from pydano.query.protocol_param import ProtocolParam
from pydano.query.utxo import UTXOs


class TransactionConfig:
    """
        This class is responsible to hold input and output utxos
        which is passed around the transaction processing fees.
    """

    def __init__(self, change_address: str):
        self.input_utxos = []
        self.output_txs = defaultdict(list)
        self.mints = []
        self.change_address = change_address


    """
    add_input_utxo: This is a helper function, it queries all the utxos on a address
                and add it to the transaction.
    """
    def add_input_utxos(self, addr: str):
        utxo = UTXOs()
        utxos, totalLovelace = utxo.utxos(addr)
        logging.info(f"Total amount available at addres {addr} is {totalLovelace}")
        logging.debug(f"All UTXOs at addres {utxos}")
        for i in utxos:
            self.add_tx_in(**i)

    """
    add_input_utxo: This will add a new input utxo to the transaction.
    
    This will be added to the traction based on query utxo or input address
    depending on the usecase such as minting etc.

    @params:
        input_utxo: utxo to add as input to the transaction.
    """
    def add_tx_in(self, utxo_hash: str, utxo_index: int):
        self.input_utxos.append({'utxo_hash': utxo_hash, 'utxo_index': utxo_index})
        return len(self.input_utxos)

    """
    add_tx_out: Add new asset to transfer
    @params:
        out_address: Payment address of receiver of the asset.
        asset_name: this can be lovlace/native token or name of the nft.
        asset_quanity: quantity of token/lovelace to transfer. Should be 1 in case of NFTs..
    """
    def add_tx_out(self, out_address: str, asset_name: str, asset_quantity: int):
        out = {'out_address': out_address,
                'name': asset_name,
                'quantity': asset_quantity
                }
        self.output_txs[out_address].append(out)
        return len(self.output_txs)

    def add_mint(self, out_address: str, policyid: str, token_name: str):
        mint_token_name = f"{policyid}.{token_name}"
        out = {"out_address": out_address,
                "name": mint_token_name,
                "quantity": 1
              }
        self.output_txs[out_address].append(out)
        self.mints.append(mint_token_name)

    def input_utxos_args(self):
        command_args = []
        assert len(self.input_utxos) > 0
        for utxo in self.input_utxos:
            command_args.append("--tx-in")
            command_args.append(f"{utxo['utxo_hash']}#{utxo['utxo_index']}")
        return command_args

    def out_tx_args(self):
        command_args = []
        for out_address, out_assets in self.output_txs.items():
            command_args.append("--tx-out")
            assert len(out_assets) > 0
            assert out_assets[0]['name'].lower() == 'lovelace'
            tx_out_config = ""
            tx_out_config += '+' + str(out_assets[0]['quantity'])
            for asset in out_assets[1:]:
                tx_out_config += '+' + str(asset['quantity']) + ' ' + str(asset['name'])
            command_args.append(out_address+tx_out_config)
        return command_args

    def mint_args(self, minting_script_file):
        command_args = []
        for i in self.mints:
            command_args.append(f'--mint=1 {i}')
        command_args.append("--minting-script-file")
        command_args.append(minting_script_file)
        script = json.load(open(minting_script_file, 'r'))
        invalid_hereafter_slot = script['scripts'][0]['slot']
        command_args.append("--invalid-hereafter")
        command_args.append(str(invalid_hereafter_slot))
        return command_args


class Transaction(CardanoCli):

    def __init__(self, transaction_config: TransactionConfig, testnet: bool = True):
        self.transaction_config = transaction_config
        self.transaction_uuid = str(uuid.uuid4())
        super().__init__(testnet)

    """
    prepare_raw_transaction: Prepare raw transaction mostly to calculate block chain fees
        @returns return the file location, which contains draft transaction to calculate fees.
    """
    def prepare_transaction(self) -> str:
        self.prepared_transaction = ""
        pass

    """
    run_transaction: This actually calls the prepare_transaction to prepare command
    and run it using subprocess
    """
    def run_transaction(self):
        self.prepare_transaction()
        logging.debug(f"Running transaction: {' '.join(self.prepared_transaction)}")
        return self.run_command(self.prepared_transaction)

class BuildTransaction(Transaction):

    def __init__(self, transaction_config: TransactionConfig, testnet: bool = True):
        super().__init__(transaction_config, testnet)
        self.protocol_file = ProtocolParam(testnet).protocol_params()

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "build", "--alonzo-era"]

    def build_base_transaction(self):
        command = self.base_command
        command = self.apply_blockchain(command)
        command.extend(self.transaction_config.input_utxos_args())
        command.extend(self.transaction_config.out_tx_args())
        return command

    def build_output_file(self, command, version='draft'):
        command.append("--out-file")
        transaction_file = os.path.join(tempdir.name, f"{self.transaction_uuid}.{version}")
        self.transaction_file = transaction_file
        command.append(transaction_file)
        return command

    def prepare_transaction(self):
        base_transaction = self.build_base_transaction()
        base_transaction.append('--change-address')
        base_transaction.append(self.transaction_config.change_address)
        base_transaction.append("--protocol-params-file")
        base_transaction.append(self.protocol_file)
        complete_trans =  self.build_output_file(base_transaction)
        self.prepared_transaction =  complete_trans

class SignTransaction(Transaction):

    def __init__(self, transaction: Transaction, signing_key: str):
        super().__init__(transaction.testnet)
        self.raw_transaction = transaction.transaction_file
        self.transaction_uuid = transaction.transaction_uuid
        self.signing_key = signing_key

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "sign"]

    def prepare_transaction(self):
        base_transaction = self.base_command
        base_transaction.append("--tx-body-file")
        base_transaction.append(self.raw_transaction)
        base_transaction.append("--signing-key-file")
        base_transaction.append(self.signing_key)
        base_transaction.append("--out-file")
        self.signed_file = os.path.join(tempdir.name, f"{self.transaction_uuid}.signed")
        base_transaction.append(self.signed_file)
        self.prepared_transaction = base_transaction

class SubmitTransaction(Transaction):

    def __init__(self, signed_transaction: SignTransaction):
        super().__init__(signed_transaction.testnet)
        self.raw_transaction = signed_transaction.signed_file
        self.transaction_uuid = signed_transaction.transaction_uuid

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "submit"]

    def prepare_transaction(self):
        base_transaction = self.base_command
        base_transaction = self.apply_blockchain(base_transaction)
        base_transaction.append("--tx-file")
        base_transaction.append(self.raw_transaction)
        self.prepared_transaction = base_transaction
