//! Criterion benchmarks for the SecureMark5G cryptographic pipeline.
//!
//! Run with:
//!   cargo bench
//!
//! HTML reports generated in target/criterion/

use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use securemark5g::{
    auth::{generate_token, current_timestamp},
    crypto::{encrypt, decrypt},
    watermark::{embed, extract},
};

// ─── Auth benchmarks ─────────────────────────────────────────────────────────

fn bench_token_generation(c: &mut Criterion) {
    let device_id  = "IOT_DEVICE_001";
    let secret_key = b"benchmark_secret_key_32_bytes__!";
    let payload    = vec![0u8; 256];
    let ts         = current_timestamp();

    c.bench_function("BLAKE3 token generation", |b| {
        b.iter(|| {
            generate_token(
                black_box(device_id),
                black_box(secret_key),
                black_box(&payload),
                black_box(ts),
            )
        })
    });
}

// ─── Crypto benchmarks ───────────────────────────────────────────────────────

fn bench_chacha20_encrypt(c: &mut Criterion) {
    let key     = [0x42u8; 32];
    let payload = vec![0u8; 256 + 32 + 8]; // sensor + token + timestamp

    c.bench_function("ChaCha20-Poly1305 encrypt (296B)", |b| {
        b.iter(|| encrypt(black_box(&key), black_box(&payload)).unwrap())
    });
}

fn bench_chacha20_decrypt(c: &mut Criterion) {
    let key       = [0x42u8; 32];
    let payload   = vec![0u8; 296];
    let encrypted = encrypt(&key, &payload).unwrap();

    c.bench_function("ChaCha20-Poly1305 decrypt (296B)", |b| {
        b.iter(|| decrypt(black_box(&key), black_box(&encrypted)).unwrap())
    });
}

fn bench_encrypt_varying_sizes(c: &mut Criterion) {
    let key = [0x42u8; 32];
    let mut group = c.benchmark_group("ChaCha20 encrypt by payload size");
    for size in [64, 256, 512, 1024, 4096].iter() {
        let payload = vec![0u8; *size];
        group.bench_with_input(BenchmarkId::from_parameter(size), size, |b, _| {
            b.iter(|| encrypt(black_box(&key), black_box(&payload)).unwrap())
        });
    }
    group.finish();
}

// ─── Watermark benchmarks ────────────────────────────────────────────────────

fn bench_watermark_embed(c: &mut Criterion) {
    let wm = b"DEV_001_";  // 8 bytes = 64 floats needed
    let original: Vec<f32> = (0..256).map(|x| x as f32 * 0.1).collect();

    c.bench_function("LSB watermark embed (256 floats, 8B wm)", |b| {
        b.iter(|| {
            let mut data = original.clone();
            embed(black_box(&mut data), black_box(wm)).unwrap()
        })
    });
}

fn bench_watermark_extract(c: &mut Criterion) {
    let wm = b"DEV_001_";
    let mut data: Vec<f32> = (0..256).map(|x| x as f32 * 0.1).collect();
    embed(&mut data, wm).unwrap();

    c.bench_function("LSB watermark extract (256 floats, 8B wm)", |b| {
        b.iter(|| extract(black_box(&data), black_box(wm.len())))
    });
}

// ─── Full pipeline benchmark ─────────────────────────────────────────────────

fn bench_full_pipeline(c: &mut Criterion) {
    let device_id  = "IOT_DEVICE_001";
    let secret_key = b"benchmark_secret_key_32_bytes__!";
    let enc_key    = [0x42u8; 32];
    let payload    = vec![0u8; 256];
    let ts         = current_timestamp();

    c.bench_function("Full pipeline: token + encrypt (256B payload)", |b| {
        b.iter(|| {
            let token   = generate_token(black_box(device_id), black_box(secret_key), black_box(&payload), black_box(ts));
            let mut pkt = payload.clone();
            pkt.extend_from_slice(&token.0);
            pkt.extend_from_slice(&ts.to_le_bytes());
            encrypt(black_box(&enc_key), black_box(&pkt)).unwrap()
        })
    });
}

criterion_group!(
    benches,
    bench_token_generation,
    bench_chacha20_encrypt,
    bench_chacha20_decrypt,
    bench_encrypt_varying_sizes,
    bench_watermark_embed,
    bench_watermark_extract,
    bench_full_pipeline,
);
criterion_main!(benches);
