from typing import List, Any, Dict
from web3 import Web3
from .disasm import abi_from_bytecode
from .utils import get_signature


def selectors_from_abi(abi: List[Any]) -> Dict[str, str]:
    selector_to_signature = {}
    for abi_description in abi:
        if abi_description["type"] == "function":
            signature = get_signature(abi_description)
            signature_hash = Web3.keccak(text=signature)[0:4].hex()
            selector_to_signature.update({signature_hash: signature})
    return selector_to_signature


def selectors_from_bytecode(code: str) -> List[str]:
    abi = abi_from_bytecode(code)
    if len(abi) == 0:
        return []

    selectors = []
    for a in abi:
        if a["type"] != "function":
            continue
        selectors.append(a["selector"])
    return selectors


def events_from_bytecode(code: str) -> List[str]:
    abi = abi_from_bytecode(code)
    if len(abi) == 0:
        return []

    events = []
    for a in abi:
        if a["type"] != "event":
            continue
        events.append(a["hash"])
    return events
