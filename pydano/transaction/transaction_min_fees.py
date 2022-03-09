from typing import Union

from pydano.cardano_cli import CardanoCli
from pydano.transaction.transaction_config import TransactionConfig
from pydano.transaction.transaction import Transaction
from pydano.transaction.miniting_config import MintingConfig

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

    def min_fees(self):
        self.prepare_transaction()
        fees_command_stdout = self.run_command(self.prepared_transaction)
        min_fees = fees_command_stdout.stdout.split()[0].strip()
        if type(min_fees) == bytes:
            min_fees = min_fees.decode()
        if not min_fees.isnumeric():
            raise ValueError("Error getting minfees")
        return int(min_fees)

