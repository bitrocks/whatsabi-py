import click
import asyncio
from web3 import Web3
from whatsabi import concurrency
from whatsabi.selectors import selectors_from_bytecode
from whatsabi.loaders import (
    FourByteSignatureLookup,
    SamczsunSignatureLookup,
    MultiSignatureLookup,
)


@click.group()
def cli():
    pass


@click.command()
def hello():
    click.echo("Hello World!")


@click.command()
@concurrency.coro
@click.option(
    "--url",
    default="http://127.0.0.1:8545",
    help="Ethereum rpc service endpoint, eg. Alchemy, Infura, etc",
)
@click.option(
    "--address",
    default="0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
    help="Ethereum contract address",
)
@click.option(
    "--siglookups",
    default=["samczsun"],
    help="SignatureLookup, choose between samczsun or 4byte or both",
)
async def guess_abi(url, address, siglookups):
    w3 = Web3(Web3.HTTPProvider(url))
    code = w3.eth.get_code(Web3.toChecksumAddress(address))
    selectors = selectors_from_bytecode(code.hex())

    multi_sig_lookup = MultiSignatureLookup(signature_lookups(siglookups))

    tasks = [wrap_load_functions(multi_sig_lookup, selector) for selector in selectors]
    signatures = await asyncio.gather(*tasks)
    flat_signatures = {
        k: v for signature_dict in signatures for k, v in signature_dict.items()
    }
    for k, v in flat_signatures.items():
        print(f"selector: {k}, candidate_signatures: {v}")


async def wrap_load_functions(sig_lookup, selector):
    signature = await sig_lookup.load_functions(selector)
    return {selector: signature}


def signature_lookups(lookups):
    sig_lookups = []
    if "samczsun" in lookups:
        sig_lookups.append(SamczsunSignatureLookup())
    if "4byte" in lookups:
        sig_lookups.append(FourByteSignatureLookup())
    return sig_lookups


if __name__ == "__main__":
    cli()
