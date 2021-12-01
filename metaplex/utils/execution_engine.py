import asyncio

from solana.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts


async def execute(
    api_endpoint,
    tx,
    signers,
    max_retries=3,
    skip_confirmation=True,
    max_timeout=60,
    target=20,
    finalized=True,
):
    async with AsyncClient(api_endpoint) as client:
        signers = list(map(Keypair, set(map(lambda s: s.seed, signers))))
        for attempt in range(max_retries):
            try:
                result = await client.send_transaction(
                    tx, *signers, opts=TxOpts(skip_preflight=True)
                )
                print(result)
                signatures = [x.signature for x in tx.signatures]
                if not skip_confirmation:
                    await confirmation(
                        client, signatures, max_timeout, target, finalized
                    )
                return result
            except Exception as e:
                print(f"Failed attempt {attempt}: {e}")
                continue
        raise e


async def confirmation(client, signatures, max_timeout=60, target=20, finalized=True):
    elapsed = 0
    while elapsed < max_timeout:
        sleep_time = 1
        await asyncio.sleep(sleep_time)
        elapsed += sleep_time
        resp = await client.get_signature_statuses(signatures)
        if resp["result"]["value"][0] is not None:
            confirmations = resp["result"]["value"][0]["confirmations"]
            is_finalized = (
                resp["result"]["value"][0]["confirmationStatus"] == "finalized"
            )
        else:
            continue
        if not finalized:
            if confirmations >= target or is_finalized:
                print(f"Took {elapsed} seconds to confirm transaction")
                return
        elif is_finalized:
            print(f"Took {elapsed} seconds to confirm transaction")
            return
