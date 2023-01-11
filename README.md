# whatsabi-py

A python implementation of [WhatsABI](https://github.com/shazow/whatsabi).

# install

```
pip install git+https://github.com/bitrocks/whatsabi-py.git
```

# cli usage
Pull the code:
```sh
git clone https://github.com/bitrocks/whatsabi-py
cd whatsabi-py
poetry install
# Extract abi
poetry run guess_abi --url <ethereum-rpc> --address <address> --siglookups samczsun | 4byte | samczsun,4byte
```

Eg.
```
poetry run guess_abi --url http://127.0.0.1:8545 --address 0x7a250d5630b4cf539739df2c5dacb4c659f2488d --siglookups samczsun
```
Output:
```
selector: 0xe8e33700, candidate_signatures: ['addLiquidity(address,address,uint256,uint256,uint256,uint256,address,uint256)']
selector: 0xf305d719, candidate_signatures: ['addLiquidityETH(address,uint256,uint256,uint256,address,uint256)']
selector: 0xfb3bdb41, candidate_signatures: ['swapETHForExactTokens(uint256,address[],address,uint256)']
selector: 0xc45a0155, candidate_signatures: ['factory()']
selector: 0xd06ca61f, candidate_signatures: ['getAmountsOut(uint256,address[])']
selector: 0xded9382a, candidate_signatures: ['removeLiquidityETHWithPermit(address,uint256,uint256,uint256,address,uint256,bool,uint8,bytes32,bytes32)']
selector: 0xaf2979eb, candidate_signatures: ['removeLiquidityETHSupportingFeeOnTransferTokens(address,uint256,uint256,uint256,address,uint256)']
selector: 0xb6f9de95, candidate_signatures: ['swapExactETHForTokensSupportingFeeOnTransferTokens(uint256,address[],address,uint256)']
selector: 0xbaa2abde, candidate_signatures: ['removeLiquidity(address,address,uint256,uint256,uint256,address,uint256)']
selector: 0x8803dbee, candidate_signatures: ['swapTokensForExactTokens(uint256,uint256,address[],address,uint256)']
selector: 0xad5c4648, candidate_signatures: ['WETH()']
selector: 0xad615dec, candidate_signatures: ['quote(uint256,uint256,uint256)']
selector: 0x791ac947, candidate_signatures: ['swapExactTokensForETHSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)']
selector: 0x7ff36ab5, candidate_signatures: ['swapExactETHForTokens(uint256,address[],address,uint256)']
selector: 0x85f8c259, candidate_signatures: ['getAmountIn(uint256,uint256,uint256)']
selector: 0x4a25d94a, candidate_signatures: ['swapTokensForExactETH(uint256,uint256,address[],address,uint256)']
selector: 0x5b0d5984, candidate_signatures: ['removeLiquidityETHWithPermitSupportingFeeOnTransferTokens(address,uint256,uint256,uint256,address,uint256,bool,uint8,bytes32,bytes32)']
selector: 0x5c11d795, candidate_signatures: ['swapExactTokensForTokensSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)']
selector: 0x1f00ca74, candidate_signatures: ['getAmountsIn(uint256,address[])']
selector: 0x2195995c, candidate_signatures: ['removeLiquidityWithPermit(address,address,uint256,uint256,uint256,address,uint256,bool,uint8,bytes32,bytes32)']
selector: 0x38ed1739, candidate_signatures: ['swapExactTokensForTokens(uint256,uint256,address[],address,uint256)']
selector: 0x02751cec, candidate_signatures: ['removeLiquidityETH(address,uint256,uint256,uint256,address,uint256)']
selector: 0x054d50d4, candidate_signatures: ['getAmountOut(uint256,uint256,uint256)']
selector: 0x18cbafe5, candidate_signatures: ['swapExactTokensForETH(uint256,uint256,address[],address,uint256)']
```


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
