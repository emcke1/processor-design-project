# ============================================================
#
#   register_file.py - 32-bit register file
#
#   Eight general-purpose registers (t0-t7).
#   Two read ports so we can grab both source operands at once,
#   and one write port for the result.
#   write_enable has to be 1 or nothing gets written,
#   that way the control unit stays in charge of when writes happen.
#
# ============================================================

NUM_REGS  = 8
WORD_MASK = 0xFFFFFFFF   # keep everything clamped to 32 bits


class RegisterFile:

    def __init__(self):
        # just a plain list, index = register number
        self.regs = [0] * NUM_REGS

    # --------------------------------------------------------
    # LOAD
    # pre-load registers before execution starts
    # takes a dict of {reg_index: value}
    # --------------------------------------------------------
    def load(self, values):
        for idx, val in values.items():
            self.regs[idx] = int(val) & WORD_MASK

    # --------------------------------------------------------
    # READ
    # two simultaneous read ports — returns (data_rs, data_rt)
    # --------------------------------------------------------
    def read(self, rs, rt):
        return self.regs[rs] & WORD_MASK, self.regs[rt] & WORD_MASK

    # --------------------------------------------------------
    # WRITE
    # only actually writes if write_enable is True
    # --------------------------------------------------------
    def write(self, rd, data, write_enable):
        if write_enable:
            self.regs[rd] = data & WORD_MASK

    # --------------------------------------------------------
    # DUMP
    # returns a copy of all register values so the output
    # printer doesn't have to poke at .regs directly
    # --------------------------------------------------------
    def dump(self):
        return {i: v for i, v in enumerate(self.regs)}
