# ============================================================
#
#   control_unit.py - Instruction decoder + control signal generator
#
#   Takes a 32-bit instruction word and figures out what everything
#   means — which registers to read/write, which ALU op to run,
#   and whether to invert the first operand.
#
#   Instruction format (R-type, 32 bits):
#
#     [31:26]  opcode  (6 bits)  — always 000000 for R-type
#     [25:21]  rs      (5 bits)  — source register 1
#     [20:16]  rt      (5 bits)  — source register 2
#     [15:11]  rd      (5 bits)  — destination register
#     [10:8]   unused  (3 bits)
#     [7:6]    func    (2 bits)  — 00=AND, 01=OR, 10=AND-not
#     [5]      inv_a   (1 bit)   — 1 = invert rs before ALU
#     [4:0]    unused  (5 bits)
#
#   The inversion flag is in the function field, not the opcode,
#   so AND and AND-not are the same instruction type — the control
#   unit just sets invert_a differently for each.
#
# ============================================================

from alu import OP_AND, OP_OR

OPCODE_RTYPE = 0b000000

# function field values
FUNC_AND     = 0b00   # standard AND
FUNC_OR      = 0b01   # standard OR
FUNC_AND_NOT = 0b10   # AND with first operand inverted


class ControlSignals:
    """Bundles all the signals the datapath needs for one instruction."""

    def __init__(self, alu_op, invert_a, reg_write):
        self.alu_op    = alu_op
        self.invert_a  = invert_a
        self.reg_write = reg_write


class ControlUnit:

    # --------------------------------------------------------
    # DECODE
    # pulls all the fields out of the instruction word and
    # decides what control signals to assert
    # returns (rs, rt, rd, ControlSignals)
    # --------------------------------------------------------
    def decode(self, instruction):
        opcode = (instruction >> 26) & 0x3F
        rs     = (instruction >> 21) & 0x1F
        rt     = (instruction >> 16) & 0x1F
        rd     = (instruction >> 11) & 0x1F
        func   = (instruction >>  6) & 0x03   # bits [7:6]
        inv_a  = bool((instruction >> 5) & 0x01)

        if opcode != OPCODE_RTYPE:
            raise ValueError("Control unit: unsupported opcode " + bin(opcode))

        if func == FUNC_AND or func == FUNC_AND_NOT:
            alu_op = OP_AND
        elif func == FUNC_OR:
            alu_op = OP_OR
        else:
            raise ValueError("Control unit: unsupported function field " + bin(func))

        signals = ControlSignals(
            alu_op    = alu_op,
            invert_a  = inv_a,
            reg_write = True,    # all three instructions write back a result
        )

        return rs, rt, rd, signals
