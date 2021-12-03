import json

import base58
from cryptography.fernet import Fernet
from metaplex.transactions import (
    burn,
    deploy,
    mint,
    send,
    topup,
    update_token_metadata,
)
from metaplex.utils.execution_engine import execute
from solana.keypair import Keypair


class MetaplexAPI:
    def __init__(self, cfg):
        self.private_key = list(base58.b58decode(cfg["PRIVATE_KEY"]))[:32]
        self.public_key = cfg["PUBLIC_KEY"]
        self.keypair = Keypair(self.private_key)
        self.cipher = Fernet(cfg["DECRYPTION_KEY"])

    def wallet(self):
        """Generate a wallet and return the address and private key."""
        keypair = Keypair()
        pub_key = keypair.public_key
        private_key = list(keypair.seed)
        return json.dumps({"address": str(pub_key), "private_key": private_key})

    async def deploy(
        self,
        api_endpoint,
        name,
        symbol,
        fees,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
    ):
        """
        Deploy a contract to the blockchain (on network that support contracts). Takes the network ID and contract name, plus initialisers of name and symbol. Process may vary significantly between blockchains.
        Returns status code of success or fail, the contract address, and the native transaction data.
        """
        try:
            tx, signers, contract = await deploy(
                api_endpoint, self.keypair, name, symbol, fees
            )
            print(contract)
            resp = await execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            resp["contract"] = contract
            resp["status"] = 200
            return json.dumps(resp)
        except:
            return json.dumps({"status": 400})

    async def topup(
        self,
        api_endpoint,
        to,
        amount=None,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
    ):
        """
        Send a small amount of native currency to the specified wallet to handle gas fees. Return a status flag of success or fail and the native transaction data.
        """
        try:
            tx, signers = await topup(api_endpoint, self.keypair, to, amount=amount)
            resp = await execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            resp["status"] = 200
            return json.dumps(resp)
        except:
            return json.dumps({"status": 400})

    async def mint(
        self,
        api_endpoint,
        contract_key,
        metadata,
        dest_key,
        link,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
        supply=1,
    ):
        """
        Mints an NFT to an account, updates the metadata and creates a master edition
        """
        tx, signers = await mint(
            api_endpoint,
            self.keypair,
            contract_key,
            metadata,
            dest_key,
            link,
            supply=supply,
        )
        resp = await execute(
            api_endpoint,
            tx,
            signers,
            max_retries=max_retries,
            skip_confirmation=skip_confirmation,
            max_timeout=max_timeout,
            target=target,
            finalized=finalized,
        )
        resp["status"] = 200
        return json.dumps(resp)
        # except:
        #     return json.dumps({"status": 400})

    async def update_token_metadata(
        self,
        api_endpoint,
        mint_token_id,
        link,
        data,
        creators_addresses,
        creators_verified,
        creators_share,
        fee,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
        supply=1,
    ):
        """
        Updates the json metadata for a given mint token id.
        """
        tx, signers = await update_token_metadata(
            api_endpoint,
            self.keypair,
            mint_token_id,
            link,
            data,
            fee,
            creators_addresses,
            creators_verified,
            creators_share,
        )
        resp = await execute(
            api_endpoint,
            tx,
            signers,
            max_retries=max_retries,
            skip_confirmation=skip_confirmation,
            max_timeout=max_timeout,
            target=target,
            finalized=finalized,
        )
        resp["status"] = 200
        return json.dumps(resp)

    async def send(
        self,
        api_endpoint,
        contract_key,
        sender_key,
        dest_key,
        encrypted_private_key,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
    ):
        """
        Transfer a token on a given network and contract from the sender to the recipient.
        May require a private key, if so this will be provided encrypted using Fernet: https://cryptography.io/en/latest/fernet/
        Return a status flag of success or fail and the native transaction data.
        """
        try:
            private_key = list(self.cipher.decrypt(encrypted_private_key))
            tx, signers = await send(
                api_endpoint,
                self.keypair,
                contract_key,
                sender_key,
                dest_key,
                private_key,
            )
            resp = await execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            resp["status"] = 200
            return json.dumps(resp)
        except:
            return json.dumps({"status": 400})

    async def burn(
        self,
        api_endpoint,
        contract_key,
        owner_key,
        encrypted_private_key,
        max_retries=3,
        skip_confirmation=False,
        max_timeout=60,
        target=20,
        finalized=True,
    ):
        """
        Burn a token, permanently removing it from the blockchain.
        May require a private key, if so this will be provided encrypted using Fernet: https://cryptography.io/en/latest/fernet/
        Return a status flag of success or fail and the native transaction data.
        """
        try:
            private_key = list(self.cipher.decrypt(encrypted_private_key))
            tx, signers = await burn(api_endpoint, contract_key, owner_key, private_key)
            resp = await execute(
                api_endpoint,
                tx,
                signers,
                max_retries=max_retries,
                skip_confirmation=skip_confirmation,
                max_timeout=max_timeout,
                target=target,
                finalized=finalized,
            )
            resp["status"] = 200
            return json.dumps(resp)
        except:
            return json.dumps({"status": 400})
