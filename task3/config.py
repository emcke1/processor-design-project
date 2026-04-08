# ============================================================
#
#   config.py - Sizes and latency constants
#
#   All the numbers that define the hierarchy live here.
#   Having them in one place means if i want to tweak a latency
#   or change a default size, i only have to do it once.
#
#   Sizes are in number of 32-bit instructions (not bytes).
#   The hierarchy rule is SSD > DRAM > L3 > L2 > L1.
#   That rule gets checked at runtime in hierarchy.py.
# ============================================================


# ------------------------------------------------------------
# DEFAULT SIZES
# these are the fallback values when no custom config is passed
# interactive mode lets the user override all of these
# ------------------------------------------------------------
DEFAULT_CONFIG = {
    "ssd_size":  256,
    "dram_size":  64,
    "l3_size":    16,
    "l2_size":     8,
    "l1_size":     4,
}


# ------------------------------------------------------------
# TRANSFER LATENCY (clock cycles)
# student-defined — picked to reflect how much slower each
# level is compared to the one above it
# ssd is the slowest by a lot, l1 to cpu is basically instant
# each key is "src_to_dst" so its obvious which direction
# ------------------------------------------------------------
LATENCY = {
    "ssd_to_dram": 10,
    "dram_to_l3":   5,
    "l3_to_l2":     3,
    "l2_to_l1":     2,
    "l1_to_cpu":    1,
}
