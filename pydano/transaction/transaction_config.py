import json
import logging
from collections import defaultdict, Counter

from pydano.query.utxo import UTXOs


class TransactionConfig:

    # controls addition of minting arguments in built command.
    minting = False

    """
    This class is responsible to hold input and output utxos
    which is passed around the transaction processing fees.
    """

    def __init__(
        self,
        change_address: str,
        min_utxo: int,
        testnet: bool = True,
        min_change_utxo: int = 1340000,
    ):
        self.input_utxos = []
        self.output_txs = defaultdict(list)
        self.mints = []
        self.change_address = change_address
        self.available_lovelace = 0
        self.available_tokens = set()
        self.min_utxo = min_utxo
        self.min_change_utxo = min_change_utxo
        self.testnet = testnet
        self.fees = 0
        self.fee_payer_address = None
        self.utxo = UTXOs(testnet=self.testnet)

    """
    add_input_utxo: This is a helper function, it queries all the utxos on a address
                and add it to the transaction.
    """

    def add_input_utxos(self, addr: str):
        utxos, self.available_lovelace, self.available_tokens = self.utxo.utxos(addr)
        logging.info(
            f"Total amount available at addres {addr} is {self.available_lovelace}, {self.available_tokens}"
        )
        logging.debug(f"All UTXOs at addres {utxos}")
        for i in utxos:
            self.add_tx_in(**i)

    """
    add_input_utxo: This will add a new input utxo to the transaction.

    This will be added to the traction based on query utxo or input address
    depending on the usecase such as minting etc.

    @params:
        input_utxo: utxo to add as input to the transaction.
    """

    def add_tx_in(self, utxo_hash: str, utxo_index: int, **kwargs):
        self.input_utxos.append({"utxo_hash": utxo_hash, "utxo_index": utxo_index})
        return len(self.input_utxos)

    """
    add_tx_out: Add new asset to transfer
    @params:
        out_address: Payment address of receiver of the asset.
        asset_name: this can be lovlace/native token or name of the nft.
        asset_quanity: quantity of token/lovelace to transfer. Should be 1 in case of NFTs..
    """

    def add_tx_out(
        self, out_address: str, asset_name: str, asset_quantity: int, fee_payer=False
    ):
        out = {
            "out_address": out_address,
            "name": asset_name,
            "quantity": asset_quantity,
        }

        self.output_txs[out_address].append(out)
        if fee_payer:
            self.fee_payer_address = out_address
        return len(self.output_txs)

    def input_utxos_args(self):
        command_args = []
        assert len(self.input_utxos) > 0
        for utxo in self.input_utxos:
            command_args.append("--tx-in")
            command_args.append(f"{utxo['utxo_hash']}#{utxo['utxo_index']}")
        return command_args

    def out_tx_args(self):
        command_args = []
        fees_paid = False
        available_lovelace = self.available_lovelace
        available_tokens = self.available_tokens.copy()
        for out_address, out_assets in self.output_txs.items():
            out_asset_counter = Counter()
            for asset in out_assets:
                out_asset_counter[asset["name"]] += asset["quantity"]
            command_args.append("--tx-out")
            assert len(out_asset_counter) > 0

            # It is mandatory to have one ADA transaction
            # So add min_utxo ada to each output tx
            if "lovelace" in out_asset_counter:
                quantity = out_asset_counter["lovelace"]
                del out_asset_counter["lovelace"]
            else:
                quantity = self.min_utxo
            # Deduct the fee from out_transaction which is supposed to pay fees
            if out_address == self.fee_payer_address:
                quantity -= self.fees
                available_lovelace -= self.fees
                fees_paid = True
            tx_out_config = "+" + str(quantity)
            available_lovelace -= quantity
            for remanining_asset in out_asset_counter.items():
                name = remanining_asset[0]
                quantity = remanining_asset[1]
                if (name not in self.mints) and (
                    name not in self.available_tokens
                    or self.available_tokens[name] < quantity
                ):
                    raise ValueError(
                        f"Trying to spend asset {name}, which is not available in {remanining_asset}, {out_assets}"
                    )
                tx_out_config += "+" + str(quantity) + " " + str(name)
                if name not in self.mints:
                    available_tokens[name] -= quantity
            command_args.append(out_address + tx_out_config)

        # This is to return non-ada assets back to change_address, as they are not
        # accounted in current `transaction build` and `cardano-cli` complains about
        # unbalances non-ada assets.
        if len(available_tokens) > 0 or available_lovelace > 0:
            pending_lovlace = available_lovelace
            if not fees_paid:
                pending_lovlace -= self.fees
            if pending_lovlace < self.min_change_utxo:
                raise ValueError("Not enough money for returning the change")
            command_args.append("--tx-out")
            leftover_out_config = "+" + str(pending_lovlace)
            for key, value in available_tokens.items():
                leftover_out_config += "+" + str(value) + " " + str(key)
            command_args.append(self.change_address + leftover_out_config)
        return command_args
