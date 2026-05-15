use thiserror::Error;

#[derive(Error, Debug)]
pub enum SecureMarkError {
    #[error("Encryption failed: {0}")]
    EncryptionError(String),
    #[error("Decryption failed — ciphertext may be tampered")]
    DecryptionError,
    #[error("Watermark mismatch — data integrity violated")]
    WatermarkMismatch,
    #[error("Replay attack detected — timestamp expired")]
    ReplayAttack,
    #[error("Token verification failed — authentication denied")]
    TokenMismatch,
    #[error("Invalid key length: expected 32 bytes")]
    InvalidKeyLength,
}
