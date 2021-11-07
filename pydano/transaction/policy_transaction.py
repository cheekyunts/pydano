import logging

from pydano.cardano_cli import CardanoCli

class PolicyIDTransaction(CardanoCli):

    def __init__(self, testnet: bool = True):
        super().__init__(testnet)

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "policyid"]

    def policyID(self, script_file):
        command = self.base_command
        command.append("--script-file")
        command.append(script_file)
        capturedout = self.run_command(command)
        policyid = capturedout.stdout.strip().decode('utf-8')
        logging.info(f"Policy ID for minting script {script_file} is {policyid}")
        return policyid
