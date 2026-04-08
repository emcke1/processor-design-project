# ============================================================
#   Author: Eden McKenzie
#   Course: CSC 4210/6210 - Computer Architecture
#   Semester: Spring 2026
#   Assignment: Processor Design Semester Project - Task 3
#
#   IoT Use Case: Smart Temperature Sensor Node
#
#   This simulates the memory subsystem of the processor.
#   Instructions have to travel through every level of the
#   hierarchy — no skipping allowed. Its a clock-driven model
#   so you can see exactly how many cycles each transfer costs.
#
#   This is the main entry point. It ties together all the stages:
#
#   Stage 1 - config.py       — sizes and latency constants
#   Stage 2 - memory_level.py — single tier (read/write/LRU)
#   Stage 3 - hierarchy.py    — full controller (read/write/clock)
#   Stage 4 - output.py       — config, trace, stats, final state
#
#   Run this file and pick demo or interactive mode.
# ============================================================

from hierarchy import MemoryHierarchy
from output    import print_config, print_trace, print_cache_stats, print_final_state


# ------------------------------------------------------------
# HELPER - safe integer input
# keeps asking until the user gives something valid
# handles decimal and 0x hex so the user has options
# ------------------------------------------------------------
def get_int(prompt, min_val=None, max_val=None):
    while True:
        raw = input(prompt).strip()
        try:
            val = int(raw, 0)   # base 0 handles both 0x... and plain decimal
        except ValueError:
            print("  Error: enter a valid integer (decimal or 0x hex).")
            continue
        if min_val is not None and val < min_val:
            print(f"  Error: must be >= {min_val}")
            continue
        if max_val is not None and val > max_val:
            print(f"  Error: must be <= {max_val}")
            continue
        return val


# ------------------------------------------------------------
# DEMO
# runs a scripted simulation to show the full pipeline working
# five sequences that each demonstrate something different:
#
#   seq 1 - cold reads, everything misses all the way to SSD
#   seq 2 - same addresses again, should all hit L1 now
#   seq 3 - new addresses to overflow L1 and force evictions
#   seq 4 - write one instruction back (write-back + allocate)
#   seq 5 - re-read an evicted address, should find it in L2/L3
# ------------------------------------------------------------
def run_demo():
    print("\n" + "=" * 60)
    print("   DEMO — Memory Hierarchy Simulation")
    print("   IoT Use Case: Smart Temperature Sensor Node")
    print("=" * 60 + "\n")

    h = MemoryHierarchy()
    print_config(h)

    # each entry is (address, 32-bit instruction value)
    # addresses go up by 4 because each instruction is 4 bytes
    program = [
        (0x00000000, 0xA0010001),
        (0x00000004, 0xA0020002),
        (0x00000008, 0xB0010000),
        (0x0000000C, 0xC0010018),
        (0x00000010, 0xD0030000),
        (0x00000014, 0xE0010002),
        (0x00000018, 0xF0010001),
        (0x0000001C, 0xA0000000),
        (0x00000020, 0x00000000),
        (0x00000024, 0xFF000000),
    ]

    h.load_program(program)
    print(f"  Loaded {len(program)} instructions into SSD.\n")

    # --------------------------------------------------------
    # SEQ 1: cold reads — all miss all the way down to SSD
    # --------------------------------------------------------
    print("--- Sequence 1: Cold reads (all cold misses) ---\n")
    addrs_to_fetch = [0x00000000, 0x00000004, 0x00000008, 0x0000000C]
    for addr in addrs_to_fetch:
        result = h.read(addr)
        print(f"  CPU got: {result:#010x}\n")

    # --------------------------------------------------------
    # SEQ 2: re-fetch same addresses — should hit L1 every time
    # --------------------------------------------------------
    print("--- Sequence 2: Re-fetch same addresses (L1 hits) ---\n")
    for addr in addrs_to_fetch:
        result = h.read(addr)
        print(f"  CPU got: {result:#010x}\n")

    # --------------------------------------------------------
    # SEQ 3: new addresses — L1 is size 4 so these will push
    # out the old ones and trigger LRU evictions
    # --------------------------------------------------------
    print("--- Sequence 3: Overflow L1 — force LRU evictions ---\n")
    extra_addrs = [0x00000010, 0x00000014, 0x00000018, 0x0000001C]
    for addr in extra_addrs:
        result = h.read(addr)
        print(f"  CPU got: {result:#010x}\n")

    # --------------------------------------------------------
    # SEQ 4: write — write-allocate loads it into L1 first,
    # then the new value gets written back
    # --------------------------------------------------------
    print("--- Sequence 4: Write operation (write-back) ---\n")
    h.write(0x00000010, 0x12345678)
    print()

    # --------------------------------------------------------
    # SEQ 5: re-read an address that was evicted from L1 earlier
    # it should still be in L2 or L3, not have to go to SSD
    # --------------------------------------------------------
    print("--- Sequence 5: Re-read evicted address (L2/L3 hit expected) ---\n")
    result = h.read(0x00000000)
    print(f"  CPU got: {result:#010x}\n")

    print_trace(h)
    print_cache_stats(h)
    print_final_state(h)


