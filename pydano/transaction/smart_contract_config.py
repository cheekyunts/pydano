import os
import json
import tempfile
import uuid

from pydano.transaction.transaction_config import TransactionConfig
from pydano.transaction.policy_transaction import PolicyIDTransaction
from pydano.cardano_temp import tempdir


class SmartContractConfig(TransactionConfig):

    smart_contract = True

    def __init__(
        self,
        change_address: str,
        min_utxo: int,
        testnet: bool = True,
        min_change_utxo: int = 1340000,
    ):
        super().__init__(change_address, min_utxo, testnet, min_change_utxo)
        if not smart_contract_file:
            raise ValueError(
                "Smart contract config requires plutus smart contract file"
            )
        self.datum_file = None
        self.redeemer_file = None
        self.smart_contract_file = None

    def add_datum_file(self, datum_file: str):
        self.datum_file = datum_file
        ### Run a transation code to convert datum file to datum hash for the transaction
        ### and also keep that saved

    def add_redeemer_file(self, reedemer_file: str, smart_contract_file: str):
        self.redeemer_file = reedemer_file
        self.smart_contract_file = smart_contract_file

    def sc_args(self):
        ## We can have two cases here:
        # 1. Locking the script
        #     this required sending --datum_hash
        # 2. Unlocking the script
        #   this require sending --tx-in-script-file --tx-in-datum-file --tx-in-reedemer_file
        pass
