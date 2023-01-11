# whatsabi-py

A python implementation of [WhatsABI](https://github.com/shazow/whatsabi).

# install

`pip install git+https://github.com/bitrocks/whatsabi-py.git`

# usage

```py
import asyncio
from web3 import Web3
from whatsabi_py.selectors import selectors_from_bytecode
from whatsabi_py.loaders import SamczsunSignatureLookup, FourByteSignatureLookup, MultiSignatureLookup

node_url = "http://127.0.0.1:8545" # Change to your endpoint
provider = Web3(Web3.HTTPProvider(node_url))
address = "0x00000000006c3852cbEf3e08E8dF289169EdE581"
code = provider.eth.get_code(address)
selectors = selectors_from_bytecode(code.hex())

# SamczsunSignatureLookup
samczsun_sig_lookup = SamczsunSignatureLookup()
func_signatures = asyncio.get_event_loop().run_until_complete(samczsun_sig_lookup.load_functions("0x06fdde03"))
print(func_signatures)
# ['name()']

# FourByteSignatureLookup
fourbyte_sig_lookup = FourByteSignatureLookup()
func_signatures = asyncio.get_event_loop().run_until_complete(fourbyte_sig_lookup.load_functions("0x06fdde03"))
print(func_signatures)
# ['transfer_attention_tg_invmru_6e7aa58(bool,address,address)',
#  'message_hour(uint256,int8,uint16,bytes32)',
#  'name()']

# MultiSignatureLookup
multi_sig_lookup = MultiSignatureLookup([samczsun_sig_lookup, fourbyte_sig_lookup])
func_signatures = asyncio.get_event_loop().run_until_complete(multi_sig_lookup.load_functions("0x06fdde03"))
print(func_signatures)
# ['transfer_attention_tg_invmru_6e7aa58(bool,address,address)',
#  'message_hour(uint256,int8,uint16,bytes32)',
#  'name()']

# Event lookup
event_signatures = asyncio.get_event_loop().run_until_complete(samczsun_sig_lookup.load_events("0x721c20121297512b72821b97f5326877ea8ecf4bb9948fea5bfcb6453074d37f"))
print(event_signatures)
# ['CounterIncremented(uint256,address)']
```

# License
MIT
