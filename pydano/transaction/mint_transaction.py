from pydano.transaction.transaction import BuildTransaction, BuildRawTransaction, TransactionConfig
from pydano.transaction.policy_transaction import PolicyIDTransaction

class MintTransaction(BuildTransaction):

    def __init__(self, transaction_config: TransactionConfig, testnet: bool = True, minting_script_file='', metadata_json_file=None):
        super().__init__(transaction_config, testnet)
        if not minting_script_file:
            raise ValueError("Minting requires Minting script")
        self.minting_script_file = minting_script_file
        self.metadata_json_file = metadata_json_file
        self.policyID = PolicyIDTransaction(testnet).policyID(self.minting_script_file)

    def build_base_transaction(self):
        command = self.base_command
        command = self.apply_blockchain(command)
        command.extend(self.transaction_config.input_utxos_args())
        command.extend(self.transaction_config.out_tx_args())
        command.extend(self.transaction_config.mint_args(self.minting_script_file, self.metadata_json_file))
        return command

# TODO: Maybe we can use multiple inheritance here.
class MintRawTransaction(BuildRawTransaction):

    def __init__(self, transaction_config: TransactionConfig, testnet: bool = True, minting_script_file='', metadata_json_file=None):
        super().__init__(transaction_config, testnet)
        if not minting_script_file:
            raise ValueError("Minting requires Minting script")
        self.minting_script_file = minting_script_file
        self.metadata_json_file = metadata_json_file
        self.policyID = PolicyIDTransaction(testnet).policyID(self.minting_script_file)

    def build_base_transaction(self):
        command = self.base_command
        command.extend(['--fee', str(self.transaction_config.fees)])
        command.extend(self.transaction_config.input_utxos_args())
        command.extend(self.transaction_config.out_tx_args())
        command.extend(self.transaction_config.mint_args(self.minting_script_file, self.metadata_json_file))
        return command
