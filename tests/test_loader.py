import pytest
from whatsabi_py.loaders import (
    EtherscanLoader,
    SourcifyABILoader,
    FourByteSignatureLookup,
    SamczsunSignatureLookup,
    MultiSignatureLookup,
)
from whatsabi_py.selectors import selectors_from_abi, events_from_bytecode


@pytest.mark.asyncio
@pytest.mark.skip(reason="comment this out if network is avaliable")
async def test_etherscan_abi_loader(sample_abi):
    etherscan_loader = EtherscanLoader()
    address = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
    abi = await etherscan_loader.load_abi(address)
    print(abi)
    assert False


@pytest.mark.asyncio
@pytest.mark.skip(reason="comment this out if network is avaliable")
async def test_etherscan_abi_loader(sample_abi):
    sourcify_loader = SourcifyABILoader()
    address = "0x7a250d5630b4cf539739df2c5dacb4c659f2488d"
    abi = await sourcify_loader.load_abi(address)
    print(abi)
    assert False


@pytest.mark.asyncio
@pytest.mark.skip(reason="comment this out if network is avaliable")
async def test_samczsun_load_functions(sample_abi):
    samczsun = SamczsunSignatureLookup()
    signatures = await samczsun.load_functions("0x46423aa7")
    assert "getOrderStatus(bytes32)" in signatures

    selector_to_signature = selectors_from_abi(sample_abi)
    for selector, expect_signature in selector_to_signature.items():
        signature = await samczsun.load_functions(selector)
        assert expect_signature in signature


@pytest.mark.asyncio
@pytest.mark.skip(reason="comment this out if network is avaliable")
async def test_4byte_load_functions(sample_abi):
    fourbyte = FourByteSignatureLookup()
    signatures = await fourbyte.load_functions("0x46423aa7")
    assert "getOrderStatus(bytes32)" in signatures

    selector_to_signature = selectors_from_abi(sample_abi)
    for selector, expect_signature in selector_to_signature.items():
        signature = await fourbyte.load_functions(selector)
        assert expect_signature in signature


@pytest.mark.asyncio
@pytest.mark.skip(reason="comment this out if network is avaliable")
async def test_samczsun_load_events():
    samczsun = SamczsunSignatureLookup()
    signatures = await samczsun.load_events(
        "0x721c20121297512b72821b97f5326877ea8ecf4bb9948fea5bfcb6453074d37f"
    )
    assert "CounterIncremented(uint256,address)" in signatures


@pytest.mark.asyncio
@pytest.mark.skip(reason="comment this out if network is avaliable")
async def test_4byte_load_events():
    fourbyte = FourByteSignatureLookup()
    signatures = await fourbyte.load_events(
        "0x721c20121297512b72821b97f5326877ea8ecf4bb9948fea5bfcb6453074d37f"
    )
    assert "CounterIncremented(uint256,address)" in signatures


@pytest.mark.asyncio
# @pytest.mark.skip(reason="comment this out if network is avaliable")
async def test_multi_signature_lookup():
    multi_signature_lookup = MultiSignatureLookup(
        [SamczsunSignatureLookup(), FourByteSignatureLookup()]
    )
    function_signatures = await multi_signature_lookup.load_functions("0x46423aa7")
    assert "getOrderStatus(bytes32)" in function_signatures

    event_signatures = await multi_signature_lookup.load_events(
        "0x721c20121297512b72821b97f5326877ea8ecf4bb9948fea5bfcb6453074d37f"
    )
    assert "CounterIncremented(uint256,address)" in event_signatures
