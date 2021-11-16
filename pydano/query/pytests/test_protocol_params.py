import pytest
import json

from pydano.query.protocol_param import ProtocolParam


def test_protocol_params():
    pp = ProtocolParam()
    param_file = pp.protocol_params()
    with open(param_file, "r") as f:
        json_params = json.load(f)
        assert "txFeePerByte" in json_params
        assert "costModels" in json_params
