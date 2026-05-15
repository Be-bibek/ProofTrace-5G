// ChaCha20-Poly1305 Authenticated Encryption
// Provides confidentiality + integrity in one pass.
// Faster than AES on devices without hardware AES acceleration.

use chacha20poly1305::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    ChaCha20Poly1305, Nonce, Key,
};
use crate::errors::SecureMarkError;

/// Encrypt plaintext with ChaCha20-Poly1305.
/// Returns 12-byte nonce prepended to ciphertext: (nonce || ciphertext || poly1305_tag).
pub fn encrypt(key_bytes: &[u8; 32], plaintext: &[u8]) -> Result<Vec<u8>, SecureMarkError> {
    let key = Key::from_slice(key_bytes);
    let cipher = ChaCha20Poly1305::new(key);
    let nonce = ChaCha20Poly1305::generate_nonce(&mut OsRng);
    let ciphertext = cipher
        .encrypt(&nonce, plaintext)
        .map_err(|e| SecureMarkError::EncryptionError(e.to_string()))?;
    // Prepend 12-byte nonce to ciphertext
    let mut output = nonce.to_vec();
    output.extend_from_slice(&ciphertext);
    Ok(output)
}

/// Decrypt a (nonce || ciphertext) blob produced by encrypt().
/// Returns Err if the AEAD tag is invalid — indicating tampered ciphertext.
pub fn decrypt(key_bytes: &[u8; 32], nonce_and_ciphertext: &[u8]) -> Result<Vec<u8>, SecureMarkError> {
    if nonce_and_ciphertext.len() < 12 {
        return Err(SecureMarkError::DecryptionError);
    }
    let (nonce_bytes, ciphertext) = nonce_and_ciphertext.split_at(12);
    let key = Key::from_slice(key_bytes);
    let cipher = ChaCha20Poly1305::new(key);
    let nonce = Nonce::from_slice(nonce_bytes);
    cipher
        .decrypt(nonce, ciphertext)
        .map_err(|_| SecureMarkError::DecryptionError)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encrypt_decrypt_roundtrip() {
        let key = [0x42u8; 32];
        let plaintext = b"SecureMark5G test payload - BLAKE3 + ChaCha20";
        let encrypted = encrypt(&key, plaintext).unwrap();
        let decrypted = decrypt(&key, &encrypted).unwrap();
        assert_eq!(decrypted, plaintext);
    }

    #[test]
    fn test_tampered_ciphertext_fails() {
        let key = [0x42u8; 32];
        let mut encrypted = encrypt(&key, b"hello world").unwrap();
        // Flip a byte in the ciphertext body (after the 12-byte nonce)
        let last = encrypted.len() - 1;
        encrypted[last] ^= 0xFF;
        assert!(decrypt(&key, &encrypted).is_err());
    }

    #[test]
    fn test_wrong_key_fails() {
        let key1 = [0x11u8; 32];
        let key2 = [0x22u8; 32];
        let encrypted = encrypt(&key1, b"secret data").unwrap();
        assert!(decrypt(&key2, &encrypted).is_err());
    }

    #[test]
    fn test_empty_nonce_fails() {
        let key = [0x42u8; 32];
        assert!(decrypt(&key, &[]).is_err());
        assert!(decrypt(&key, &[0u8; 11]).is_err()); // Less than 12 bytes
    }

    #[test]
    fn test_nonce_is_unique_per_call() {
        let key = [0xAAu8; 32];
        let p = b"same plaintext";
        let enc1 = encrypt(&key, p).unwrap();
        let enc2 = encrypt(&key, p).unwrap();
        // Different nonces → different ciphertexts
        assert_ne!(&enc1[..12], &enc2[..12]);
    }
}
