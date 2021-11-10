from pydano.transaction.transaction import Transaction, TransactionConfig, CalculateMinFeeTransaction

class AdjustFeeTransaction:
    def __init__(self, transaction: Transaction, transaction_config: TransactionConfig):
        self.transaction = transaction
        self.transaction_config = transaction_config

    def run_transaction(self):
        self.transaction.run_transaction()
        calc_fee = CalculateMinFeeTransaction(self.transaction_config, self.transaction.transaction_file, testnet=self.transaction.testnet)
        fees_command_stdout = calc_fee.run_transaction()
        min_fees = fees_command_stdout.stdout.split()[0].strip()
        if type(min_fees) == bytes:
            min_fees = min_fees.decode()
        if not min_fees.isnumeric():
            raise ValueError("Error getting minfees")
        min_fees = int(min_fees)
        self.transaction.transaction_config.fees = min_fees
        self.transaction.run_transaction()
        return self.transaction

