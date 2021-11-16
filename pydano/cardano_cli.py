import subprocess


class CardanoCli(object):

    """Docstring for CardanoCli."""

    def __init__(self, testnet: bool = True):
        self.testnet = testnet

    @property
    def base_command(self):
        return ["cardano-cli"]

    def apply_blockchain(self, command_array: list):
        if self.testnet:
            return command_array + ["--testnet-magic", "1097911063"]
        return command_array + ["--mainnet"]

    def run_command(self, command_argv: list):
        try:
            return subprocess.run(command_argv, check=True, capture_output=True)
        except Exception as e:
            print(e.output, e.stderr)
            raise e
