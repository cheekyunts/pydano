import pytest
from pydano.addresses.generate_address import Address


@pytest.mark.address
def test_generate_address():
    addr = Address()
    addr.generate_keypair()
    assert addr.verification != ""
    assert addr.signing != ""

    final_addr = addr.generate_address()
    assert final_addr.startswith("addr_test1")
