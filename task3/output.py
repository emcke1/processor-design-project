# ============================================================
#
#   output.py - Display functions
#
#   All the printing lives here so the main file and the
#   hierarchy dont have to deal with formatting at all.
#   Same idea as utils.py in task2 — shared stuff in one spot.
#
#   Four things to print:
#     print_config     - sizes and latency table before sim runs
#     print_trace      - full clock-tagged event log
#     print_cache_stats - hits, misses, hit rate per level
#     print_final_state - whats in each level at the end
# ============================================================

from config import LATENCY


# ------------------------------------------------------------
# CONFIG
# shows the hierarchy setup before any simulation runs
# useful so the user knows what theyre looking at
# also shows the latency table so the trace cycle counts
# make sense when they read it later
# ------------------------------------------------------------
def print_config(hierarchy):
    print("=" * 60)
    print("   MEMORY HIERARCHY CONFIGURATION")
    print("=" * 60)
    print(f"  {'Level':<10} {'Capacity (instrs)':>20}  {'Bytes':>12}")
    print(f"  {'-'*10} {'-'*20}  {'-'*12}")
    for level in hierarchy.levels:
        bytes_size = level.capacity * 4     # 4 bytes per 32-bit instruction
        print(f"  {level.name:<10} {level.capacity:>20}  {bytes_size:>10} B")
    print()
    print("  Transfer Latencies (clock cycles):")
    for key, val in LATENCY.items():
        src, dst = key.split("_to_")
        print(f"    {src.upper():>6} → {dst.upper():<6}: {val} cycles")
    print("=" * 60)
    print()


# ------------------------------------------------------------
# TRACE
# every event that happened during the simulation with the
# cycle number it happened at
# shows hits, misses, every transfer, every eviction, every
# write-back — basically the full story of what went on
# ------------------------------------------------------------
def print_trace(hierarchy):
    print("=" * 60)
    print("   INSTRUCTION ACCESS TRACE")
    print("=" * 60)
    for line in hierarchy.trace:
        print(" ", line)
    print("=" * 60)
    print()


# ------------------------------------------------------------
# CACHE STATS
# hits and misses per level plus the hit rate percentage
# also prints total clock cycles so you can see what the
# transfers actually cost over the whole simulation
# ------------------------------------------------------------
def print_cache_stats(hierarchy):
    print("=" * 60)
    print("   CACHE HIT / MISS STATISTICS")
    print("=" * 60)
    print(f"  {'Level':<8} {'Hits':>8} {'Misses':>8} {'Total':>8} {'Hit Rate':>10}")
    print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")
    for level in [hierarchy.l1, hierarchy.l2, hierarchy.l3,
                  hierarchy.dram, hierarchy.ssd]:
        total = level.hits + level.misses
        rate  = f"{(level.hits / total * 100):.1f}%" if total > 0 else "N/A"
        print(f"  {level.name:<8} {level.hits:>8} {level.misses:>8} "
              f"{total:>8} {rate:>10}")
    print(f"\n  Total clock cycles elapsed: {hierarchy.clock}")
    print("=" * 60)
    print()


# ------------------------------------------------------------
# FINAL STATE
# dumps everything thats currently in each level
# printed L1 first down to SSD so the "hot" data is at the top
# useful for verifying that write-backs propagated correctly
# and that the right stuff ended up in the right places
# ------------------------------------------------------------
def print_final_state(hierarchy):
    print("=" * 60)
    print("   FINAL STATE OF EACH MEMORY LEVEL")
    print("=" * 60)
    for level in reversed(hierarchy.levels):    # L1 first, SSD last
        occupied = level.count()
        print(f"\n  [ {level.name} ]  {occupied}/{level.capacity} slots used")
        if occupied == 0:
            print("    (empty)")
        else:
            for addr, val in level.data.items():
                print(f"    addr={addr:#010x}  val={val:#010x}")
    print()
    print("=" * 60)
    print()
