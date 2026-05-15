"""
5G Channel Simulator.
Injects three categories of attack for testing detection rates:
  - replay: re-sends a previously captured packet
  - tamper: randomly flips bytes with configurable probability
  - impersonate: replaces device_id (used by attack_test.py at a higher level)
"""
import random


class ChannelSimulator:
    """Simulates a 5G transmission channel with configurable attack injection."""

    def __init__(
        self,
        tamper_prob: float = 0.0,
        replay: bool = False,
        drop_prob: float = 0.0,
        seed: int = None,
    ):
        """
        Args:
            tamper_prob: Probability [0.0, 1.0] of flipping a random byte in each packet.
            replay:      If True, resend the previously captured packet instead of the new one.
            drop_prob:   Probability [0.0, 1.0] of silently dropping a packet (returns None).
            seed:        Optional random seed for reproducible experiments.
        """
        self.tamper_prob = tamper_prob
        self.replay = replay
        self.drop_prob = drop_prob
        self._last_packet: bytes | None = None
        self._rng = random.Random(seed)
        self.stats = {"sent": 0, "tampered": 0, "replayed": 0, "dropped": 0}

    def transmit(self, packet: bytes) -> bytes | None:
        """Simulate transmitting a packet through the (possibly hostile) channel.

        Returns the (possibly modified) packet, or None if dropped.
        """
        self.stats["sent"] += 1

        # Replay attack: return old packet, don't save the new one
        if self.replay and self._last_packet is not None:
            self.stats["replayed"] += 1
            return self._last_packet

        self._last_packet = packet

        # Drop
        if self.drop_prob > 0 and self._rng.random() < self.drop_prob:
            self.stats["dropped"] += 1
            return None

        # Tamper: flip a random byte
        if self.tamper_prob > 0 and self._rng.random() < self.tamper_prob:
            p = bytearray(packet)
            idx = self._rng.randint(0, len(p) - 1)
            p[idx] ^= 0xFF
            self.stats["tampered"] += 1
            return bytes(p)

        return packet

    def reset(self):
        """Reset state between test scenarios."""
        self._last_packet = None
        self.stats = {"sent": 0, "tampered": 0, "replayed": 0, "dropped": 0}
