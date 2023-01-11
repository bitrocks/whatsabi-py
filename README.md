# whatsabi-py

A python implementation of [WhatsABI](https://github.com/shazow/whatsabi).

# install

`pip install git+https://github.com/bitrocks/whatsabi-py.git`

# usage

```py
import asyncio
from web3 import Web3
from whatsabi.selectors import selectors_from_bytecode
from whatsabi.loaders import SamczsunSignatureLookup, FourByteSignatureLookup, MultiSignatureLookup

node_url = "http://127.0.0.1:8545" # Change to your endpoint
provider = Web3(Web3.HTTPProvider(node_url))
address = "0x00000000006c3852cbEf3e08E8dF289169EdE581"
code = provider.eth.get_code(address)
selectors = selectors_from_bytecode(code.hex())
print(selectors)
# ['0x00000000',
#  '0x06fdde03',
#  '0x46423aa7',
#  '0x55944a42',
#  '0x5b34b966',
#  '0x79df72bd',
#  '0x87201b41',
#  '0x88147732',
#  '0xa8174404',
#  '0xb3a34c4c',
#  '0xe7acab24',
#  '0xed98a574',
#  '0xf07ec373',
#  '0xf47b7740',
#  '0xfb0f3ee1',
#  '0xfd9f1e10']

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
