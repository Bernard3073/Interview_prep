"""
Week 8 — Fixed-size ring buffer for sensor messages.

PROBLEM
-------
Real-time perception nodes keep a bounded history of recent messages without
unbounded memory growth or per-push allocation. Implement a circular buffer with
O(1) push and indexed access to the most-recent-N items.

This mirrors the LeetCode "Design Circular Queue" but in a robotics framing.

Run:  python w8_ring_buffer.py
"""


class RingBuffer:
    def __init__(self, capacity):
        self.cap = capacity
        self.buf = [None] * capacity
        self.head = 0          # next write position
        self.size = 0

    def push(self, item):
        self.buf[self.head] = item
        self.head = (self.head + 1) % self.cap
        self.size = min(self.size + 1, self.cap)

    def latest(self):
        if self.size == 0:
            return None
        return self.buf[(self.head - 1) % self.cap]

    def to_list(self):
        """Oldest -> newest."""
        if self.size < self.cap:
            return self.buf[:self.size]
        return self.buf[self.head:] + self.buf[:self.head]

    def __len__(self):
        return self.size


if __name__ == "__main__":
    rb = RingBuffer(3)
    for i in range(5):
        rb.push(("msg", i))
    print("contents (old->new):", rb.to_list())
    print("latest:", rb.latest())
    assert len(rb) == 3
    assert rb.latest() == ("msg", 4)
    assert rb.to_list() == [("msg", 2), ("msg", 3), ("msg", 4)]
    print("Ring buffer OK")
