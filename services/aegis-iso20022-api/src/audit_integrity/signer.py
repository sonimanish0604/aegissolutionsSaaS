from __future__ import annotations

import base64
import hmac
from abc import ABC, abstractmethod
from hashlib import sha256
from typing import Protocol


class ManifestSigner(Protocol):
    def sign(self, payload: bytes) -> str:
        ...


class LocalHmacSigner:
    """HMAC-SHA256 signer using an in-memory secret (for local/dev use)."""

    def __init__(self, secret: bytes) -> None:
        self._secret = secret

    def sign(self, payload: bytes) -> str:
        signature = hmac.new(self._secret, payload, sha256).digest()
        return base64.b64encode(signature).decode("ascii")


class KmsSigner(ManifestSigner):  # pragma: no cover - requires AWS
    """AWS KMS-backed signer using GenerateMac/VerifyMac"""

    def __init__(self, kms_client, key_id: str, mac_algorithm: str = "HMAC_SHA_256") -> None:
        self._kms_client = kms_client
        self._key_id = key_id
        self._mac_algorithm = mac_algorithm

    def sign(self, payload: bytes) -> str:
        response = self._kms_client.generate_mac(
            KeyId=self._key_id,
            Message=payload,
            MacAlgorithm=self._mac_algorithm,
        )
        mac = response["Mac"]
        return base64.b64encode(mac).decode("ascii")

    def verify(self, payload: bytes, signature: str) -> bool:
        mac = base64.b64decode(signature)
        try:
            self._kms_client.verify_mac(
                KeyId=self._key_id,
                Message=payload,
                MacAlgorithm=self._mac_algorithm,
                Mac=mac,
            )
            return True
        except self._kms_client.exceptions.KMSInvalidMacException:
            return False
