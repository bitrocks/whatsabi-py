from typing import Union
from web3 import Web3
from eth_utils import abi


def hexlify(b: bytes) -> str:
    return "0x" + b.hex()


def arrayify(b: Union[str, bytes]) -> bytes:
    if isinstance(b, str):
        if b.startswith("0x"):
            b = b[2:]
        return bytes.fromhex(b)
    return b


def zero_pad(b: bytes, length: int) -> bytes:
    return b.rjust(length, b"\0")


def bytes_to_int(b: bytes) -> int:
    return int.from_bytes(b, "big")


def get_signature(abi_description) -> str:
    inputs = abi_description["inputs"]
    joined_input_types = ",".join(
        input["type"] if input["type"] != "tuple" else abi.collapse_if_tuple(input)
        for input in inputs
    )
    signature = f"{abi_description['name']}({joined_input_types})"
    return signature
