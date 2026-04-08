# ============================================================
#
#   memory_level.py - Single memory tier
#
#   One MemoryLevel object represents one tier in the hierarchy.
#   It doesnt know about the levels above or below it.
#   It just handles its own storage, hit/miss counting, and
#   evicting when it gets full.
#
#   LRU is the replacement policy (bonus requirement).
#   i used OrderedDict because it keeps insertion order and
#   has move_to_end() built in, which makes LRU really easy.
#   most recently used goes to the end, least recently used
#   stays at the front and gets evicted first when its full.
# ============================================================

from collections import OrderedDict


class MemoryLevel:

    def __init__(self, name, capacity):
        self.name     = name
        self.capacity = capacity
        self.data     = OrderedDict()   # addr -> 32-bit value, LRU order
        self.hits     = 0
        self.misses   = 0

    # --------------------------------------------------------
    # READ
    # returns (value, True) on hit, (None, False) on miss
    # on a hit we move the entry to the end so its marked as
    # recently used and wont be the next one evicted
    # --------------------------------------------------------
    def read(self, addr):
        if addr in self.data:
            self.hits += 1
            self.data.move_to_end(addr)
            return self.data[addr], True
        self.misses += 1
        return None, False

    # --------------------------------------------------------
    # WRITE
    # if the addr is already here, just update and move to end
    # if we're full, evict the front (LRU) entry first
    # returns the evicted (addr, value) or None if no eviction
    # the caller is responsible for writing the evicted block
    # down to the next lower level
    # --------------------------------------------------------
    def write(self, addr, value):
        if addr in self.data:
            self.data.move_to_end(addr)
            self.data[addr] = value
            return None

        evicted = None
        if len(self.data) >= self.capacity:
            evicted_addr, evicted_val = self.data.popitem(last=False)
            evicted = (evicted_addr, evicted_val)

        self.data[addr] = value
        return evicted

    # --------------------------------------------------------
    # HELPERS
    # small utility methods so other files dont have to poke
    # at .data directly
    # --------------------------------------------------------
    def contains(self, addr):
        return addr in self.data

    def count(self):
        return len(self.data)

    def is_full(self):
        return len(self.data) >= self.capacity
