// LSB Steganographic Watermarking
// Embeds a device fingerprint into the least significant bits of sensor float values.
// The watermark is invisible to normal inspection but detectable on extraction.

use crate::errors::SecureMarkError;

/// Embed a watermark string into the LSBs of a float array.
/// Each byte of the watermark occupies 8 consecutive f32 LSBs (1 bit each).
/// Returns Err if sensor data is shorter than 8 * watermark.len() samples.
pub fn embed(data: &mut [f32], watermark: &[u8]) -> Result<(), SecureMarkError> {
    if data.len() < watermark.len() * 8 {
        return Err(SecureMarkError::EncryptionError(
            "Sensor data too short to carry watermark".into(),
        ));
    }
    for (byte_idx, &wm_byte) in watermark.iter().enumerate() {
        for bit_pos in 0..8 {
            let sample_idx = byte_idx * 8 + bit_pos;
            let bit = (wm_byte >> bit_pos) & 1;
            let bits = data[sample_idx].to_bits();
            // Clear LSB and set to watermark bit
            let new_bits = (bits & !1u32) | (bit as u32);
            data[sample_idx] = f32::from_bits(new_bits);
        }
    }
    Ok(())
}

/// Extract watermark bytes from the LSBs of a float array.
pub fn extract(data: &[f32], wm_len: usize) -> Vec<u8> {
    let mut result = vec![0u8; wm_len];
    for (byte_idx, item) in result.iter_mut().enumerate().take(wm_len) {
        let mut byte = 0u8;
        for bit_pos in 0..8 {
            let sample_idx = byte_idx * 8 + bit_pos;
            if sample_idx < data.len() {
                let lsb = (data[sample_idx].to_bits() & 1) as u8;
                byte |= lsb << bit_pos;
            }
        }
        *item = byte;
    }
    result
}

/// Verify that the extracted watermark matches the expected value.
pub fn verify(data: &[f32], expected_wm: &[u8]) -> Result<(), SecureMarkError> {
    let extracted = extract(data, expected_wm.len());
    if extracted == expected_wm {
        Ok(())
    } else {
        Err(SecureMarkError::WatermarkMismatch)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_embed_extract_roundtrip() {
        let mut data: Vec<f32> = (0..256).map(|x| x as f32 * 0.1).collect();
        let wm = b"DEV_101_AUTH";
        embed(&mut data, wm).unwrap();
        let extracted = extract(&data, wm.len());
        assert_eq!(extracted, wm.as_ref());
    }

    #[test]
    fn test_tamper_detection() {
        let mut data: Vec<f32> = (0..256).map(|x| x as f32 * 0.1).collect();
        let wm = b"DEV_101";
        embed(&mut data, wm).unwrap();
        // Simulate tamper: flip a bit in the data
        data[10] += 1.0;
        assert!(verify(&data, wm).is_err());
    }

    #[test]
    fn test_short_data_error() {
        let mut data: Vec<f32> = vec![1.0; 4]; // Only 4 floats — not enough for a 1-byte watermark
        let wm = b"A"; // Needs 8 floats
        assert!(embed(&mut data, wm).is_err());
    }

    #[test]
    fn test_lsb_change_is_imperceptible() {
        // Use values near 1.0 where float32 LSB is exactly 2^-23 ≈ 1.19e-7
        let original: Vec<f32> = (0..64).map(|x| 1.0 + (x as f32 * 0.01)).collect();
        let mut watermarked = original.clone();
        embed(&mut watermarked, b"BIBEK_01").unwrap();
        for (o, w) in original.iter().zip(watermarked.iter()) {
            let diff = (o - w).abs();
            // At magnitude 1.0, the max diff is exactly 2^-23
            assert!(diff < 1.3e-7, "Watermark changed value too much: {} vs {} (diff={})", o, w, diff);
        }
    }
}
