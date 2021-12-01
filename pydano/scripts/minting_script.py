import json

from pydano.cardano_temp import get_temp_file
from pydano.addresses.generate_address import Address
from pydano.transaction.policy_transaction import PolicyIDTransaction


class MintingScript:
    def __init__(self, address: Address, locking_slot: int, file_name=""):
        self.address = address
        self.locking_slot = locking_slot
        self.file_name = file_name

    @property
    def policy_script(self):
        initial_script = {"scripts": [], "type": "all"}
        if not self.address:
            raise ValueError("Need valid address for generating script file")
        initial_script["scripts"].append(
            {"keyHash": self.address.keyhash, "type": "sig"}
        )
        if self.locking_slot:
            initial_script["scripts"].append(
                {"slot": self.locking_slot, "type": "before"}
            )
        return initial_script

    @property
    def policy_script_file(self):
        if self.file_name:
            tmp_file = self.file_name
        else:
            tmp_file = get_temp_file(prefix=".minting_script")
            self.file_name = tmp_file
        return self.file_name

    def generate_scriptfile(self):
        tmp_file = self.policy_script_file
        script = self.policy_script
        with open(tmp_file, "w") as f:
            json.dump(script, f, indent=4)
        return tmp_file

    @property
    def policy_id(self):
        file_ = self.policy_script_file
        policy_transaction = PolicyIDTransaction(False)
        return policy_transaction.policyID(file_)
