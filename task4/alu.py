# ============================================================
#
#   alu.py - 32-bit ALU
#
#   Supports AND and OR.
#   NOT is not a separate instruction — instead the control unit
#   can set invert_a=True to flip the first operand before the
#   operation happens. That's how we get ~C & D without adding
#   a whole new instruction type.
#
# ============================================================

WORD_MASK = 0xFFFFFFFF

# operation codes — these match the function field encoding in control_unit.py
OP_AND = 0
OP_OR  = 1


class ALU:

    # --------------------------------------------------------
    # EXECUTE
    # a, b are the two 32-bit operands
    # alu_op picks AND or OR
    # invert_a flips a before the operation (handles NOT)
    # --------------------------------------------------------
    def execute(self, a, b, alu_op, invert_a):
        if invert_a:
            a = (~a) & WORD_MASK

        if alu_op == OP_AND:
            return (a & b) & WORD_MASK

        if alu_op == OP_OR:
            return (a | b) & WORD_MASK

        # shouldnt get here if the control unit is doing its job
        raise ValueError("ALU: unknown operation code " + str(alu_op))
