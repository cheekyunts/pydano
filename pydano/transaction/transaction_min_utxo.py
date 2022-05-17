from typing import Union

from pydano.cardano_cli import CardanoCli
from pydano.query.protocol_param import ProtocolParam

class CalculateMinUTXOTransaction(CardanoCli):
    def __init__(
        self,
        tx_out: str,
        testnet: bool = True,
    ):
        super().__init__(testnet)
        self.tx_out = tx_out
        self.protocol_file = ProtocolParam(testnet).protocol_params()

    def min_utxo(self) -> int:
        self.prepare_transaction()
        print(self.prepared_transaction)
        utxo_command_stdout = self.run_command(self.prepared_transaction)
        min_req_utxo_fees = int(utxo_command_stdout.stdout.split()[1].strip())
        return min_req_utxo_fees

    @property
    def base_command(self):
        return ["cardano-cli", "transaction", "calculate-min-required-utxo"]

    def prepare_transaction(self):
        command = self.base_command
        command.append("--tx-out")
        command.append(self.tx_out)
        command.append("--protocol-params-file")
        command.append(self.protocol_file)
        self.prepared_transaction = command
