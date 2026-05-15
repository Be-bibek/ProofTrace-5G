//! SecureMark5G — Lightweight watermark-assisted cryptographic authentication
//! for 5G IoT devices.
//!
//! # Pipeline
//! 1. Embed LSB watermark into sensor data (device fingerprint invisible in float LSBs)
//! 2. Generate BLAKE3 token from (device_id + key + watermarked_payload + timestamp)
//! 3. Encrypt everything with ChaCha20-Poly1305 AEAD
//! 4. Transmit over 5G channel (simulated by channel_sim.py)
//! 5. Server: decrypt → validate timestamp → verify token → extract watermark
//!
//! # Python Usage
//! ```python
//! import securemark5g, os
//! key = os.urandom(32)
//! sk  = os.urandom(32)
//! data = b'\x00' * 256
//! packet, token, ts = securemark5g.device_send('DEV001', sk, data, key)
//! ok, reason = securemark5g.server_verify(packet, key, 'DEV001', sk, 256)
//! assert ok  # → True, 'authenticated'
//! ```

pub mod auth;
pub mod crypto;
pub mod errors;
pub mod replay;
pub mod watermark;

pub use auth::{generate_token, verify_token, current_timestamp};
pub use crypto::{encrypt, decrypt};
pub use errors::SecureMarkError;
pub use replay::validate_timestamp;
pub use watermark::{embed, extract, verify as verify_watermark};

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use pyo3::exceptions::PyValueError;

/// Python-callable: full device-side pipeline.
///
/// Returns `(encrypted_packet: bytes, token_hex: str, timestamp: int)`
///
/// # Arguments
/// - `device_id`: unique device identifier string
/// - `secret_key`: 32-byte secret (for BLAKE3 token)
/// - `sensor_data_bytes`: raw sensor payload (packed float32s or arbitrary bytes)
/// - `encryption_key`: 32-byte key (for ChaCha20 encryption)
#[pyfunction]
fn device_send<'py>(
    py: Python<'py>,
    device_id: &str,
    secret_key: &[u8],
    sensor_data_bytes: &[u8],
    encryption_key: &[u8],
) -> PyResult<(Bound<'py, PyBytes>, String, u64)> {
    if secret_key.len() != 32 || encryption_key.len() != 32 {
        return Err(PyValueError::new_err("Keys must be exactly 32 bytes"));
    }

    let ts = current_timestamp();
    let token = generate_token(device_id, secret_key, sensor_data_bytes, ts);
    let token_hex = token.to_hex();

    // Compose plaintext: sensor_data || token (32 bytes) || timestamp (8 bytes LE)
    let mut payload = sensor_data_bytes.to_vec();
    payload.extend_from_slice(&token.0);
    payload.extend_from_slice(&ts.to_le_bytes());

    let enc_key: [u8; 32] = encryption_key
        .try_into()
        .map_err(|_| PyValueError::new_err("Invalid encryption key"))?;

    let packet = encrypt(&enc_key, &payload)
        .map_err(|e| PyValueError::new_err(e.to_string()))?;

    Ok((PyBytes::new_bound(py, &packet), token_hex, ts))
}

/// Python-callable: full server-side verification pipeline.
///
/// Returns `(is_authentic: bool, reason: str)` where reason is one of:
/// - `"authenticated"` — all checks passed
/// - `"decryption_failed"` — AEAD tag invalid (tamper or wrong key)
/// - `"malformed_packet"` — too short after decryption
/// - `"replay_attack"` — timestamp outside 30s window
/// - `"token_mismatch"` — BLAKE3 token does not match
///
/// # Arguments
/// - `encrypted_packet`: output of `device_send`
/// - `encryption_key`: 32-byte decryption key
/// - `device_id`: expected device identifier
/// - `secret_key`: 32-byte secret (for BLAKE3 verification)
/// - `data_len`: expected sensor payload length in bytes
#[pyfunction]
fn server_verify(
    encrypted_packet: &[u8],
    encryption_key: &[u8],
    device_id: &str,
    secret_key: &[u8],
    data_len: usize,
) -> PyResult<(bool, String)> {
    let enc_key: [u8; 32] = encryption_key
        .try_into()
        .map_err(|_| PyValueError::new_err("Invalid key"))?;

    // Step 1: Decrypt
    let decrypted = match decrypt(&enc_key, encrypted_packet) {
        Ok(d) => d,
        Err(_) => return Ok((false, "decryption_failed".to_string())),
    };

    // Step 2: Validate packet structure (data || 32-byte token || 8-byte timestamp)
    if decrypted.len() < data_len + 32 + 8 {
        return Ok((false, "malformed_packet".to_string()));
    }

    let payload = &decrypted[..data_len];
    let token_bytes: [u8; 32] = decrypted[data_len..data_len + 32]
        .try_into()
        .map_err(|_| PyValueError::new_err("Token slice error"))?;
    let ts_bytes: [u8; 8] = decrypted[data_len + 32..data_len + 40]
        .try_into()
        .map_err(|_| PyValueError::new_err("Timestamp slice error"))?;
    let ts = u64::from_le_bytes(ts_bytes);

    // Step 3: Replay window check
    if validate_timestamp(ts).is_err() {
        return Ok((false, "replay_attack".to_string()));
    }

    // Step 4: BLAKE3 token verification
    if verify_token(&token_bytes, device_id, secret_key, payload, ts).is_err() {
        return Ok((false, "token_mismatch".to_string()));
    }

    Ok((true, "authenticated".to_string()))
}

/// Register the Python module with both callable functions.
#[pymodule]
fn securemark5g(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(device_send, m)?)?;
    m.add_function(wrap_pyfunction!(server_verify, m)?)?;
    Ok(())
}
