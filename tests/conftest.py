import pytest
import json

UNI_V2_ROUTER02 = "./tests/data/UniswapV2Router02.json"


@pytest.fixture(scope="module")
def sample_abi():
    with open(UNI_V2_ROUTER02) as f:
        r = json.load(f)
        return r["abi"]


@pytest.fixture(scope="module")
def sample_code():
    with open(UNI_V2_ROUTER02) as f:
        r = json.load(f)
        return r["evm"]["deployedBytecode"]["object"]
