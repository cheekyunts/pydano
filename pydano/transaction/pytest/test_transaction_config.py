import pytest
from unittest.mock import MagicMock

from pydano.transaction.transaction_config import TransactionConfig


@pytest.mark.transaction_config
def test_basic_transaction_config():

    tc = TransactionConfig("test_addr1", 1340000)
    tc.utxo.utxos = MagicMock(
        return_value=(
            [{"utxo_hash": "hash1", "utxo_amount": 6333333, "utxo_index": 0}],
            6333333,
            {},
        )
    )
    tc.add_input_utxos("test_addr1")
    tc.add_tx_out("addr_2", "lovelace", 2000000)

    assert tc.out_tx_args() == [
        "--tx-out",
        "addr_2+2000000",
        "--tx-out",
        "test_addr1+4333333",
    ]
    assert tc.input_utxos_args() == ["--tx-in", "hash1#0"]

    tc = TransactionConfig("test_addr1", 1340000)
    tc.utxo.utxos = MagicMock(
        return_value=(
            [{"utxo_hash": "hash1", "utxo_amount": 6333333, "utxo_index": 1}],
            6333333,
            {},
        )
    )
    tc.add_input_utxos("test_addr1")
    assert tc.input_utxos_args() == ["--tx-in", "hash1#1"]


# This also tests by default fees is deducted from person doing the transaction change address
@pytest.mark.transaction_config
def test_basic_transaction_config_check_fees():

    tc = TransactionConfig("test_addr1", 1340000)
    tc.fees = 333333
    tc.utxo.utxos = MagicMock(
        return_value=(
            [{"utxo_hash": "hash1", "utxo_amount": 6333333, "utxo_index": 0}],
            6333333,
            {},
        )
    )
    tc.add_input_utxos("test_addr1")
    tc.add_tx_out("addr_2", "lovelace", 2000000)

    assert tc.out_tx_args() == [
        "--tx-out",
        "addr_2+2000000",
        "--tx-out",
        "test_addr1+4000000",
    ]
    assert tc.input_utxos_args() == ["--tx-in", "hash1#0"]


# receiver pays the fees
@pytest.mark.transaction_config
def test_basic_transaction_config_check_fees_receiver_pays():

    tc = TransactionConfig("test_addr1", 1340000)
    tc.fees = 333333
    tc.utxo.utxos = MagicMock(
        return_value=(
            [{"utxo_hash": "hash1", "utxo_amount": 6333333, "utxo_index": 0}],
            6333333,
            {},
        )
    )
    tc.add_input_utxos("test_addr1")
    tc.add_tx_out("addr_2", "lovelace", 2333333, fee_payer=True)

    assert tc.out_tx_args() == [
        "--tx-out",
        "addr_2+2000000",
        "--tx-out",
        "test_addr1+4000000",
    ]
    assert tc.input_utxos_args() == ["--tx-in", "hash1#0"]
