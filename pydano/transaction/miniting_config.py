import os
import json
import tempfile
import uuid

from pydano.transaction.transaction_config import TransactionConfig
from pydano.transaction.policy_transaction import PolicyIDTransaction
from pydano.cardano_temp import tempdir


class MintingConfig(TransactionConfig):

    minting = True

    def __init__(
        self,
        minting_script_file: str,
        change_address: str,
        min_utxo: int,
        testnet: bool = True,
        metadata_json_file: str = None,
        min_change_utxo: int = 1340000,
    ):
        super().__init__(change_address, min_utxo, testnet, min_change_utxo)
        if not minting_script_file:
            raise ValueError("Minting requires Minting script")
        self.minting_script_file = minting_script_file
        self.metadata_json_file = metadata_json_file
        self.minting_metadata = []
        self.all_metadata_content = (
            json.load(open(metadata_json_file, "r")) if metadata_json_file else {}
        )
        self.policyID = PolicyIDTransaction(testnet).policyID(self.minting_script_file)

    def add_mint(self, out_address: str, token_name: str, token_metadata: dict = None):
        if token_metadata:
            # assert token_metadata["asset_name"] == token_name
            self.minting_metadata.append(token_metadata)
        elif token_name in self.all_metadata_content:
            metadata = self.all_metadata_content[token_name]
            # assert metadata["name"] == token_name
            self.minting_metadata.append(metadata)
        mint_token_name = f"{self.policyID}.{token_name}"
        out = {"out_address": out_address, "name": mint_token_name, "quantity": 1}
        self.output_txs[out_address].append(out)
        self.mints.append(mint_token_name)

    @property
    def get_metadata_file(self):
        if not self.minting_metadata:
            return None
        tmp_metadata_file = os.path.join(tempdir.name, f"{str(uuid.uuid4())}.json")
        final_metadata = {
            "721": {
                f"self.policyID": {
                    mint_token["name"]: mint_token
                    for mint_token in self.minting_metadata
                }
            }
        }
        with open(tmp_metadata_file, "w") as f:
            json.dump(final_metadata, f)
        return tmp_metadata_file

    def mint_args(self):
        command_args = ["--mint"]
        mint_args = ""
        first_transaction = True
        for i in self.mints:
            if first_transaction:
                first_transaction = False
            else:
                mint_args += "+"
            mint_args += f"1 {i}"
        command_args.append(mint_args)
        command_args.append("--minting-script-file")
        command_args.append(self.minting_script_file)
        metadata_json_file = self.get_metadata_file
        if metadata_json_file:
            command_args.append("--metadata-json-file")
            command_args.append(metadata_json_file)
        script = json.load(open(self.minting_script_file, "r"))
        all_locking = list(filter(lambda x: "slot" in x, script["scripts"]))
        if "slot" in all_locking[0]:
            invalid_hereafter_slot = all_locking[0]["slot"]
            command_args.append("--invalid-hereafter")
            command_args.append(str(invalid_hereafter_slot))
        return command_args
