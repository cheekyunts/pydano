from pydano.transaction.transaction_config import TransactionConfig
from pydano.transaction.transaction import BuildRawTransaction


class EmptyWallet:
    def __init__(
        self,
        in_address: str,
        out_address: str,
        min_utxo: int,
        min_change_utxo: int,
        mainnet: bool = False,
    ):
        self.in_address = in_address
        self.min_utxo = min_utxo
        self.mainnet = mainnet
        self.min_change_utxo = min_change_utxo
        self.out_address = out_address

    def run(self, signing_key):
        tc = TransactionConfig(
            self.in_address,
            self.min_utxo,
            testnet=not self.mainnet,
            min_change_utxo=self.min_change_utxo,
        )
        tc.add_input_utxos(self.in_address)
        tc.add_tx_out(self.out_address, "lovelace", tc.available_lovelace, True)
        for token, quantity in tc.available_tokens.items():
            tc.add_tx_out(self.out_address, token, quantity)
        bt = BuildRawTransaction(tc, testnet=not self.mainnet)
        bt.run_raw_transaction()
        bt.submit(signing_key)
