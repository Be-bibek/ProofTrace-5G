"""
Python integration tests for the SecureMark5G Rust extension.
Run with: pytest tests/ -v
"""
import os
import sys
import pytest

try:
    import securemark5g
except ImportError:
    pytest.skip("securemark5g not installed — run: maturin develop", allow_module_level=True)


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def keys():
    return {
        "enc_key":    os.urandom(32),
        "secret_key": os.urandom(32),
    }

@pytest.fixture
def payload():
    """256 bytes of zero-padded sensor data."""
    return b"\x00" * 256


# ─── Round-trip tests ─────────────────────────────────────────────────────────

def test_device_send_returns_tuple(keys, payload):
    result = securemark5g.device_send("DEV001", keys["secret_key"], payload, keys["enc_key"])
    assert isinstance(result, tuple) and len(result) == 3
    packet, token_hex, ts = result
    assert isinstance(packet, bytes) and len(packet) > 0
    assert isinstance(token_hex, str) and len(token_hex) == 64  # 32 bytes hex
    assert isinstance(ts, int) and ts > 0


def test_authenticated_round_trip(keys, payload):
    packet, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload, keys["enc_key"])
    ok, reason = securemark5g.server_verify(packet, keys["enc_key"], "DEV001", keys["secret_key"], len(payload))
    assert ok is True
    assert reason == "authenticated"


def test_wrong_enc_key_fails(keys, payload):
    packet, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload, keys["enc_key"])
    wrong_key = os.urandom(32)
    ok, reason = securemark5g.server_verify(packet, wrong_key, "DEV001", keys["secret_key"], len(payload))
    assert ok is False
    assert reason == "decryption_failed"


def test_wrong_secret_key_fails(keys, payload):
    packet, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload, keys["enc_key"])
    wrong_sk = os.urandom(32)
    ok, reason = securemark5g.server_verify(packet, keys["enc_key"], "DEV001", wrong_sk, len(payload))
    assert ok is False
    assert reason == "token_mismatch"


def test_wrong_device_id_fails(keys, payload):
    packet, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload, keys["enc_key"])
    ok, reason = securemark5g.server_verify(packet, keys["enc_key"], "FAKE_DEVICE", keys["secret_key"], len(payload))
    assert ok is False
    assert reason == "token_mismatch"


def test_tampered_packet_fails(keys, payload):
    packet, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload, keys["enc_key"])
    tampered = bytearray(packet)
    tampered[-1] ^= 0xFF
    ok, reason = securemark5g.server_verify(bytes(tampered), keys["enc_key"], "DEV001", keys["secret_key"], len(payload))
    assert ok is False
    assert reason == "decryption_failed"


def test_key_length_validation(keys, payload):
    with pytest.raises(Exception):
        securemark5g.device_send("DEV001", b"short", payload, keys["enc_key"])
    with pytest.raises(Exception):
        securemark5g.device_send("DEV001", keys["secret_key"], payload, b"short")


def test_different_payloads_produce_different_packets(keys):
    payload1 = b"\x00" * 256
    payload2 = b"\xFF" * 256
    p1, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload1, keys["enc_key"])
    p2, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload2, keys["enc_key"])
    assert p1 != p2


def test_nonce_randomness_produces_different_packets(keys, payload):
    """Two calls with identical inputs produce different ciphertexts (unique nonces)."""
    p1, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload, keys["enc_key"])
    p2, _, _ = securemark5g.device_send("DEV001", keys["secret_key"], payload, keys["enc_key"])
    assert p1 != p2  # Different nonces → different ciphertexts


def test_multiple_devices_independent(keys, payload):
    """Verify that authentication is device-specific."""
    sk_a = os.urandom(32)
    sk_b = os.urandom(32)
    packet_a, _, _ = securemark5g.device_send("DEV_A", sk_a, payload, keys["enc_key"])
    packet_b, _, _ = securemark5g.device_send("DEV_B", sk_b, payload, keys["enc_key"])
    # DEV_A's packet should not verify for DEV_B's credentials
    ok, _ = securemark5g.server_verify(packet_a, keys["enc_key"], "DEV_B", sk_b, len(payload))
    assert ok is False
