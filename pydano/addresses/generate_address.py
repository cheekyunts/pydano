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
        if os.path.isfile(self.signing_file) or os.path.isfile(self.verification_file):
            raise FileExistsError(
                f"keypair file exists: {self.signing_file}, {self.verification_file} already exist, won't overwrite keys"
            )
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


class Address(GenerateKeyPair):

    """This generates the address, private key, public key and address"""

    def __init__(self, dirname: str = None, key_name: str = None, testnet: bool = True):
        self.key_name = key_name
        if not self.key_name:
            self.key_name = str(uuid.uuid4())
        self.dirname = dirname if dirname else tempdir.name
        self.verification_file = os.path.join(self.dirname, f"{self.key_name}.vkey")
        self.signing_file = os.path.join(self.dirname, f"{self.key_name}.skey")
        self.keyhash_file = os.path.join(self.dirname, f"{self.key_name}.keyhash")
        self.address_file = os.path.join(self.dirname, f"{self.key_name}.addr")
        super().__init__(self.verification_file, self.signing_file, testnet)

    def load(self):
        if (
            not os.path.isfile(self.verification_file)
            or not os.path.isfile(self.signing_file)
            or not os.path.isfile(self.keyhash_file)
            or not os.path.isfile(self.address_file)
        ):
            raise FileNotFoundError(
                "You are missing one of the skey, vkey, keyhash, addr file."
            )
        self.read_address()
        self.read_keyhash()

    @property
    def verification(self):
        return json.load(open(self.verification_file, "r"))["cborHex"]

    @property
    def signing(self):
        return json.load(open(self.signing_file, "r"))["cborHex"]

    def create_address(self):
        self.generate_keypair()
        address = self.generate_address()
        keyhash = self.generate_keyhash()
        return address

    def generate_address(self):
        if os.path.isfile(self.address_file):
            raise FileExistsError(
                f"Address file: {self.address_file} already exist, use load() instead"
            )
        current_command = self.base_command
        current_command.append("build")
        current_command.append("--payment-verification-key-file")
        current_command.append(self.verification_file)
        current_command.append("--out-file")
        current_command.append(self.address_file)
        current_command = self.apply_blockchain(current_command)
        logging.debug(f"Running command: {current_command}")
        self.run_command(current_command)
        self.read_address()
        logging.info(f"Generated keys: {self.address}")
        return self.address

    def read_address(self):
        self.address = open(self.address_file, "r").read().strip()

    def generate_keyhash(self):
        if os.path.isfile(self.keyhash_file):
            raise FileExistsError(
                f"Keyhash file: {self.keyhash_file} already exist, use load() instead"
            )
        current_command = self.base_command
        current_command.append("key-hash")
        current_command.append("--payment-verification-key-file")
        current_command.append(self.verification_file)
        current_command.append("--out-file")
        current_command.append(self.keyhash_file)
        logging.debug(f"Running command: {current_command}")
        self.run_command(current_command)
        self.read_keyhash()
        logging.info(f"Generated keyhash: {self.keyhash_file}")
        return self.keyhash

    def read_keyhash(self):
        self.keyhash = open(self.keyhash_file, "r").read().strip()
