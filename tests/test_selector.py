from whatsabi_py.selectors import selectors_from_bytecode, selectors_from_abi


def test_selectors_from_bytecode_match_from_abi(sample_code, sample_abi):
    selector_to_signature = selectors_from_abi(sample_abi)
    expected = list(selector_to_signature.keys())
    selectors = selectors_from_bytecode(sample_code)
    assert set(expected) == set(selectors)
