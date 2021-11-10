import logging

from pydano.query.base import Query
from pydano.cardano_temp import protocol_params_file

class ProtocolParam(Query):

    """This performs the query for protocol parameters"""

    """
    protocol_params: This queries for current protocol parameter file
                     and return location of the file to be used in other requests.
        @returns location of file containing current parameter file.
    """
    def protocol_params(self):
        current_command = self.base_command
        current_command.append("protocol-parameters")
        updated_command = self.apply_blockchain(current_command)
        protocol_file = protocol_params_file()
        updated_command.append("--out-file")
        updated_command.append(protocol_file)
        logging.debug(f"Running command: {updated_command}")
        self.run_command(updated_command)
        return protocol_file
