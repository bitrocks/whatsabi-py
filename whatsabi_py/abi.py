from typing import Optional, List, Union


class ABIFunction:
    type: str = "function"
    selector: str
    sig: Optional[str]
    sig_alts: Optional[List[str]]
    payable: Optional[bool]


class ABIEvent:
    type: str = "event"
    selector: str
    sig: Optional[str]
    sig_alts: Optional[List[str]]


ABI = List[Union[ABIFunction, ABIEvent]]
