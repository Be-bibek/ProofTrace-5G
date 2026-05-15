// Replay Attack Prevention via Timestamp Window Validation

use crate::errors::SecureMarkError;
use std::time::{SystemTime, UNIX_EPOCH};

/// Maximum allowed age of a packet timestamp in seconds.
/// Packets older than this window are rejected as potential replay attacks.
pub const REPLAY_WINDOW_SECONDS: u64 = 30;

/// Validate that a received timestamp is within the acceptable window.
/// Handles clock skew in both directions (|now - ts| <= REPLAY_WINDOW_SECONDS).
pub fn validate_timestamp(received_ts: u64) -> Result<(), SecureMarkError> {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("Clock error")
        .as_secs();

    let age = if now >= received_ts {
        now - received_ts
    } else {
        received_ts - now
    };

    if age <= REPLAY_WINDOW_SECONDS {
        Ok(())
    } else {
        Err(SecureMarkError::ReplayAttack)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_timestamp_now() {
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();
        assert!(validate_timestamp(ts).is_ok());
    }

    #[test]
    fn test_valid_timestamp_within_window() {
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            - 15; // 15 seconds ago — within the 30s window
        assert!(validate_timestamp(ts).is_ok());
    }

    #[test]
    fn test_expired_timestamp() {
        let old_ts = 1_000_000u64; // Far in the past
        assert!(validate_timestamp(old_ts).is_err());
    }

    #[test]
    fn test_boundary_just_inside_window() {
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            - REPLAY_WINDOW_SECONDS; // Exactly at the boundary
        assert!(validate_timestamp(ts).is_ok());
    }

    #[test]
    fn test_boundary_just_outside_window() {
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            - REPLAY_WINDOW_SECONDS
            - 1; // One second past the boundary
        assert!(validate_timestamp(ts).is_err());
    }
}
