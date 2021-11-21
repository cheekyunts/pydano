from pydano.transaction.transaction_config import TransactionConfig
from pydano.transaction.transaction import BuildTransaction, BuildRawTransaction


class MintTransaction(BuildTransaction):
    def build_base_transaction(self):
        command = self.base_command
        command = self.apply_blockchain(command)
        command.extend(self.transaction_config.input_utxos_args())
        command.extend(self.transaction_config.out_tx_args())
        command.extend(self.transaction_config.mint_args())
        return command


# TODO: Maybe we can use multiple inheritance here.
class MintRawTransaction(BuildRawTransaction):
    def build_base_transaction(self):
        command = self.base_command
        command = self.apply_blockchain(command)
        command.extend(["--fee", str(self.transaction_config.fees)])
        command.extend(self.transaction_config.input_utxos_args())
        command.extend(self.transaction_config.out_tx_args())
        command.extend(self.transaction_config.mint_args())
        return command
