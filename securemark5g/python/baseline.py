"""
AES-256-GCM + SHA-256 Python baseline.
Used for performance comparison against the Rust/BLAKE3/ChaCha20 implementation.

This is deliberately NOT optimized — it uses pure Python cryptography to represent
the kind of implementation a typical developer would write without Rust.
"""
import hashlib
import os
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def baseline_generate_token(
    device_id: str,
    secret_key: bytes,
    payload: bytes,
    timestamp: int,
) -> bytes:
    """Generate SHA-256 authentication token (Python baseline)."""
    h = hashlib.sha256()
    h.update(device_id.encode())
    h.update(secret_key)
    h.update(payload)
    h.update(timestamp.to_bytes(8, "little"))
    return h.digest()


def baseline_encrypt(key: bytes, plaintext: bytes) -> bytes:
    """Encrypt with AES-256-GCM. Returns nonce || ciphertext || tag."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ct


def baseline_decrypt(key: bytes, data: bytes) -> bytes:
    """Decrypt AES-256-GCM ciphertext. Raises InvalidTag on tamper."""
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(data[:12], data[12:], None)


def baseline_full_pipeline(
    device_id: str,
    secret_key: bytes,
    payload: bytes,
    enc_key: bytes,
) -> tuple:
    """Full device-side pipeline: token generation + encryption.

    Returns:
        (packet: bytes, token_hex: str, timestamp: int)
    """
    ts = int(time.time())
    token = baseline_generate_token(device_id, secret_key, payload, ts)
    full_plaintext = payload + token + ts.to_bytes(8, "little")
    packet = baseline_encrypt(enc_key, full_plaintext)
    return packet, token.hex(), ts


def baseline_server_verify(
    encrypted_packet: bytes,
    enc_key: bytes,
    device_id: str,
    secret_key: bytes,
    data_len: int,
    replay_window: int = 30,
) -> tuple:
    """Full server-side verification pipeline (Python baseline).

    Returns:
        (is_authentic: bool, reason: str)
    """
    try:
        decrypted = baseline_decrypt(enc_key, encrypted_packet)
    except Exception:
        return False, "decryption_failed"

    if len(decrypted) < data_len + 32 + 8:
        return False, "malformed_packet"

    payload = decrypted[:data_len]
    token_received = decrypted[data_len:data_len + 32]
    ts_bytes = decrypted[data_len + 32:data_len + 40]
    ts = int.from_bytes(ts_bytes, "little")

    # Replay check
    if abs(time.time() - ts) > replay_window:
        return False, "replay_attack"

    # Token verify
    expected_token = baseline_generate_token(device_id, secret_key, payload, ts)
    if token_received != expected_token:
        return False, "token_mismatch"

    return True, "authenticated"
