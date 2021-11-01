from pydano.query.base import Query
from pydano.cardano_temp import protocol_params_file

class UTXOs(Query):

    """This performs the query for utxo at address"""

    def process_stdout(self, output):
        if type(output) == bytes:
            output = output.decode('utf-8')
        utxoTableRows = output.strip().splitlines()
        available_utxos = []
        totalLovelace = 0
        for x in range(2, len(utxoTableRows)):
            cells = utxoTableRows[x].split()
            totalLovelace +=  int(cells[2])
            available_utxos.append({'utxo_hash': cells[0], 'utxo_index': cells[1]})
        return available_utxos, totalLovelace

    def utxos(self, address):
        current_command = self.base_command
        current_command.append("utxo")
        updated_command = self.apply_blockchain(current_command)
        updated_command.append("--address")
        updated_command.append(address)
        print("Running command", updated_command)
        called_process = self.run_command(updated_command)
        return self.process_stdout(called_process.stdout)
