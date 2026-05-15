// BLAKE3-based Authentication Token Generation
// Token = BLAKE3(device_id || secret_key || watermarked_payload || timestamp_nonce)

use blake3::Hasher;
use crate::errors::SecureMarkError;
use std::time::{SystemTime, UNIX_EPOCH};

pub struct AuthToken(pub [u8; 32]);

impl AuthToken {
    pub fn to_hex(&self) -> String {
        hex::encode(self.0)
    }
}

/// Generate a 32-byte BLAKE3 authentication token.
/// The timestamp is embedded as a nonce to prevent replay attacks.
pub fn generate_token(
    device_id: &str,
    secret_key: &[u8],
    payload: &[u8],
    timestamp: u64,
) -> AuthToken {
    let mut hasher = Hasher::new();
    hasher.update(device_id.as_bytes());
    hasher.update(secret_key);
    hasher.update(payload);
    hasher.update(&timestamp.to_le_bytes());
    let hash = hasher.finalize();
    AuthToken(*hash.as_bytes())
}

/// Verify a received token against the recomputed expected token.
/// Uses constant-time comparison to prevent timing attacks.
pub fn verify_token(
    received: &[u8; 32],
    device_id: &str,
    secret_key: &[u8],
    payload: &[u8],
    timestamp: u64,
) -> Result<(), SecureMarkError> {
    let expected = generate_token(device_id, secret_key, payload, timestamp);
    // Constant-time comparison: accumulate XOR diff across all bytes
    let diff: u8 = received
        .iter()
        .zip(expected.0.iter())
        .fold(0u8, |acc, (a, b)| acc | (a ^ b));
    if diff == 0 {
        Ok(())
    } else {
        Err(SecureMarkError::TokenMismatch)
    }
}

/// Get current UNIX timestamp in seconds.
pub fn current_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("System clock before UNIX epoch")
        .as_secs()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_token_round_trip() {
        let device_id = "IOT_DEVICE_001";
        let secret_key = b"super_secret_key_32bytes_exactly";
        let payload = b"TEMP:30.5|HUM:65.2";
        let ts = current_timestamp();

        let token = generate_token(device_id, secret_key, payload, ts);
        assert!(verify_token(&token.0, device_id, secret_key, payload, ts).is_ok());
    }

    #[test]
    fn test_wrong_key_fails() {
        let ts = current_timestamp();
        let token = generate_token("DEV", b"correct_key_00000000000000000000", b"data", ts);
        assert!(verify_token(&token.0, "DEV", b"wrong_key_000000000000000000000", b"data", ts).is_err());
    }

    #[test]
    fn test_wrong_device_id_fails() {
        let ts = current_timestamp();
        let key = b"testkey_32bytes_exactly_padded!!";
        let token = generate_token("DEVICE_A", key, b"payload", ts);
        assert!(verify_token(&token.0, "DEVICE_B", key, b"payload", ts).is_err());
    }

    #[test]
    fn test_wrong_payload_fails() {
        let ts = current_timestamp();
        let key = b"testkey_32bytes_exactly_padded!!";
        let token = generate_token("DEV", key, b"original", ts);
        assert!(verify_token(&token.0, "DEV", key, b"modified", ts).is_err());
    }

    #[test]
    fn test_wrong_timestamp_fails() {
        let ts = current_timestamp();
        let key = b"testkey_32bytes_exactly_padded!!";
        let token = generate_token("DEV", key, b"data", ts);
        assert!(verify_token(&token.0, "DEV", key, b"data", ts + 1).is_err());
    }
}
