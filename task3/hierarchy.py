# ============================================================
#
#   hierarchy.py - Memory hierarchy controller
#
#   This is the core of the simulation. MemoryHierarchy owns
#   all five levels and enforces the no-skip rule — data has
#   to go through every level in order, no shortcuts.
#
#   Read path: check L1 first, then L2, L3, DRAM, SSD
#   on a miss at every level, load from SSD and bring the
#   block back up through every level on the way to the CPU
#
#   Write path: write-allocate (load into L1 if its not there)
#   then write-back (evictions push dirty blocks down the chain)
#
#   The clock advances by the defined latency on every transfer.
#   Every event gets appended to self.trace so output.py can
#   print it later as the instruction access trace.
# ============================================================

from config       import DEFAULT_CONFIG, LATENCY
from memory_level import MemoryLevel


class MemoryHierarchy:

    def __init__(self, config=None):
        cfg = config if config else dict(DEFAULT_CONFIG)

        # ----------------------------------------------------
        # validate hierarchy sizes before building anything
        # if the sizes are wrong the simulation wont make sense
        # so its better to just error out right here
        # ----------------------------------------------------
        sizes = [cfg["ssd_size"], cfg["dram_size"],
                 cfg["l3_size"],  cfg["l2_size"], cfg["l1_size"]]
        names = ["SSD", "DRAM", "L3", "L2", "L1"]
        for i in range(len(sizes) - 1):
            if sizes[i] <= sizes[i + 1]:
                raise ValueError(
                    f"Hierarchy violated: {names[i]} ({sizes[i]}) must be "
                    f"larger than {names[i+1]} ({sizes[i+1]})"
                )

        self.ssd  = MemoryLevel("SSD",  cfg["ssd_size"])
        self.dram = MemoryLevel("DRAM", cfg["dram_size"])
        self.l3   = MemoryLevel("L3",   cfg["l3_size"])
        self.l2   = MemoryLevel("L2",   cfg["l2_size"])
        self.l1   = MemoryLevel("L1",   cfg["l1_size"])

        # ordered slowest to fastest — output.py uses this list
        self.levels = [self.ssd, self.dram, self.l3, self.l2, self.l1]

        self.clock = 0
        self.trace = []
        self.cfg   = cfg

    # --------------------------------------------------------
    # LOG + TICK
    # _log adds a timestamped line to the trace
    # _tick advances the clock by however many cycles passed
    # keeping these as small helpers makes the read/write
    # methods a lot easier to follow
    # --------------------------------------------------------
    def _log(self, msg):
        self.trace.append(f"[Cycle {self.clock:>5}] {msg}")

    def _tick(self, cycles):
        self.clock += cycles

    # --------------------------------------------------------
    # TRANSFER
    # moves one instruction from src to dst
    # advances the clock by the defined latency
    # if dst is full, the LRU block gets evicted and written
    # back to the next level down (write-back policy)
    # --------------------------------------------------------
    def _transfer(self, src, dst, addr, value, latency_key):
        lat = LATENCY[latency_key]
        self._tick(lat)

        evicted = dst.write(addr, value)

        self._log(
            f"  {src.name} → {dst.name} | addr={addr:#010x} "
            f"val={value:#010x} | latency={lat} cycles"
        )

        if evicted is not None:
            e_addr, e_val = evicted
            self._log(
                f"  [LRU Evict from {dst.name}] addr={e_addr:#010x} "
                f"→ written back to lower level"
            )
            self._writeback_eviction(dst, e_addr, e_val)

        return value

    # --------------------------------------------------------
    # WRITEBACK ON EVICTION
    # when a level evicts a block it has to go somewhere
    # chain is L1→L2→L3→DRAM→SSD
    # SSD is the bottom — nothing below it so we stop there
    # --------------------------------------------------------
    def _writeback_eviction(self, evicted_from, addr, value):
        if evicted_from is self.l1:
            lower, lat = self.l2, LATENCY["l2_to_l1"]
        elif evicted_from is self.l2:
            lower, lat = self.l3, LATENCY["l3_to_l2"]
        elif evicted_from is self.l3:
            lower, lat = self.dram, LATENCY["dram_to_l3"]
        elif evicted_from is self.dram:
            lower, lat = self.ssd, LATENCY["ssd_to_dram"]
        else:
            return  # SSD has nowhere to write back to

        self._tick(lat)
        lower.write(addr, value)
        self._log(
            f"  [Write-back] {evicted_from.name} → {lower.name} | "
            f"addr={addr:#010x} val={value:#010x}"
        )

    # --------------------------------------------------------
    # LOAD PROGRAM
    # pre-fill SSD with the instruction set before simulation
    # SSD is the ground truth — all other levels start empty
    # this doesnt cost clock cycles, its just setup
    # --------------------------------------------------------
    def load_program(self, instructions):
        for addr, val in instructions:
            if addr in self.ssd.data:
                raise ValueError(f"Duplicate address: {addr:#010x}")
            self.ssd.data[addr] = val

        self._log(f"Program loaded: {len(instructions)} instructions into SSD")

    # --------------------------------------------------------
    # READ
    # check each level fastest to slowest
    # first level that has the addr is a hit — load it back
    # up through every level between there and L1, then return
    # if nothing has it, thats a fault (bad address)
    # --------------------------------------------------------
    def read(self, addr):
        self._log(f"READ  addr={addr:#010x}")

        # L1 - fastest, check first
        val, hit = self.l1.read(addr)
        if hit:
            self._tick(LATENCY["l1_to_cpu"])
            self._log(f"  L1 HIT  → val={val:#010x} | total latency=1 cycle")
            return val
        self._log(f"  L1 MISS")

        # L2
        val, hit = self.l2.read(addr)
        if hit:
            self._log(f"  L2 HIT  → val={val:#010x}")
            self._transfer(self.l2, self.l1, addr, val, "l2_to_l1")
            self._tick(LATENCY["l1_to_cpu"])
            return val
        self._log(f"  L2 MISS")

        # L3
        val, hit = self.l3.read(addr)
        if hit:
            self._log(f"  L3 HIT  → val={val:#010x}")
            self._transfer(self.l3, self.l2, addr, val, "l3_to_l2")
            self._transfer(self.l2, self.l1, addr, val, "l2_to_l1")
            self._tick(LATENCY["l1_to_cpu"])
            return val
        self._log(f"  L3 MISS")

        # DRAM
        val, hit = self.dram.read(addr)
        if hit:
            self._log(f"  DRAM HIT → val={val:#010x}")
            self._transfer(self.dram, self.l3, addr, val, "dram_to_l3")
            self._transfer(self.l3,   self.l2, addr, val, "l3_to_l2")
            self._transfer(self.l2,   self.l1, addr, val, "l2_to_l1")
            self._tick(LATENCY["l1_to_cpu"])
            return val
        self._log(f"  DRAM MISS")

        # SSD - slowest, last resort
        val, hit = self.ssd.read(addr)
        if hit:
            self._log(f"  SSD HIT  → val={val:#010x}")
            self._transfer(self.ssd,  self.dram, addr, val, "ssd_to_dram")
            self._transfer(self.dram, self.l3,   addr, val, "dram_to_l3")
            self._transfer(self.l3,   self.l2,   addr, val, "l3_to_l2")
            self._transfer(self.l2,   self.l1,   addr, val, "l2_to_l1")
            self._tick(LATENCY["l1_to_cpu"])
            return val

        # not found anywhere — invalid address
        self._log(f"  FAULT: addr={addr:#010x} not in SSD — invalid access")
        return None

    # --------------------------------------------------------
    # WRITE
    # write-allocate: if the addr isnt in L1 yet, load it first
    # then write the new value to L1
    # also update SSD (ground truth) and any intermediate level
    # that already has this addr so they dont stay stale
    # if L1 evicts something, that block goes back down the chain
    # --------------------------------------------------------
    def write(self, addr, value):
        self._log(f"WRITE addr={addr:#010x} val={value:#010x}")

        # write-allocate: need it in L1 before we can write to it
        if not self.l1.contains(addr):
            self._log(f"  Write-allocate: loading {addr:#010x} into hierarchy")
            self.read(addr)

        evicted = self.l1.write(addr, value)
        self._tick(1)
        self._log(f"  Written to L1: addr={addr:#010x} val={value:#010x}")

        if evicted is not None:
            e_addr, e_val = evicted
            self._log(f"  [LRU Evict from L1] addr={e_addr:#010x} → write-back")
            self._writeback_eviction(self.l1, e_addr, e_val)

        # update SSD as the ground truth
        self.ssd.data[addr] = value

        # update intermediate levels that already have this addr
        for level in [self.l2, self.l3, self.dram]:
            if level.contains(addr):
                level.data[addr] = value
                level.data.move_to_end(addr)
                self._log(f"  Updated {level.name}: addr={addr:#010x}")

        return value
