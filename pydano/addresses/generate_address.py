import logging
import uuid
import os
import json

from pydano.cardano_temp import tempdir
from pydano.cardano_cli import CardanoCli


class GenerateKeyPair(CardanoCli):
    def __init__(self, verification_file: str, signing_file: str, testnet: bool = True):
        super().__init__(testnet)
        self.verification_file = verification_file
        self.signing_file = signing_file

    def generate_keypair(self):
        current_command = self.base_command
        current_command.append("key-gen")
        current_command.append("--verification-key-file")
        current_command.append(self.verification_file)
        current_command.append("--signing-key-file")
        current_command.append(self.signing_file)
        logging.debug(f"Running command: {current_command}")
        self.run_command(current_command)
        logging.info(f"Generated keys: {self.verification_file}, {self.signing_file}")

    @property
    def base_command(self):
        return ["cardano-cli", "address"]

    def generate_address(self):
        current_command = self.base_command
        current_command.append("build")
        current_command.append("--payment-verification-key-file")
        current_command.append(self.verification_file)
        current_command.append("--out-file")
        address_file = os.path.join(tempdir.name, f"{self.key_name}.addr")
        current_command.append(address_file)
        current_command = self.apply_blockchain(current_command)
        logging.debug(f"Running command: {current_command}")
        self.run_command(current_command)
        final_address = open(address_file, "r").read().strip()
        logging.info(f"Generated keys: {final_address}")
        return final_address


class Address(GenerateKeyPair):

    """This generates the address, private key, public key and address"""

    def __init__(self, dirname: str = None, key_name: str = None, testnet: bool = True):
        self.key_name = key_name
        if not self.key_name:
            self.key_name = str(uuid.uuid4())
        self.dirname = dirname if dirname else tempdir.name
        self.verification_file = os.path.join(self.dirname, f"{self.key_name}.vkey")
        self.signing_file = os.path.join(self.dirname, f"{self.key_name}.skey")
        super().__init__(self.verification_file, self.signing_file, testnet)

    @property
    def verification(self):
        return json.load(open(self.verification_file, "r"))["cborHex"]

    @property
    def signing(self):
        return json.load(open(self.signing_file, "r"))["cborHex"]

    def create_address(self):
        self.generate_keypair()
        return self.generate_address()
