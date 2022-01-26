import os
import time

from pydano.addresses.generate_address import Address
from pydano.transaction.transaction_config import TransactionConfig
from pydano.transaction.transaction import BuildRawTransaction
from pydano.features.empty_wallet import EmptyWallet
from pydano.query.utxo import UTXOs

FUND_WALLET_ADDRESS = os.environ["FUND_WALLET_ADDRESS"]
FUND_WALLET_SIGNING_KEY = os.environ["FUND_WALLET_SIGNING_KEY"]
MAINNET = os.environ.get("MAINNET", False)
MIN_UTXO = os.environ.get("MIN_UTXO", 1000000)
MIN_CHANGE_UTXO = os.environ.get("MIN_CHANGE_UTXO", 1000000)
WAIT_TIME = os.environ.get("TRANSACTION_WAIT_TIME", 60)


def get_random_address():
    addr = Address()
    addr.generate_keypair()
    final_addr = addr.generate_address()
    return addr


def add_money(addr: Address, amount: int):
    tc = TransactionConfig(
        FUND_WALLET_ADDRESS,
        MIN_UTXO,
        testnet=not MAINNET,
        min_change_utxo=MIN_CHANGE_UTXO,
    )
    tc.add_input_utxos(FUND_WALLET_ADDRESS)
    tc.add_tx_out(addr.read_address(), "lovelace", amount)
    bt = BuildRawTransaction(tc, testnet=not MAINNET)
    bt.run_raw_transaction()
    bt.submit(FUND_WALLET_SIGNING_KEY)


def empty_wallet(addr: Address):
    ew = EmptyWallet(
        addr.read_address(), FUND_WALLET_ADDRESS, MIN_UTXO, MIN_CHANGE_UTXO, MAINNET
    )
    ew.run(addr.signing_file)


def check_lovelace(addr: Address, amount: int):
    time.sleep(WAIT_TIME)
    utxos = UTXOs(not MAINNET)
    _, lovelace, _ = utxos.utxos(addr.read_address())
    assert lovelace >= amount
