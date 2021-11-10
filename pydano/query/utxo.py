import logging
from collections import Counter

from pydano.query.base import Query
from pydano.cardano_temp import protocol_params_file

class UTXOs(Query):

    """This performs the query for utxo at address"""

    def parse_row(self, row):
        lovelace = 0
        tokens = Counter()
        # Extract hash
        row = row.strip()
        hash_end = row.find(' ')
        hash_  = row[:hash_end]

        # Extract index
        row = row[hash_end:].strip()
        index_end = row.find(' ')
        index = row[:index_end]
        row = row[index_end:].strip()

        # Extract assets of each UTXOs
        all_assets = row.split('+')
        for asset in all_assets:
            asset = asset.strip()
            if asset == 'TxOutDatumHashNone':
                continue
            try:
                quantity, asset_name = asset.split()
                asset_name = asset_name.strip()
                quantity = int(quantity.strip())
                if asset_name == 'lovelace':
                    lovelace += quantity
                else:
                    tokens[asset_name] += quantity
            except Exception as e:
                logging.error(f"Unable to parse asset with {asset}, {e}")
        return hash_, index, lovelace, tokens

    def process_stdout(self, output):
        if type(output) == bytes:
            output = output.decode('utf-8')
        utxoTableRows = output.strip().splitlines()
        available_utxos = []
        tokens = Counter()
        totalLovelace = 0
        for x in range(2, len(utxoTableRows)):
            utxo_hash, utxo_index, lovelace, utxo_tokens = self.parse_row(utxoTableRows[x])
            totalLovelace +=  lovelace
            tokens = tokens + utxo_tokens
            available_utxos.append({'utxo_hash': utxo_hash, 'utxo_index': utxo_index, 'utxo_amount': lovelace})
        return available_utxos, totalLovelace, tokens

    def utxos(self, address):
        current_command = self.base_command
        current_command.append("utxo")
        updated_command = self.apply_blockchain(current_command)
        updated_command.append("--address")
        updated_command.append(address)
        logging.debug(f"Running command: {updated_command}")
        called_process = self.run_command(updated_command)
        return self.process_stdout(called_process.stdout)
