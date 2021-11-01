class Transaction:

    def __init__(self, signing_key: str, testnet: bool = True):
        self.signing_key = signing_key
        self.input_utxos = []
        self.output_txs = []
        self.testnet = True

    """
    add_input_utxo: This will add a new input utxo to the transaction.
    
    This will be added to the traction based on query utxo or input address
    depending on the usecase such as minting etc.

    @params:
        input_utxo: utxo to add as input to the transaction.
    """
    def add_tx_in(self, input_utxo: str):
        self.input_utxos.append(input_utxo)
        return len(self.input_utxos)

    """
    add_tx_out: Add new asset to transfer
    @params:
        out_address: Payment address of receiver of the asset.
        asset_name: this can be lovlace/native token or name of the nft.
        asset_quanity: quantity of token/lovelace to transfer. Should be 1 in case of NFTs..
    """
    def add_tx_out(self, out_address: str, asset_name: str, asset_quantity: int):
        out = {'out_address': out_address,
                'name': asset_name,
                'quantity': asset_quantity
                }
        self.output_txs.append(out)
        return len(self.output_txs)

    """
    get_protocol_parameters: This queries for current protocol parameter file
                             and return location of the file to be used in other requests.
        @returns location of file containing current parameter file.
    """
    def get_protocol_parameters(self) -> str:
        return None

    """
    prepare_raw_transaction: Prepare raw transaction mostly to calculate block chain fees
        @returns return the file location, which contains draft transaction to calculate fees.
    """
    def prepare_raw_transaction(self) -> str:
        return None

    """
    calc_min_fees: Take the protocol parameter file and draft transaction.
        @return: fees required by the blockchain to perform this transaction
    """
    def calc_min_fees(self, tx_draft: str, protocol_file: str) -> int:
        return None
    
    """
    prepare_final_transaction: This gets the final transaction accounting for all transactions and fees
    """
    def prepare_final_transaction(self, min_fees: int) -> str:
        return None

    """
    Signs the final transaction and returns path for signed transaction
    """
    def sign_transaction(self, tx_final: str) -> str:
        return None

    """
    Submits the transaction to the blockchain
    """
    def submit_transaction(self, tx_signed: str) -> str:
        return None

    """
    execute: This performs the whole flow of executing transation end-to-end
             when only utxo and expected output are returned
    """
    def execute(self):
        protocol_file = self.get_protocol_parameters()
        tx_draft = self.prepare_raw_transaction()
        min_fees = self.calc_min_fees(tx_draft, protocol_file)
        tx_final = self.prepare_final_transaction(min_fees)
        tx_signed = self.sign_transaction(tx_final)
        self.submit_transaction(tx_signed)
        return True


class CardanoCLITransactions(Transaction):
    def get_protocol_file(self):


