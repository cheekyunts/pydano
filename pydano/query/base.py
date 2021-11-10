import tempfile

from pydano.cardano_cli import CardanoCli

class Query(CardanoCli):

    """Base class to do cardano cli query
       Currently it will include doing query for
       protocol parameters or utxos for assets and sums.

    """
    def __init__(self, testnet: bool = True):
        super().__init__(testnet)
   
    @property
    def base_command(self):
        return ["cardano-cli", "query"]

