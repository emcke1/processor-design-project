# ============================================================
#
#   mux.py - Multiplexer
#
#   Generic N-input mux used by the datapath to route signals.
#   The main one that matters for this task is the 2-input mux
#   in front of ALU input A — it picks between the raw register
#   value and its inverted version based on the invert_a signal.
#
# ============================================================


# --------------------------------------------------------
# MUX
# inputs is just a list, sel picks which one to pass through
# sel=0 -> inputs[0], sel=1 -> inputs[1], etc.
# --------------------------------------------------------
def mux(inputs, sel):
    if sel < 0 or sel >= len(inputs):
        raise IndexError(
            "MUX: selector " + str(sel) + " out of range for "
            + str(len(inputs)) + "-input mux"
        )
    return inputs[sel]


# --------------------------------------------------------
# MUX2
# just a shortcut for the common 2-input case
# sel=0 returns a, sel=1 returns b
# --------------------------------------------------------
def mux2(a, b, sel):
    return mux([a, b], sel)