# ------------------------------------------------------------
# INTERACTIVE MODE
# user sets up the hierarchy themselves and issues commands
# one at a time — good for trying specific scenarios
# ------------------------------------------------------------
def run_interactive():
    print("\n" + "=" * 60)
    print("   INTERACTIVE MODE — Memory Hierarchy Simulation")
    print("=" * 60 + "\n")

    print("Configure hierarchy sizes (number of 32-bit instructions).")
    print("Constraint: SSD > DRAM > L3 > L2 > L1\n")

    # keep asking until they give a valid configuration
    while True:
        try:
            cfg = {
                "ssd_size":  get_int("  SSD  size: ", min_val=1),
                "dram_size": get_int("  DRAM size: ", min_val=1),
                "l3_size":   get_int("  L3   size: ", min_val=1),
                "l2_size":   get_int("  L2   size: ", min_val=1),
                "l1_size":   get_int("  L1   size: ", min_val=1),
            }
            h = MemoryHierarchy(cfg)
            break
        except ValueError as e:
            print(f"\n  Config error: {e}\n  Try again.\n")

    print_config(h)

    print("Load instructions into SSD.")
    num = get_int("  How many instructions? ", min_val=1, max_val=cfg["ssd_size"])
    print("  Enter each as: address value  (hex or decimal, e.g. 0x0 0xDEADBEEF)")
    instructions = []
    for i in range(num):
        while True:
            raw = input(f"    Instruction {i + 1}: ").strip().split()
            if len(raw) != 2:
                print("    Need exactly two values: address value")
                continue
            try:
                addr = int(raw[0], 0)
                val  = int(raw[1], 0) & 0xFFFFFFFF   # clamp to 32 bits
                instructions.append((addr, val))
                break
            except ValueError:
                print("    Invalid input. Try again.")

    h.load_program(instructions)
    print(f"\n  {num} instructions loaded into SSD.\n")

    print("Commands:  read <addr>   write <addr> <value>   stats   state   trace   quit\n")
    while True:
        cmd = input("  > ").strip().split()
        if not cmd:
            continue

        op = cmd[0].lower()

        if op in ("quit", "exit", "q"):
            break

        elif op == "read" and len(cmd) == 2:
            try:
                addr = int(cmd[1], 0)
            except ValueError:
                print("  Invalid address.")
                continue
            result = h.read(addr)
            print(f"  → {result:#010x}\n" if result is not None else "  → FAULT\n")

        elif op == "write" and len(cmd) == 3:
            try:
                addr = int(cmd[1], 0)
                val  = int(cmd[2], 0) & 0xFFFFFFFF
            except ValueError:
                print("  Invalid address or value.")
                continue
            h.write(addr, val)
            print(f"  → Written {val:#010x} to {addr:#010x}\n")

        elif op == "stats":
            print_cache_stats(h)

        elif op == "state":
            print_final_state(h)

        elif op == "trace":
            print_trace(h)

        else:
            print("  Unknown command. Try: read <addr> | write <addr> <val> | stats | state | trace | quit")

    print("\n--- Session complete ---\n")
    print_trace(h)
    print_cache_stats(h)
    print_final_state(h)


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("\n  Task 3 — Memory Hierarchy Simulation")
    print("  1) Run demo")
    print("  2) Interactive mode")
    choice = input("\n  Choose (1 or 2): ").strip()

    if choice == "1":
        run_demo()
    elif choice == "2":
        run_interactive()
    else:
        print("  Invalid choice. Running demo by default.")
        run_demo()
