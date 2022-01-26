import pytest

from pydano.test_utils import (
    get_random_address,
    add_money,
    empty_wallet,
    check_lovelace,
    MIN_UTXO,
    MIN_CHANGE_UTXO,
    MAINNET,
    FUND_WALLET_SIGNING_KEY,
)
from pydano.features.empty_wallet import EmptyWallet


def test_empty_wallet():
    amount = 10000000
    fees = 200000
    addr = get_random_address()
    add_money(addr, amount)
    check_lovelace(addr, amount)
    addr2 = get_random_address()
    ew = EmptyWallet(
        addr.read_address(), addr2.read_address(), MIN_UTXO, MIN_CHANGE_UTXO, MAINNET
    )
    ew.run(addr.signing_file)
    check_lovelace(addr2, amount - fees)
    check_lovelace(addr, 0)
    empty_wallet(addr2)
