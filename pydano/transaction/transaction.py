import os
import uuid
import logging
from typing import Union

from pydano.cardano_cli import CardanoCli
from pydano.cardano_temp import tempdir
from pydano.query.protocol_param import ProtocolParam
from pydano.transaction.transaction_config import TransactionConfig
from pydano.transaction.miniting_config import MintingConfig


class Transaction(CardanoCli):
    def __init__(
        self,
        transaction_config: Union[TransactionConfig, MintingConfig],
        testnet: bool = True,
    ):
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


class RawTransaction(Transaction):
    transaction_file = None

    def run_raw_transaction(self):
        self.run_transaction()
        if self.transaction_file == None:
            raise ValueError("Intial transaction did not complete")
        calc_fee = CalculateMinFeeTransaction(
            self.transaction_config, self.transaction_file, testnet=self.testnet
        )
        fees_command_stdout = calc_fee.run_transaction()
        min_fees = fees_command_stdout.stdout.split()[0].strip()
        if type(min_fees) == bytes:
            min_fees = min_fees.decode()
        if not min_fees.isnumeric():
            raise ValueError("Error getting minfees")
        min_fees = int(min_fees)
        self.transaction_config.fees = min_fees
        self.run_transaction()
        return self


class SignTransaction(Transaction):
    def __init__(self, transaction: Transaction, signing_key: str):
        super().__init__(transaction.transaction_config, transaction.testnet)
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
        if type(self.signing_key) == list:
            for key in self.signing_key:
                base_transaction.append("--signing-key-file")
                base_transaction.append(key)

        else:
            base_transaction.append("--signing-key-file")
            base_transaction.append(self.signing_key)
        base_transaction.append("--out-file")
        self.signed_file = os.path.join(tempdir.name, f"{self.transaction_uuid}.signed")
        base_transaction.append(self.signed_file)
        self.prepared_transaction = base_transaction


class SubmitTransaction(Transaction):
    def __init__(self, signed_transaction: SignTransaction):
        super().__init__(
            signed_transaction.transaction_config, signed_transaction.testnet
        )
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


class SignAndSubmit:
    def submit(self, signing_key):
        print("Signing Transaction")
        st = SignTransaction(self, signing_key)
        st.run_transaction()
        print("Submitting Transaction")
        st = SubmitTransaction(st)
        st.run_transaction()


class BuildTransaction(Transaction, SignAndSubmit):

    raw = False
    minting = False

    def __init__(
        self,
        transaction_config: Union[TransactionConfig, MintingConfig],
        testnet: bool = True,
    ):
        super().__init__(transaction_config, testnet)
        self.protocol_file = ProtocolParam(testnet).protocol_params()

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "build", "--alonzo-era"]

    def build_base_transaction(self):
        command = self.base_command
        if not self.raw:
            command = self.apply_blockchain(command)
        else:
            command.extend(["--fee", str(self.transaction_config.fees)])
        command.extend(self.transaction_config.input_utxos_args())
        command.extend(self.transaction_config.out_tx_args())
        if self.minting:
            command.extend(self.transaction_config.mint_args())
        return command

    def build_output_file(self, command, version="draft"):
        command.append("--out-file")
        transaction_file = os.path.join(
            tempdir.name, f"{self.transaction_uuid}.{version}"
        )
        self.transaction_file = transaction_file
        command.append(transaction_file)
        return command

    def prepare_transaction(self):
        base_transaction = self.build_base_transaction()
        if not self.raw:
            base_transaction.append("--change-address")
            base_transaction.append(self.transaction_config.change_address)
        base_transaction.append("--protocol-params-file")
        base_transaction.append(self.protocol_file)
        complete_trans = self.build_output_file(base_transaction)
        self.prepared_transaction = complete_trans


class CalculateMinFeeTransaction(Transaction):
    def __init__(
        self,
        transaction_config: Union[TransactionConfig, MintingConfig],
        raw_transaction: str,
        testnet: bool = True,
    ):
        super().__init__(transaction_config, testnet)
        self.raw_transaction = raw_transaction
        self.protocol_file = ProtocolParam(testnet).protocol_params()

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "calculate-min-fee"]

    def prepare_transaction(self):
        command = self.base_command
        command.append("--tx-body-file")
        command.append(self.raw_transaction)
        len_output_txs = len(self.transaction_config.output_txs)
        command.extend(
            [
                "--tx-in-count",
                "1",
                "--tx-out-count",
                str(len_output_txs),
                "--witness-count",
                str(1 + len_output_txs),
            ]
        )
        command = self.apply_blockchain(command)
        command.append("--protocol-params-file")
        command.append(self.protocol_file)
        self.prepared_transaction = command


class BuildRawTransaction(BuildTransaction, RawTransaction, SignAndSubmit):

    raw = True

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "build-raw", "--alonzo-era"]


class MintRawTransaction(BuildTransaction, RawTransaction, SignAndSubmit):

    raw = True
    minting = True

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "build-raw", "--alonzo-era"]
